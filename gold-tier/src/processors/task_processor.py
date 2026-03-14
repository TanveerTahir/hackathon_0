#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Processor - Processes tasks from Needs_Action folder.

This is the "reasoning" layer that:
- Reads task files
- Generates execution plans
- Creates approval requests
- Moves tasks through workflow
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskProcessor:
    """
    Processes tasks from the Needs_Action folder.
    """

    def __init__(self, vault_path: str):
        """
        Initialize the task processor.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Define folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_dir = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs'

        # Ensure folders exist
        for folder in [self.plans_dir, self.pending_approval, self.approved, 
                       self.rejected, self.done, self.logs_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    def process_all_tasks(self) -> Dict[str, int]:
        """
        Process all tasks in Needs_Action folder.

        Returns:
            Dictionary with processing statistics
        """
        stats = {
            'processed': 0,
            'errors': 0,
            'plans_created': 0,
            'approvals_created': 0
        }

        if not self.needs_action.exists():
            return stats

        # Get all markdown files
        task_files = list(self.needs_action.glob('*.md'))

        for task_file in task_files:
            try:
                result = self.process_task(task_file)
                stats['processed'] += 1
                if result.get('plan_created'):
                    stats['plans_created'] += 1
                if result.get('approval_created'):
                    stats['approvals_created'] += 1
            except Exception as e:
                self.logger.error(f"Error processing {task_file.name}: {e}")
                stats['errors'] += 1

        return stats

    def process_task(self, task_file: Path) -> Dict[str, Any]:
        """
        Process a single task file.

        Args:
            task_file: Path to the task file

        Returns:
            Processing result dictionary
        """
        result = {
            'success': True,
            'plan_created': False,
            'approval_created': False,
            'moved_to': None
        }

        # Read task file
        content = task_file.read_text(encoding='utf-8')

        # Extract metadata
        task_type = self._extract_frontmatter_value(content, 'type')
        priority = self._extract_frontmatter_value(content, 'priority')
        source = self._extract_frontmatter_value(content, 'source')

        # Determine if approval is needed
        needs_approval = self._requires_approval(task_type, priority, content)

        if needs_approval:
            # Create approval request
            approval_file = self._create_approval_request(task_file, content)
            result['approval_created'] = True
            result['moved_to'] = str(approval_file)
        else:
            # Create execution plan
            plan_file = self._create_execution_plan(task_file, content, task_type)
            result['plan_created'] = True

            # For low-priority simple tasks, can auto-complete
            if priority == 'low':
                self._complete_task(task_file)
                result['moved_to'] = str(self.done / task_file.name)

        return result

    def _requires_approval(self, task_type: str, priority: str, content: str) -> bool:
        """
        Determine if task requires human approval.

        Args:
            task_type: Type of task
            priority: Priority level
            content: Task content

        Returns:
            True if approval required
        """
        # High priority tasks always need approval
        if priority == 'high':
            return True

        # Certain task types need approval
        approval_types = [
            'payment', 'invoice', 'financial',
            'email_external', 'social_post',
            'approval_request'
        ]

        if any(t in (task_type or '').lower() for t in approval_types):
            return True

        # Check content for sensitive keywords
        sensitive_keywords = [
            'payment', 'invoice', 'contract', 'legal',
            'send email', 'post to', 'publish'
        ]

        content_lower = content.lower()
        if any(kw in content_lower for kw in sensitive_keywords):
            return True

        return False

    def _create_approval_request(self, task_file: Path, content: str) -> Path:
        """
        Create approval request file.

        Args:
            task_file: Original task file
            content: Task content

        Returns:
            Path to approval request file
        """
        # Extract relevant info
        task_type = self._extract_frontmatter_value(content, 'type')
        priority = self._extract_frontmatter_value(content, 'priority')
        source = self._extract_frontmatter_value(content, 'source')

        # Generate approval filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_filename = f"APPROVAL_{task_type or 'TASK'}_{timestamp}.md"
        approval_path = self.pending_approval / approval_filename

        # Build approval content
        approval_content = f"""---
type: approval_request
original_task: "{task_file.name}"
request_type: "{task_type or 'task'}"
priority: "{priority or 'normal'}"
source: "{source or 'unknown'}"
created: {datetime.now().isoformat()}
status: pending
expires: {(datetime.now().replace(hour=23, minute=59)).isoformat()}
---

# ⚠️ Approval Required

## Original Task

**File:** `{task_file.name}`

**Type:** {task_type or 'Task'}

**Priority:** {priority or 'normal'}

**Source:** {source or 'Unknown'}

---

## Task Content

{content}

---

## Action Required

Please review the task above and take one of the following actions:

### To Approve
1. Review the task details
2. Move this file to `/Approved` folder
3. The task will be executed automatically

### To Reject
1. Add rejection reason below
2. Move this file to `/Rejected` folder

---

## Decision

**Status:** Pending

**Approved By:** 

**Approved At:** 

**Rejection Reason:** 

---
*Auto-generated by Task Processor*
"""

        approval_path.write_text(approval_content, encoding='utf-8')

        # Move original task to pending folder
        dest = self.pending_approval / task_file.name
        shutil.move(str(task_file), str(dest))

        self.logger.info(f"Created approval request: {approval_filename}")
        return approval_path

    def _create_execution_plan(self, task_file: Path, content: str, task_type: str) -> Path:
        """
        Create execution plan for task.

        Args:
            task_file: Original task file
            content: Task content
            task_type: Task type

        Returns:
            Path to plan file
        """
        # Generate plan filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_filename = f"PLAN_{task_type or 'TASK'}_{timestamp}.md"
        plan_path = self.plans_dir / plan_filename

        # Build suggested steps based on task type
        steps = self._generate_plan_steps(task_type, content)

        # Build plan content
        plan_content = f"""---
type: execution_plan
original_task: "{task_file.name}"
task_type: "{task_type or 'task'}"
created: {datetime.now().isoformat()}
status: planned
completed_steps: 0
total_steps: {len(steps)}
---

# 📋 Execution Plan

## Original Task

**File:** `{task_file.name}`

**Type:** {task_type or 'Task'}

---

## Task Content

{content}

---

## Execution Steps

"""

        for i, step in enumerate(steps, 1):
            plan_content += f"{i}. [ ] {step}\n"

        plan_content += f"""
---

## Execution Log

| Step | Timestamp | Status | Notes |
|------|-----------|--------|-------|
"""

        for i in range(1, len(steps) + 1):
            plan_content += f"| {i} | | | |\n"

        plan_content += """
---

## Completion

**Status:** Not Started

**Completed At:** 

**Notes:** 

---
*Auto-generated by Task Processor*
"""

        plan_path.write_text(plan_content, encoding='utf-8')

        self.logger.info(f"Created execution plan: {plan_filename}")
        return plan_path

    def _generate_plan_steps(self, task_type: str, content: str) -> List[str]:
        """
        Generate execution steps based on task type.

        Args:
            task_type: Task type
            content: Task content

        Returns:
            List of step descriptions
        """
        steps = []

        task_type_lower = (task_type or '').lower()

        if 'email' in task_type_lower:
            steps = [
                "Read email content and identify required action",
                "Draft response or determine forwarding recipient",
                "Check for attachments or links",
                "Send email or move to approved folder"
            ]
        elif 'invoice' in task_type_lower or 'payment' in task_type_lower:
            steps = [
                "Review invoice/payment details",
                "Verify amount and recipient",
                "Check against business records",
                "Process payment or send invoice",
                "Update accounting records"
            ]
        elif 'file' in task_type_lower:
            steps = [
                "Review file content",
                "Determine required action",
                "Process or archive file",
                "Update task status"
            ]
        elif 'social' in task_type_lower or 'facebook' in task_type_lower or 'twitter' in task_type_lower:
            steps = [
                "Review social media content",
                "Determine appropriate response",
                "Draft response or engagement",
                "Post or schedule content"
            ]
        else:
            steps = [
                "Review task details",
                "Determine required action",
                "Execute action",
                "Verify completion",
                "Update task status"
            ]

        return steps

    def _complete_task(self, task_file: Path):
        """
        Mark task as complete.

        Args:
            task_file: Path to task file
        """
        dest = self.done / task_file.name
        shutil.move(str(task_file), str(dest))
        self.logger.info(f"Task completed: {task_file.name}")

    def _extract_frontmatter_value(self, content: str, key: str) -> Optional[str]:
        """Extract a value from YAML frontmatter"""
        try:
            lines = content.split('\n')
            in_frontmatter = False
            for line in lines:
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                elif in_frontmatter and line.startswith(f'{key}:'):
                    value = line.split(':', 1)[1].strip().strip('"\'')
                    return value
        except:
            pass
        return None

    def update_dashboard(self) -> bool:
        """
        Update the Dashboard.md with current stats.

        Returns:
            True if successful
        """
        dashboard_path = self.vault_path / 'Dashboard.md'

        if not dashboard_path.exists():
            self.logger.warning("Dashboard.md not found")
            return False

        try:
            # Count tasks in each folder
            stats = {
                'needs_action': len(list(self.needs_action.glob('*.md'))),
                'plans': len(list(self.plans_dir.glob('*.md'))),
                'pending_approval': len(list(self.pending_approval.glob('*.md'))),
                'approved': len(list(self.approved.glob('*.md'))),
                'done': len(list(self.done.glob('*.md')))
            }

            # Read current dashboard
            content = dashboard_path.read_text(encoding='utf-8')

            # Update stats (simplified - would parse and update properly)
            # For now, just log
            self.logger.info(f"Dashboard stats: {stats}")

            return True

        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
            return False
