#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors a designated "drop folder" for new files. When a file
is added, it creates a corresponding markdown action file in Needs_Action
with metadata about the dropped file.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
"""

import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add watchers directory to path for base_watcher import
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher


class FilesystemWatcher(BaseWatcher):
    """
    Watcher that monitors a drop folder for new files.
    
    When a file is detected, it:
    1. Copies the file to the vault's Inbox folder
    2. Creates a markdown action file in Needs_Action
    """

    def __init__(self, vault_path: str, drop_folder: str = None, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (default: vault/Inbox/Drop)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Setup drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Inbox' / 'Drop'
        
        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup inbox folder for copied files
        self.inbox_folder = self.vault_path / 'Inbox'
        self.inbox_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash
        self.processed_hashes: set = set()
        
        # Keywords that trigger high priority
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'receipt',
            'contract', 'agreement', 'deadline', 'review'
        ]

    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file for deduplication."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _detect_priority(self, filename: str) -> str:
        """
        Detect priority level based on filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            Priority level string
        """
        filename_lower = filename.lower()
        
        for keyword in self.priority_keywords:
            if keyword in filename_lower:
                return "high"
        
        return "normal"

    def _detect_category(self, filename: str) -> str:
        """
        Detect category based on filename and extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            Category string
        """
        filename_lower = filename.lower()
        ext = Path(filename).suffix.lower()
        
        # Category mappings
        if any(x in filename_lower for x in ['invoice', 'bill', 'receipt']):
            return "financial"
        elif any(x in filename_lower for x in ['contract', 'agreement', 'legal']):
            return "legal"
        elif any(x in filename_lower for x in ['report', 'summary', 'analysis']):
            return "report"
        elif ext in ['.pdf', '.doc', '.docx']:
            return "document"
        elif ext in ['.xls', '.xlsx', '.csv']:
            return "spreadsheet"
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return "image"
        else:
            return "general"

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of new file information dictionaries
        """
        new_files = []
        
        if not self.drop_folder.exists():
            return new_files
        
        # Get all files in drop folder
        for filepath in self.drop_folder.iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                file_hash = self._get_file_hash(filepath)
                
                # Skip if already processed
                if file_hash in self.processed_hashes:
                    continue
                
                # Add to new files
                new_files.append({
                    'filepath': filepath,
                    'filename': filepath.name,
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime),
                    'hash': file_hash
                })
                
                # Mark as processed
                self.processed_hashes.add(file_hash)
        
        return new_files

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for the dropped file.
        
        Args:
            item: File information dictionary
            
        Returns:
            Path to the created action file
        """
        filepath = item['filepath']
        filename = item['filename']
        
        # Copy file to inbox
        dest_path = self.inbox_folder / filename
        try:
            shutil.copy2(filepath, dest_path)
            self.logger.info(f"Copied file to inbox: {dest_path.name}")
        except Exception as e:
            self.logger.warning(f"Could not copy file to inbox: {e}")
            dest_path = filepath
        
        # Generate unique ID from hash (first 8 chars)
        unique_id = item['hash'][:8]
        action_filename = self._generate_filename('FILE', unique_id)
        action_path = self.needs_action / action_filename
        
        # Detect priority and category
        priority = self._detect_priority(filename)
        category = self._detect_category(filename)
        
        # Create suggested actions based on category
        suggested_actions = self._get_suggested_actions(category, priority)
        
        # Build action file content
        content = self._build_action_content(
            filename=filename,
            filepath=str(dest_path),
            size=item['size'],
            modified=item['modified'],
            priority=priority,
            category=category,
            suggested_actions=suggested_actions
        )
        
        # Write action file
        action_path.write_text(content, encoding='utf-8')
        
        return action_path

    def _get_suggested_actions(self, category: str, priority: str) -> List[str]:
        """
        Get suggested actions based on category and priority.
        
        Args:
            category: File category
            priority: Priority level
            
        Returns:
            List of suggested action strings
        """
        actions = []
        
        # Category-specific actions
        if category == "financial":
            actions = [
                "Review financial details",
                "Record in accounting system",
                "Check if payment is required",
                "File in appropriate category"
            ]
            if priority == "high":
                actions.insert(0, "⚠️ URGENT: Process immediately")
        elif category == "legal":
            actions = [
                "Review legal terms",
                "Check for required signatures",
                "Forward to legal review if needed",
                "Archive signed copy"
            ]
        elif category == "report":
            actions = [
                "Read and summarize key points",
                "Extract action items",
                "Share with relevant stakeholders",
                "File in reports folder"
            ]
        elif category == "document":
            actions = [
                "Review document content",
                "Determine required action",
                "Extract key information",
                "Archive or process"
            ]
        else:
            actions = [
                "Review file content",
                "Determine required action",
                "Process or archive"
            ]
        
        return actions

    def _build_action_content(
        self,
        filename: str,
        filepath: str,
        size: int,
        modified: datetime,
        priority: str,
        category: str,
        suggested_actions: List[str]
    ) -> str:
        """
        Build the markdown content for the action file.
        
        Args:
            filename: Original filename
            filepath: Path to copied file
            size: File size in bytes
            modified: Last modified timestamp
            priority: Priority level
            category: Category
            suggested_actions: List of suggested actions
            
        Returns:
            Markdown content string
        """
        # Format file size
        size_kb = size / 1024
        if size_kb < 1024:
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = f"{size_kb / 1024:.1f} MB"
        
        # Build frontmatter
        frontmatter = self._create_frontmatter(
            item_type="file_drop",
            source_file=f'"{filename}"',
            source_path=f'"{filepath}"',
            file_size=f'"{size_str}"',
            file_modified=f'"{modified.isoformat()}"',
            category=f'"{category}"',
            priority=f'"{priority}"'
        )
        
        # Build suggested actions markdown
        actions_md = "\n".join([f"- [ ] {action}" for action in suggested_actions])
        
        # Build content
        content = f"""{frontmatter}

# 📄 File Drop: {filename}

## File Information

| Property | Value |
|----------|-------|
| **Original Name** | {filename} |
| **Location** | `{filepath}` |
| **Size** | {size_str} |
| **Modified** | {modified.strftime('%Y-%m-%d %H:%M')} |
| **Category** | {category} |
| **Priority** | {priority} |

## Description

A new file has been dropped for processing. Please review and take appropriate action.

## Suggested Actions

{actions_md}

## Notes

*Add any notes or context here*

---
*Auto-generated by Filesystem Watcher*
"""
        return content


def main():
    """Main entry point for running the watcher standalone."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [drop_folder]")
        print("  vault_path: Path to Obsidian vault")
        print("  drop_folder: Path to drop folder (optional, default: vault/Inbox/Drop)")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    drop_folder = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = FilesystemWatcher(vault_path, drop_folder)
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()


if __name__ == "__main__":
    main()
