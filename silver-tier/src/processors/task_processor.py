#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Processor - Reads tasks from Needs_Action and generates plans.

This module provides the "Reasoning" layer of the AI Employee architecture.
It reads task files, analyzes them, and generates structured action plans.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TaskProcessor:
    """
    Processes tasks from the Needs_Action folder.
    
    Responsibilities:
    - Read and parse task files
    - Generate action plans
    - Update dashboard
    - Move completed tasks
    """

    def __init__(self, vault_path: str):
        """
        Initialize the task processor.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        
        # Define folder paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_dir = self.vault_path / 'Plans'
        self.done_dir = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.rejected_dir = self.vault_path / 'Rejected'
        self.logs_dir = self.vault_path / 'Logs'
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for directory in [
            self.needs_action, self.plans_dir, self.done_dir,
            self.pending_approval, self.approved_dir, self.rejected_dir,
            self.logs_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_pending_tasks(self) -> List[Path]:
        """
        Get all pending task files from Needs_Action.
        
        Returns:
            List of paths to pending task files
        """
        if not self.needs_action.exists():
            return []
        
        return sorted(
            self.needs_action.glob('*.md'),
            key=lambda p: p.stat().st_mtime
        )

    def read_task(self, task_path: Path) -> Dict[str, Any]:
        """
        Read and parse a task file.
        
        Args:
            task_path: Path to the task file
            
        Returns:
            Dictionary with task data
        """
        content = task_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = self._parse_frontmatter(content)
        
        # Extract body (content after frontmatter)
        body_match = re.search(r'---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        body = body_match.group(2) if body_match else content
        
        # Extract suggested actions
        actions = self._extract_actions(body)
        
        return {
            'path': task_path,
            'filename': task_path.name,
            'frontmatter': frontmatter,
            'body': body,
            'actions': actions,
            'type': frontmatter.get('type', 'unknown'),
            'priority': frontmatter.get('priority', 'normal'),
            'status': frontmatter.get('status', 'pending'),
            'category': frontmatter.get('category', 'general')
        }

    def _parse_frontmatter(self, content: str) -> Dict[str, str]:
        """
        Parse YAML frontmatter from content.
        
        Args:
            content: File content
            
        Returns:
            Dictionary of frontmatter fields
        """
        frontmatter = {}
        
        # Simple YAML parser for flat key-value pairs
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if match:
            fm_content = match.group(1)
            for line in fm_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    frontmatter[key] = value
        
        return frontmatter

    def _extract_actions(self, body: str) -> List[Dict[str, Any]]:
        """
        Extract action items from task body.
        
        Args:
            body: Task body content
            
        Returns:
            List of action dictionaries
        """
        actions = []
        
        # Find checkbox items
        for match in re.finditer(r'^-\s*\[([ x])\]\s*(.+)$', body, re.MULTILINE):
            checked = match.group(1) == 'x'
            action_text = match.group(2).strip()
            actions.append({
                'text': action_text,
                'completed': checked
            })
        
        return actions

    def generate_plan(self, task: Dict[str, Any]) -> Path:
        """
        Generate an action plan for a task.
        
        Args:
            task: Task data dictionary
            
        Returns:
            Path to the created plan file
        """
        # Generate plan filename
        plan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        task_type = task['type']
        plan_filename = f"PLAN_{task_type}_{plan_id}.md"
        plan_path = self.plans_dir / plan_filename
        
        # Build plan content
        content = self._build_plan_content(task, plan_id)
        
        # Write plan file
        plan_path.write_text(content, encoding='utf-8')
        
        return plan_path

    def _build_plan_content(self, task: Dict[str, Any], plan_id: str) -> str:
        """
        Build the markdown content for a plan file.
        
        Args:
            task: Task data dictionary
            plan_id: Unique plan identifier
            
        Returns:
            Markdown content string
        """
        # Determine if approval is needed
        needs_approval = self._check_approval_required(task)
        
        # Build action steps
        action_steps = []
        for i, action in enumerate(task['actions'], 1):
            status = "[x]" if action['completed'] else "[ ]"
            action_steps.append(f"{i}. {status} {action['text']}")
        
        if not action_steps:
            action_steps = ["1. [ ] Review task and determine required actions"]
        
        # Build content
        content = f"""---
type: plan
task_file: "{task['filename']}"
task_type: "{task['type']}"
priority: "{task['priority']}"
category: "{task['category']}"
created: {datetime.now().isoformat()}
status: planned
needs_approval: {str(needs_approval).lower()}
---

# 📋 Action Plan: {task['filename']}

## Task Summary

| Property | Value |
|----------|-------|
| **Task Type** | {task['type']} |
| **Priority** | {task['priority']} |
| **Category** | {task['category']} |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |

## Task Content

{task['body'][:500] if len(task['body']) > 500 else task['body']}

## Action Steps

{'\n'.join(action_steps)}

## Approval Required

{'⚠️ **Yes** - This task requires human approval before execution.' if needs_approval else '✅ **No** - This task can be executed automatically.'}

## Execution Notes

*Add any notes about execution here*

## Completion Criteria

- [ ] All action steps completed
- [ ] Results documented
- [ ] Task file moved to Done
- [ ] Dashboard updated

---
*Auto-generated by Task Processor*
"""
        return content

    def _check_approval_required(self, task: Dict[str, Any]) -> bool:
        """
        Check if a task requires human approval.
        
        Args:
            task: Task data dictionary
            
        Returns:
            True if approval required
        """
        # Check priority
        if task['priority'] == 'high':
            return True
        
        # Check category
        if task['category'] == 'financial':
            return True
        
        # Check for approval keywords in body
        approval_keywords = [
            'payment', 'approve', 'authorization', 'confirm',
            'send email', 'post', 'publish', 'transfer'
        ]
        
        body_lower = task['body'].lower()
        for keyword in approval_keywords:
            if keyword in body_lower:
                return True
        
        return False

    def create_approval_request(self, task: Dict[str, Any], plan_path: Path) -> Path:
        """
        Create an approval request file.
        
        Args:
            task: Task data dictionary
            plan_path: Path to the plan file
            
        Returns:
            Path to the approval request file
        """
        # Generate approval filename
        approval_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_filename = f"APPROVAL_{task['type']}_{approval_id}.md"
        approval_path = self.pending_approval / approval_filename
        
        # Build content
        content = f"""---
type: approval_request
task_file: "{task['filename']}"
plan_file: "{plan_path.name}"
task_type: "{task['type']}"
created: {datetime.now().isoformat()}
expires: {(datetime.now().replace(hour=23, minute=59)).isoformat()}
status: pending
---

# ⚠️ Approval Required

## Request Details

| Property | Value |
|----------|-------|
| **Task** | {task['filename']} |
| **Type** | {task['type']} |
| **Priority** | {task['priority']} |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |

## Task Summary

{task['body'][:300] if len(task['body']) > 300 else task['body']}

## Plan Reference

See plan file: `{plan_path.name}`

## Instructions

**To Approve:**
1. Review the task and plan above
2. Move this file to the `/Approved` folder
3. The AI will execute the plan

**To Reject:**
1. Add a comment below explaining why
2. Move this file to the `/Rejected` folder

## Decision

*Add your decision and any comments here*

---
*Approval expires at end of day*
"""
        approval_path.write_text(content, encoding='utf-8')
        
        return approval_path

    def process_approved_tasks(self) -> List[Dict[str, Any]]:
        """
        Process tasks that have been approved.
        
        Returns:
            List of processed task results
        """
        results = []
        
        if not self.approved_dir.exists():
            return results
        
        for approval_file in self.approved_dir.glob('*.md'):
            try:
                result = self._execute_approved_task(approval_file)
                results.append(result)
            except Exception as e:
                self._log_error(f"Error processing approved task {approval_file.name}: {e}")
        
        return results

    def _execute_approved_task(self, approval_file: Path) -> Dict[str, Any]:
        """
        Execute an approved task.
        
        Args:
            approval_file: Path to the approval file
            
        Returns:
            Result dictionary
        """
        # Read approval file to get task info
        content = approval_file.read_text(encoding='utf-8')
        frontmatter = self._parse_frontmatter(content)
        
        task_filename = frontmatter.get('task_file', '')
        plan_filename = frontmatter.get('plan_file', '')
        
        # Find the original task file
        task_path = self.needs_action / task_filename
        if not task_path.exists():
            # Try to find by pattern
            matching = list(self.needs_action.glob(f"*{task_filename.split('_')[1]}*"))
            if matching:
                task_path = matching[0]
        
        # Move task to Done
        if task_path.exists():
            shutil.move(str(task_path), str(self.done_dir / task_path.name))
        
        # Move approval file to Done
        shutil.move(str(approval_file), str(self.done_dir / approval_file.name))
        
        # Update dashboard
        self.update_dashboard()
        
        return {
            'task': task_filename,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }

    def update_dashboard(self):
        """Update the dashboard with current statistics."""
        if not self.dashboard_path.exists():
            return
        
        content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Count items in each folder
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        plans_count = len(list(self.plans_dir.glob('*.md')))
        pending_count = len(list(self.pending_approval.glob('*.md')))
        done_today = len([
            f for f in self.done_dir.glob('*.md')
            if datetime.fromtimestamp(f.stat().st_mtime).date() == datetime.now().date()
        ])
        
        # Update stats table
        content = re.sub(
            r'\| Pending Tasks \|.*\|',
            f'| Pending Tasks | {needs_action_count} | - |',
            content
        )
        content = re.sub(
            r'\| In Progress \|.*\|',
            f'| In Progress | {plans_count} | - |',
            content
        )
        content = re.sub(
            r'\| Completed Today \|.*\|',
            f'| Completed Today | {done_today} | - |',
            content
        )
        content = re.sub(
            r'\| Awaiting Approval \|.*\|',
            f'| Awaiting Approval | {pending_count} | - |',
            content
        )
        
        # Update folder counts
        content = re.sub(
            r'\| Needs_Action \|.*\|',
            f'| Needs_Action | {needs_action_count} | - |',
            content
        )
        content = re.sub(
            r'\| Plans \|.*\|',
            f'| Plans | {plans_count} | - |',
            content
        )
        content = re.sub(
            r'\| Pending_Approval \|.*\|',
            f'| Pending_Approval | {pending_count} | - |',
            content
        )
        
        # Update timestamp
        content = re.sub(
            r'Last full refresh:.*',
            f'Last full refresh: {datetime.now().isoformat()}',
            content
        )
        content = re.sub(
            r'\*\*Generated:\*\*.*',
            f'**Generated:** {datetime.now().strftime("%Y-%m-%d")}',
            content
        )
        
        self.dashboard_path.write_text(content, encoding='utf-8')

    def _log_error(self, message: str):
        """Log an error message."""
        log_file = self.logs_dir / f"processor_{datetime.now().strftime('%Y-%m-%d')}.log"
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [ERROR] {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def process_all_tasks(self) -> Dict[str, int]:
        """
        Process all pending tasks.
        
        Returns:
            Dictionary with processing statistics
        """
        stats = {
            'processed': 0,
            'plans_created': 0,
            'approvals_requested': 0,
            'errors': 0
        }
        
        tasks = self.get_pending_tasks()
        
        for task_path in tasks:
            try:
                # Read task
                task = self.read_task(task_path)
                
                # Generate plan
                plan_path = self.generate_plan(task)
                stats['plans_created'] += 1
                
                # Check if approval needed
                if self._check_approval_required(task):
                    self.create_approval_request(task, plan_path)
                    stats['approvals_requested'] += 1
                else:
                    # Auto-execute non-sensitive tasks
                    self._execute_approved_task(plan_path)
                
                stats['processed'] += 1
                
            except Exception as e:
                self._log_error(f"Error processing {task_path.name}: {e}")
                stats['errors'] += 1
        
        # Update dashboard
        self.update_dashboard()
        
        return stats
