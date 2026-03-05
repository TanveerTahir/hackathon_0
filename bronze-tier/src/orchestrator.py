#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital FTE Orchestrator - Coordinates watchers and task processing.

This is the main entry point for running the AI Employee system.
It coordinates watchers (perception), task processors (reasoning),
and manages the overall workflow.

Usage:
    python orchestrator.py /path/to/vault [options]

    Options:
        --watchers: Comma-separated list of watchers to run (filesystem,gmail)
        --interval: Check interval in seconds (default: 60)
        --process: Process tasks after each check cycle
        --daemon: Run continuously in background
"""

import argparse
import signal
import sys
import time
import io
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Enable UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates:
    - Watchers (perception layer)
    - Task processors (reasoning layer)
    - Dashboard updates
    - Logging
    """

    def __init__(
        self,
        vault_path: str,
        watchers: List[str] = None,
        check_interval: int = 60,
        auto_process: bool = True
    ):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            watchers: List of watcher names to enable
            check_interval: Seconds between check cycles
            auto_process: Whether to auto-process tasks after each cycle
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.auto_process = auto_process
        self.running = False
        self.watchers_to_run = watchers or ['filesystem']
        
        # Ensure vault exists
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")

        # Import watchers dynamically
        self.watchers = []
        self._load_watchers()

        # Create task processor
        from processors import TaskProcessor
        self.processor = TaskProcessor(str(vault_path))

        # Setup logging
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_watchers(self):
        """Load and initialize requested watchers."""
        from watchers import FilesystemWatcher

        for watcher_name in self.watchers_to_run:
            try:
                if watcher_name == 'filesystem':
                    watcher = FilesystemWatcher(str(self.vault_path))
                    self.watchers.append(watcher)
                    print(f"✓ Loaded FilesystemWatcher")

                elif watcher_name == 'gmail':
                    try:
                        from watchers import GmailWatcher
                        watcher = GmailWatcher(str(self.vault_path))
                        self.watchers.append(watcher)
                        print(f"✓ Loaded GmailWatcher")
                    except ImportError as e:
                        print(f"⚠ GmailWatcher not available: {e}")

            except Exception as e:
                print(f"✗ Failed to load {watcher_name}: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down orchestrator...")
        self.running = False

    def _log(self, message: str, level: str = "info"):
        """Log a message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
        
        log_file = self.logs_dir / f"orchestrator_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Also print to console
        prefix = {
            'info': 'ℹ',
            'warning': '⚠',
            'error': '✗',
            'success': '✓'
        }.get(level, '•')
        
        print(f"{prefix} {message}")

    def run_cycle(self) -> dict:
        """
        Run one complete check cycle.
        
        Returns:
            Dictionary with cycle statistics
        """
        stats = {
            'timestamp': datetime.now().isoformat(),
            'watchers_run': 0,
            'tasks_created': 0,
            'tasks_processed': 0,
            'errors': 0
        }
        
        self._log("Starting check cycle...", "info")
        
        # Run each watcher once (single check, not continuous)
        for watcher in self.watchers:
            try:
                items = watcher.check_for_updates()
                for item in items:
                    try:
                        watcher.create_action_file(item)
                        stats['tasks_created'] += 1
                    except Exception as e:
                        self._log(f"Error creating action file: {e}", "error")
                        stats['errors'] += 1
                
                stats['watchers_run'] += 1
                
            except Exception as e:
                self._log(f"Watcher {watcher.__class__.__name__} error: {e}", "error")
                stats['errors'] += 1
        
        # Process tasks if auto-process is enabled
        if self.auto_process and stats['tasks_created'] > 0:
            try:
                process_stats = self.processor.process_all_tasks()
                stats['tasks_processed'] = process_stats['processed']
                stats['errors'] += process_stats['errors']
            except Exception as e:
                self._log(f"Task processor error: {e}", "error")
                stats['errors'] += 1
        
        # Update dashboard
        try:
            self.processor.update_dashboard()
        except Exception as e:
            self._log(f"Dashboard update error: {e}", "error")
            stats['errors'] += 1
        
        self._log(
            f"Cycle complete: {stats['tasks_created']} tasks created, "
            f"{stats['tasks_processed']} processed",
            "success"
        )
        
        return stats

    def run(self, daemon: bool = False):
        """
        Run the orchestrator.
        
        Args:
            daemon: If True, run continuously. If False, run one cycle.
        """
        self.running = True
        
        self._log("=" * 50, "info")
        self._log("Digital FTE Orchestrator Starting", "success")
        self._log(f"Vault: {self.vault_path}", "info")
        self._log(f"Watchers: {', '.join(self.watchers_to_run)}", "info")
        self._log(f"Check interval: {self.check_interval}s", "info")
        self._log("=" * 50, "info")
        
        if daemon:
            # Continuous mode
            while self.running:
                try:
                    self.run_cycle()
                    time.sleep(self.check_interval)
                except Exception as e:
                    self._log(f"Cycle error: {e}", "error")
                    time.sleep(self.check_interval)
        else:
            # Single cycle mode
            self.run_cycle()
        
        self._log("Orchestrator stopped", "info")

    def status(self) -> dict:
        """
        Get current system status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'vault': str(self.vault_path),
            'watchers': [w.__class__.__name__ for w in self.watchers],
            'check_interval': self.check_interval,
            'auto_process': self.auto_process,
            'running': self.running,
            'folders': {
                'needs_action': len(list((self.vault_path / 'Needs_Action').glob('*.md'))),
                'plans': len(list((self.vault_path / 'Plans').glob('*.md'))),
                'pending_approval': len(list((self.vault_path / 'Pending_Approval').glob('*.md'))),
                'done': len(list((self.vault_path / 'Done').glob('*.md')))
            }
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Digital FTE Orchestrator - AI Employee System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run one check cycle with filesystem watcher
  python orchestrator.py /path/to/vault
  
  # Run continuously with Gmail and filesystem watchers
  python orchestrator.py /path/to/vault --watchers filesystem,gmail --daemon
  
  # Run with custom check interval
  python orchestrator.py /path/to/vault --interval 30
  
  # Check status only
  python orchestrator.py /path/to/vault --status
        """
    )
    
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--watchers', '-w',
        default='filesystem',
        help='Comma-separated list of watchers (filesystem,gmail)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='Run continuously in daemon mode'
    )
    parser.add_argument(
        '--no-process',
        action='store_true',
        help='Disable auto-processing of tasks'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show system status and exit'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)
    
    # Create orchestrator
    try:
        orchestrator = Orchestrator(
            str(vault_path),
            watchers=args.watchers.split(','),
            check_interval=args.interval,
            auto_process=not args.no_process
        )
    except Exception as e:
        print(f"Error creating orchestrator: {e}")
        sys.exit(1)
    
    # Show status or run
    if args.status:
        import json
        status = orchestrator.status()
        print(json.dumps(status, indent=2))
    else:
        orchestrator.run(daemon=args.daemon)


if __name__ == "__main__":
    main()
