"""
Base Skill Module - Foundation for all AI Employee Skills

This module provides the abstract base class for all skills in the system.
All skills must inherit from BaseSkill and implement the required methods.

Silver Tier Implementation - Personal AI Employee Hackathon 0
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json
import logging


class SkillError(Exception):
    """Base exception for skill errors"""
    pass


class SkillConfigurationError(SkillError):
    """Raised when skill configuration is invalid"""
    pass


class SkillExecutionError(SkillError):
    """Raised when skill execution fails"""
    pass


class BaseSkill(ABC):
    """
    Abstract base class for all AI Employee skills.
    
    Attributes:
        name (str): Unique identifier for the skill
        description (str): Human-readable description
        version (str): Skill version (semver format)
        vault_path (Path): Path to the Obsidian vault
        config (Dict): Skill-specific configuration
        logger (logging.Logger): Logger instance
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        vault_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a base skill.
        
        Args:
            name: Unique skill identifier
            description: Human-readable description
            version: Skill version (semver format)
            vault_path: Path to Obsidian vault (optional)
            config: Skill-specific configuration (optional)
        """
        self.name = name
        self.description = description
        self.version = version
        self.vault_path = Path(vault_path) if vault_path else None
        self.config = config or {}
        self.created_at = datetime.now().isoformat()
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Validate configuration
        self._validate_config()
        
        self.logger.info(f"Skill '{self.name}' v{self.version} initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the skill"""
        logger = logging.getLogger(f"skills.{self.name}")
        logger.setLevel(logging.INFO)
        
        # Create console handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _validate_config(self) -> None:
        """Validate skill configuration"""
        if self.vault_path and not self.vault_path.exists():
            self.logger.warning(f"Vault path does not exist: {self.vault_path}")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the skill's primary function.
        
        Args:
            **kwargs: Skill-specific arguments
            
        Returns:
            Dict containing execution results
            
        Raises:
            SkillExecutionError: If execution fails
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the input/output schema for this skill.
        
        Returns:
            Dict describing input parameters and output structure
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "input_schema": self._get_input_schema(),
            "output_schema": self._get_output_schema()
        }
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """Get input parameter schema (override in subclasses)"""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        """Get output schema (override in subclasses)"""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "error": {"type": "string"}
            }
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "vault_path": str(self.vault_path) if self.vault_path else None,
            "config_keys": list(self.config.keys())
        }
    
    def _write_log(self, log_entry: Dict[str, Any]) -> None:
        """Write a log entry to the vault logs"""
        if not self.vault_path:
            return
        
        logs_dir = self.vault_path / "Logs"
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        
        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                logs = []
        
        # Add new log entry
        log_entry["timestamp"] = datetime.now().isoformat()
        log_entry["skill"] = self.name
        logs.append(log_entry)
        
        # Write back
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}')"
