#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

Gold Tier version with enhanced error handling and audit logging.
"""

import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher


class FilesystemWatcher(BaseWatcher):
    """
    Watcher that monitors a drop folder for new files.
    """

    def __init__(self, vault_path: str, drop_folder: str = None, check_interval: int = 30):
        """Initialize the filesystem watcher."""
        super().__init__(vault_path, check_interval)

        # Setup drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Inbox' / 'Drop'

        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.inbox_folder = self.vault_path / 'Inbox'
        self.inbox_folder.mkdir(parents=True, exist_ok=True)

        self.processed_hashes: set = set()
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'receipt',
            'contract', 'agreement', 'deadline', 'review'
        ]

    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _detect_priority(self, filename: str) -> str:
        """Detect priority level based on filename."""
        filename_lower = filename.lower()
        for keyword in self.priority_keywords:
            if keyword in filename_lower:
                return "high"
        return "normal"

    def _detect_category(self, filename: str) -> str:
        """Detect category based on filename."""
        filename_lower = filename.lower()
        ext = Path(filename).suffix.lower()

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
        """Check the drop folder for new files."""
        new_files = []

        if not self.drop_folder.exists():
            return new_files

        for filepath in self.drop_folder.iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                file_hash = self._get_file_hash(filepath)

                if file_hash in self.processed_hashes:
                    continue

                new_files.append({
                    'filepath': filepath,
                    'filename': filepath.name,
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime),
                    'hash': file_hash
                })

                self.processed_hashes.add(file_hash)

        return new_files

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create a markdown action file for the dropped file."""
        filepath = item['filepath']
        filename = item['filename']

        # Copy file to inbox
        dest_path = self.inbox_folder / filename
        try:
            shutil.copy2(filepath, dest_path)
            self.logger.info(f"Copied file to inbox: {dest_path.name}")
        except Exception as e:
            self.logger.warning(f"Could not copy file: {e}")
            dest_path = filepath

        unique_id = item['hash'][:8]
        action_filename = self._generate_filename('FILE', unique_id)
        action_path = self.needs_action / action_filename

        priority = self._detect_priority(filename)
        category = self._detect_category(filename)
        suggested_actions = self._get_suggested_actions(category, priority)

        content = self._build_action_content(
            filename=filename,
            filepath=str(dest_path),
            size=item['size'],
            modified=item['modified'],
            priority=priority,
            category=category,
            suggested_actions=suggested_actions
        )

        action_path.write_text(content, encoding='utf-8')
        return action_path

    def _get_suggested_actions(self, category: str, priority: str) -> List[str]:
        """Get suggested actions based on category."""
        actions = []

        if category == "financial":
            actions = [
                "Review financial details",
                "Record in accounting system",
                "Check if payment is required"
            ]
            if priority == "high":
                actions.insert(0, "⚠️ URGENT: Process immediately")
        elif category == "legal":
            actions = [
                "Review legal terms",
                "Check for required signatures",
                "Forward to legal review if needed"
            ]
        elif category == "report":
            actions = [
                "Read and summarize key points",
                "Extract action items",
                "Share with stakeholders"
            ]
        else:
            actions = [
                "Review file content",
                "Determine required action",
                "Process or archive"
            ]

        return actions

    def _build_action_content(
        self, filename: str, filepath: str, size: int,
        modified: datetime, priority: str, category: str,
        suggested_actions: List[str]
    ) -> str:
        """Build markdown content for action file."""
        size_kb = size / 1024
        size_str = f"{size_kb / 1024:.1f} MB" if size_kb >= 1024 else f"{size_kb:.1f} KB"

        frontmatter = self._create_frontmatter(
            item_type="file_drop",
            source_file=f'"{filename}"',
            source_path=f'"{filepath}"',
            file_size=f'"{size_str}"',
            file_modified=f'"{modified.isoformat()}"',
            category=f'"{category}"',
            priority=f'"{priority}"'
        )

        actions_md = "\n".join([f"- [ ] {action}" for action in suggested_actions])

        return f"""{frontmatter}

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

A new file has been dropped for processing.

## Suggested Actions

{actions_md}

## Notes

*Add any notes or context here*

---
*Auto-generated by Filesystem Watcher*
"""


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [drop_folder]")
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
