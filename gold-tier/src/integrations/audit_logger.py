#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logger - Comprehensive audit logging for AI Employee System.

Provides:
- Action logging
- Change tracking
- Compliance reporting
- Audit trail export

Usage:
    from integrations.audit_logger import AuditLogger
    
    logger = AuditLogger(vault_path)
    logger.log_action('invoice_created', {'invoice_id': 123, 'amount': 1000})
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


class ActionType(Enum):
    """Types of auditable actions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    SEND = "send"
    RECEIVE = "receive"
    PROCESS = "process"
    ERROR = "error"
    SYSTEM = "system"


class AuditLogger:
    """
    Comprehensive audit logger for compliance and tracking.
    """

    def __init__(self, vault_path: str):
        """
        Initialize the audit logger.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.audit_dir = self.vault_path / 'Logs' / 'Audit'
        self.daily_log: Optional[Path] = None
        self.current_date: Optional[str] = None

        # Ensure audit directory exists
        self.audit_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _get_daily_log(self) -> Path:
        """Get or create today's audit log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.current_date != today:
            self.current_date = today
            self.daily_log = self.audit_dir / f"audit_{today}.jsonl"
        return self.daily_log

    def log_action(
        self,
        action: str,
        details: Dict[str, Any],
        actor: str = "ai_employee",
        action_type: ActionType = None,
        source: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Log an action to the audit trail.

        Args:
            action: Action name/description
            details: Action details
            actor: Who/what performed the action
            action_type: Type of action
            source: Source system/component
            metadata: Additional metadata

        Returns:
            Audit entry ID
        """
        if action_type is None:
            action_type = ActionType.PROCESS

        timestamp = datetime.now()
        entry_id = f"{timestamp.strftime('%Y%m%d%H%M%S%f')}"

        audit_entry = {
            'entry_id': entry_id,
            'timestamp': timestamp.isoformat(),
            'action': action,
            'action_type': action_type.value,
            'actor': actor,
            'source': source or self.__class__.__name__,
            'details': details,
            'metadata': metadata or {}
        }

        # Write to daily log
        log_file = self._get_daily_log()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, default=str) + '\n')

        self.logger.debug(f"Audit logged: {action} ({entry_id})")

        return entry_id

    def log_create(
        self,
        resource_type: str,
        resource_id: Any,
        details: Dict[str, Any],
        **kwargs
    ) -> str:
        """Log a create action"""
        return self.log_action(
            action=f"create_{resource_type}",
            details={'resource_type': resource_type, 'resource_id': resource_id, **details},
            action_type=ActionType.CREATE,
            **kwargs
        )

    def log_read(
        self,
        resource_type: str,
        resource_id: Any,
        **kwargs
    ) -> str:
        """Log a read action"""
        return self.log_action(
            action=f"read_{resource_type}",
            details={'resource_type': resource_type, 'resource_id': resource_id},
            action_type=ActionType.READ,
            **kwargs
        )

    def log_update(
        self,
        resource_type: str,
        resource_id: Any,
        changes: Dict[str, Any],
        **kwargs
    ) -> str:
        """Log an update action"""
        return self.log_action(
            action=f"update_{resource_type}",
            details={'resource_type': resource_type, 'resource_id': resource_id, 'changes': changes},
            action_type=ActionType.UPDATE,
            **kwargs
        )

    def log_delete(
        self,
        resource_type: str,
        resource_id: Any,
        **kwargs
    ) -> str:
        """Log a delete action"""
        return self.log_action(
            action=f"delete_{resource_type}",
            details={'resource_type': resource_type, 'resource_id': resource_id},
            action_type=ActionType.DELETE,
            **kwargs
        )

    def log_approve(
        self,
        approval_type: str,
        approval_id: Any,
        details: Dict[str, Any],
        **kwargs
    ) -> str:
        """Log an approval action"""
        return self.log_action(
            action=f"approve_{approval_type}",
            details={'approval_type': approval_type, 'approval_id': approval_id, **details},
            action_type=ActionType.APPROVE,
            **kwargs
        )

    def log_reject(
        self,
        rejection_type: str,
        rejection_id: Any,
        reason: str,
        **kwargs
    ) -> str:
        """Log a rejection action"""
        return self.log_action(
            action=f"reject_{rejection_type}",
            details={'rejection_type': rejection_type, 'rejection_id': rejection_id, 'reason': reason},
            action_type=ActionType.REJECT,
            **kwargs
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        **kwargs
    ) -> str:
        """Log an error"""
        return self.log_action(
            action=f"error_{error_type}",
            details={'error_type': error_type, 'error_message': error_message, 'context': context},
            action_type=ActionType.ERROR,
            **kwargs
        )

    def get_audit_trail(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        action_type: ActionType = None,
        actor: str = None,
        source: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with optional filters.

        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            action_type: Filter by action type
            actor: Filter by actor
            source: Filter by source

        Returns:
            List of audit entries
        """
        entries = []

        # Determine which files to read
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now()

        current = start_date
        while current <= end_date:
            log_file = self.audit_dir / f"audit_{current.strftime('%Y-%m-%d')}.jsonl"
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            entry = json.loads(line.strip())

                            # Apply filters
                            if action_type and entry.get('action_type') != action_type.value:
                                continue
                            if actor and entry.get('actor') != actor:
                                continue
                            if source and entry.get('source') != source:
                                continue

                            entries.append(entry)
                except Exception as e:
                    self.logger.error(f"Error reading audit log: {e}")

            current += timedelta(days=1)

        return entries

    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "summary"
    ) -> str:
        """
        Generate audit report.

        Args:
            start_date: Report start date
            end_date: Report end date
            report_type: Type of report (summary, detailed, compliance)

        Returns:
            Report content as markdown string
        """
        entries = self.get_audit_trail(start_date, end_date)

        # Group by action type
        by_type = {}
        by_actor = {}
        by_source = {}

        for entry in entries:
            action_type = entry.get('action_type', 'unknown')
            actor = entry.get('actor', 'unknown')
            source = entry.get('source', 'unknown')

            by_type[action_type] = by_type.get(action_type, 0) + 1
            by_actor[actor] = by_actor.get(actor, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1

        # Build report
        report = f"""---
type: audit_report
report_type: {report_type}
generated: {datetime.now().isoformat()}
period_start: {start_date.strftime('%Y-%m-%d')}
period_end: {end_date.strftime('%Y-%m-%d')}
---

# 📊 Audit Report

**Report Type:** {report_type.title()}

**Period:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Total Entries:** {len(entries)}

---

## Summary by Action Type

| Action Type | Count |
|-------------|-------|
"""

        for action_type, count in sorted(by_type.items()):
            report += f"| {action_type.title()} | {count} |\n"

        report += """
## Summary by Actor

| Actor | Count |
|-------|-------|
"""

        for actor, count in sorted(by_actor.items(), key=lambda x: x[1], reverse=True):
            report += f"| {actor} | {count} |\n"

        report += """
## Summary by Source

| Source | Count |
|--------|-------|
"""

        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
            report += f"| {source} | {count} |\n"

        if report_type == "detailed":
            report += """
## Detailed Entries

"""
            for entry in entries[:100]:  # Limit to 100 entries
                report += f"""
### {entry.get('entry_id')}

- **Timestamp:** {entry.get('timestamp')}
- **Action:** {entry.get('action')}
- **Type:** {entry.get('action_type')}
- **Actor:** {entry.get('actor')}
- **Details:** {json.dumps(entry.get('details'), indent=2)}

---
"""

        report += """
---
*Report generated by AI Employee Audit Logger*
"""

        return report

    def export_audit_trail(
        self,
        output_path: str,
        start_date: datetime = None,
        end_date: datetime = None,
        format: str = "json"
    ) -> Path:
        """
        Export audit trail to file.

        Args:
            output_path: Output file path
            start_date: Filter by start date
            end_date: Filter by end date
            format: Export format (json, csv)

        Returns:
            Path to exported file
        """
        entries = self.get_audit_trail(start_date, end_date)
        output = Path(output_path)

        if format == "json":
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2, default=str)
        elif format == "csv":
            import csv
            if entries:
                keys = entries[0].keys()
                with open(output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(entries)

        self.logger.info(f"Audit trail exported to {output}")
        return output


# Global audit logger instance
global_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str = None) -> AuditLogger:
    """Get or create global audit logger"""
    global global_audit_logger
    if global_audit_logger is None:
        if vault_path:
            global_audit_logger = AuditLogger(vault_path)
        else:
            raise ValueError("vault_path required for initial audit logger creation")
    return global_audit_logger
