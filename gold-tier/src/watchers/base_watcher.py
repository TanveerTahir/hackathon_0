#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all watcher implementations.

Watchers are the "senses" of the AI Employee system, monitoring various
data sources and creating actionable markdown files for Claude to process.

Gold Tier: Extended with error recovery and comprehensive logging.
"""

import logging
import time
import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing_extensions import override


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.

    Watchers run continuously in the background, monitoring specific
    data sources and creating task files when new items are detected.
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.processed_ids: set = set()
        self.running = False
        self.error_count = 0
        self.max_errors = 3
        self.last_error_time: Optional[datetime] = None

        # Define folder paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_dir = self.vault_path / 'Logs'
        self.integrations_dir = self.vault_path / 'Integrations'

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.integrations_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for this watcher."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Create handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check the data source for new items.

        Returns:
            List of new items to process, each as a dictionary
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file in Needs_Action folder.

        Args:
            item: The item to create an action file for

        Returns:
            Path to the created file
        """
        pass

    def _generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a standardized filename.

        Args:
            prefix: File prefix (e.g., 'EMAIL', 'WHATSAPP')
            unique_id: Unique identifier for the item

        Returns:
            Filename string
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{prefix}_{unique_id}_{date_str}.md"

    def _create_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Create YAML frontmatter for action files.

        Args:
            item_type: Type of item (email, whatsapp, file_drop, etc.)
            **kwargs: Additional frontmatter fields

        Returns:
            YAML frontmatter string
        """
        lines = [
            "---",
            f"type: {item_type}",
            f"created: {datetime.now().isoformat()}",
            "status: pending",
            "priority: normal",
        ]

        for key, value in kwargs.items():
            lines.append(f"{key}: {value}")

        lines.append("---")
        return "\n".join(lines)

    def log_activity(self, message: str, level: str = "info"):
        """
        Log activity to the Logs folder.

        Args:
            message: Message to log
            level: Log level (info, warning, error)
        """
        log_file = self.logs_dir / f"watcher_{datetime.now().strftime('%Y-%m-%d')}.log"

        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def log_audit(self, action: str, details: Dict[str, Any]):
        """
        Create comprehensive audit log entry.

        Args:
            action: Action performed
            details: Details dictionary
        """
        audit_file = self.logs_dir / f"audit_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.__class__.__name__,
            'action': action,
            'details': details
        }

        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')

    def handle_error(self, error: Exception, context: str = ""):
        """
        Handle errors with graceful degradation.

        Args:
            error: Exception that occurred
            context: Additional context
        """
        self.error_count += 1
        self.last_error_time = datetime.now()

        error_msg = f"{context}: {str(error)}"
        self.logger.error(error_msg)
        self.log_activity(error_msg, "error")
        self.log_audit('error', {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'error_count': self.error_count
        })

        # Reset error count after 5 minutes without errors
        if self.error_count >= self.max_errors:
            self.logger.warning("Max errors reached, implementing graceful degradation")
            self.log_activity("Graceful degradation activated", "warning")

    def should_continue(self) -> bool:
        """
        Check if watcher should continue running.

        Returns:
            True if should continue, False if should stop due to errors
        """
        if self.error_count >= self.max_errors:
            # Check if 5 minutes have passed since last error
            if self.last_error_time:
                elapsed = (datetime.now() - self.last_error_time).total_seconds()
                if elapsed < 300:  # 5 minutes
                    return False
                else:
                    # Reset after cooldown
                    self.error_count = 0
                    self.logger.info("Error count reset after cooldown")
        return True

    def run(self):
        """
        Main run loop for the watcher.

        Continuously checks for updates and creates action files.
        Implements error recovery and graceful degradation.
        """
        self.running = True
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.log_activity(f"Watcher started: {self.__class__.__name__}")
        self.log_audit('started', {'watcher': self.__class__.__name__})

        try:
            while self.running:
                if not self.should_continue():
                    self.logger.warning("Pausing due to errors, will retry soon")
                    time.sleep(60)  # Wait 1 minute before retry
                    continue

                try:
                    items = self.check_for_updates()
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                            self.logger.info(f"Created action file: {filepath.name}")
                            self.log_activity(f"Created action file: {filepath.name}")
                            self.log_audit('action_file_created', {
                                'filepath': str(filepath),
                                'item_id': item.get('id', 'unknown')
                            })
                        except Exception as e:
                            self.handle_error(e, f"Error creating action file for {item.get('id', 'unknown')}")

                except Exception as e:
                    self.handle_error(e, "Error in check loop")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("Watcher stopped by user")
            self.log_activity("Watcher stopped by user")
        finally:
            self.running = False
            self.log_audit('stopped', {'watcher': self.__class__.__name__})

    def stop(self):
        """Stop the watcher."""
        self.running = False
        self.logger.info(f"Stopping {self.__class__.__name__}")
        self.log_activity(f"Watcher stopped: {self.__class__.__name__}")
        self.log_audit('stopped', {'watcher': self.__class__.__name__})
