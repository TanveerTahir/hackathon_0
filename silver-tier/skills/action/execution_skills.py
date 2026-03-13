"""
Autonomous Execution Skills - Action Layer for AI Employee

This module contains skills for autonomous task execution, scheduling,
decision making, and progress tracking.

Silver Tier Implementation - Personal AI Employee Hackathon 0
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json
import uuid
import re

from ..core.base_skill import BaseSkill, SkillExecutionError


class TaskCreationSkill(BaseSkill):
    """
    Skill: task_creation
    
    Creates structured task files in the vault based on extracted information.
    
    Input:
        - task_data: dict - Task information (title, description, priority, etc.)
        - task_type: str - Type of task (email, whatsapp, linkedin, general)
        - auto_categorize: bool - Automatically categorize task
        - destination_folder: str - Target folder (default: Needs_Action)
    
    Output:
        - success: bool
        - data: dict containing:
            - task_id: str
            - file_path: str
            - task_data: dict
            - created_at: str (ISO format)
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="task_creation",
            description="Create structured task files in the vault",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.task_counter = 0
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_data": {
                    "type": "object",
                    "description": "Task information"
                },
                "task_type": {
                    "type": "string",
                    "description": "Type of task",
                    "enum": ["email", "whatsapp", "linkedin", "google", "general"]
                },
                "auto_categorize": {
                    "type": "boolean",
                    "description": "Automatically categorize task"
                },
                "destination_folder": {
                    "type": "string",
                    "description": "Target folder"
                }
            },
            "required": ["task_data"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "file_path": {"type": "string"},
                        "task_data": {"type": "object"},
                        "created_at": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the task creation skill"""
        try:
            task_data = kwargs.get("task_data", {})
            task_type = kwargs.get("task_type", "general")
            auto_categorize = kwargs.get("auto_categorize", True)
            destination_folder = kwargs.get("destination_folder", "Needs_Action")
            
            if not task_data.get("title"):
                raise SkillExecutionError("task_data must include 'title'")
            
            # Generate task ID
            task_id = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Auto-categorize if requested
            if auto_categorize:
                task_data["category"] = self._categorize_task(task_data)
                task_data["tags"] = self._generate_tags(task_data, task_type)
            
            # Ensure destination folder exists
            dest_path = self.vault_path / destination_folder if self.vault_path else Path(destination_folder)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', task_data["title"])[:30].replace(" ", "_")
            filename = f"{task_type.upper()}_{safe_title}_{task_id}.md"
            filepath = dest_path / filename
            
            # Generate markdown content
            content = self._generate_task_content(task_id, task_data, task_type)
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            
            result = {
                "task_id": task_id,
                "file_path": str(filepath),
                "task_data": task_data,
                "created_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "create_task",
                "task_id": task_id,
                "task_type": task_type,
                "file_path": str(filepath),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error creating task: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _categorize_task(self, task_data: Dict) -> str:
        """Categorize task based on content"""
        title = task_data.get("title", "").lower()
        description = task_data.get("description", "").lower()
        text = f"{title} {description}"
        
        categories = {
            "communication": ["email", "reply", "message", "call", "respond"],
            "finance": ["invoice", "payment", "bill", "money", "transaction"],
            "meeting": ["meeting", "appointment", "schedule", "call", "zoom"],
            "social": ["post", "linkedin", "twitter", "facebook", "social media"],
            "admin": ["document", "file", "organize", "update", "review"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "general"
    
    def _generate_tags(self, task_data: Dict, task_type: str) -> List[str]:
        """Generate tags for the task"""
        tags = [task_type]
        
        priority = task_data.get("priority", "normal")
        tags.append(f"priority:{priority}")
        
        category = task_data.get("category", "general")
        tags.append(f"category:{category}")
        
        return tags
    
    def _generate_task_content(self, task_id: str, task_data: Dict, task_type: str) -> str:
        """Generate markdown content for task file"""
        frontmatter = {
            "type": f"{task_type}_task",
            "task_id": task_id,
            "title": task_data.get("title", "Untitled"),
            "priority": task_data.get("priority", "normal"),
            "status": "pending",
            "created": datetime.now().isoformat(),
            "category": task_data.get("category", "general"),
            "tags": task_data.get("tags", [])
        }
        
        # Build frontmatter YAML
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}:")
                for item in value:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        
        frontmatter_text = "\n".join(fm_lines)
        
        # Build body
        body = f"""

# Task: {task_data.get('title', 'Untitled')}

## Description
{task_data.get('description', 'No description provided.')}

## Source
Type: {task_type}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Action Items
"""
        # Add suggested actions based on task type
        actions = self._get_suggested_actions(task_type, task_data)
        for action in actions:
            body += f"- [ ] {action}\n"
        
        body += "\n## Notes\nAdd any additional notes here...\n"
        
        return frontmatter_text + body
    
    def _get_suggested_actions(self, task_type: str, task_data: Dict) -> List[str]:
        """Get suggested actions based on task type"""
        default_actions = ["Review task details", "Take necessary action", "Mark as complete"]
        
        type_actions = {
            "email": ["Read full email", "Draft response", "Send reply", "Archive email"],
            "whatsapp": ["Read message", "Respond if needed", "Archive conversation"],
            "linkedin": ["Review opportunity", "Consider response", "Update CRM"],
            "google": ["Review alert", "Take action if needed", "Archive"],
        }
        
        return type_actions.get(task_type, default_actions)


class TaskSchedulingSkill(BaseSkill):
    """
    Skill: task_scheduling
    
    Schedules tasks for execution based on priority, deadlines, and availability.
    
    Input:
        - tasks: list - List of tasks to schedule
        - schedule_config: dict - Scheduling configuration
        - working_hours: dict - Working hours configuration
        - blackout_dates: list - Dates when no tasks should be scheduled
    
    Output:
        - success: bool
        - data: dict containing:
            - scheduled_tasks: list with scheduled times
            - schedule_conflicts: list
            - recommendations: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="task_scheduling",
            description="Schedule tasks for execution based on priority and availability",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.working_hours = self.config.get("working_hours", {
            "start": 9,  # 9 AM
            "end": 17,   # 5 PM
            "timezone": "UTC"
        })
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Tasks to schedule"
                },
                "schedule_config": {
                    "type": "object",
                    "description": "Scheduling configuration"
                },
                "working_hours": {
                    "type": "object",
                    "description": "Working hours configuration"
                },
                "blackout_dates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dates when no tasks should be scheduled"
                }
            },
            "required": ["tasks"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "scheduled_tasks": {"type": "array"},
                        "schedule_conflicts": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the task scheduling skill"""
        try:
            tasks = kwargs.get("tasks", [])
            schedule_config = kwargs.get("schedule_config", {})
            working_hours = kwargs.get("working_hours", self.working_hours)
            blackout_dates = kwargs.get("blackout_dates", [])
            
            if not tasks:
                return {"success": True, "data": {
                    "scheduled_tasks": [],
                    "schedule_conflicts": [],
                    "recommendations": ["No tasks to schedule"]
                }, "error": None}
            
            # Sort tasks by priority
            sorted_tasks = self._sort_by_priority(tasks)
            
            # Schedule tasks
            scheduled = self._schedule_tasks(sorted_tasks, working_hours, blackout_dates)
            
            # Find conflicts
            conflicts = self._find_conflicts(scheduled)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scheduled, conflicts)
            
            result = {
                "scheduled_tasks": scheduled,
                "schedule_conflicts": conflicts,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "schedule_tasks",
                "task_count": len(tasks),
                "scheduled_count": len(scheduled),
                "conflict_count": len(conflicts),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error scheduling tasks: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _sort_by_priority(self, tasks: List[Dict]) -> List[Dict]:
        """Sort tasks by priority"""
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        return sorted(tasks, key=lambda t: priority_order.get(t.get("priority", "normal"), 2))
    
    def _schedule_tasks(
        self,
        tasks: List[Dict],
        working_hours: Dict,
        blackout_dates: List[str]
    ) -> List[Dict]:
        """Schedule tasks within working hours"""
        scheduled = []
        current_time = datetime.now()
        
        # Parse blackout dates
        blackout_set = set(blackout_dates)
        
        for task in tasks:
            # Find next available slot
            slot = self._find_next_available_slot(
                current_time, working_hours, blackout_set, task
            )
            
            task_copy = task.copy()
            task_copy["scheduled_time"] = slot.isoformat()
            task_copy["scheduled_date"] = slot.strftime("%Y-%m-%d")
            task_copy["scheduled_time_only"] = slot.strftime("%H:%M")
            task_copy["status"] = "scheduled"
            
            scheduled.append(task_copy)
            
            # Move current time forward
            duration = task.get("estimated_duration", 30)  # minutes
            current_time = slot + timedelta(minutes=duration)
        
        return scheduled
    
    def _find_next_available_slot(
        self,
        current_time: datetime,
        working_hours: Dict,
        blackout_dates: set,
        task: Dict
    ) -> datetime:
        """Find next available time slot"""
        slot = current_time
        
        # Check if current time is within working hours
        while True:
            # Skip blackout dates
            if slot.strftime("%Y-%m-%d") in blackout_dates:
                slot = slot.replace(hour=working_hours["start"], minute=0, second=0) + timedelta(days=1)
                continue
            
            # Check if within working hours
            if slot.hour < working_hours["start"]:
                slot = slot.replace(hour=working_hours["start"], minute=0, second=0)
            elif slot.hour >= working_hours["end"]:
                slot = slot.replace(hour=working_hours["start"], minute=0, second=0) + timedelta(days=1)
                continue
            
            # Check if weekend (optional)
            if slot.weekday() >= 5:  # Saturday or Sunday
                slot = slot.replace(hour=working_hours["start"], minute=0, second=0)
                days_to_monday = 7 - slot.weekday()
                slot += timedelta(days=days_to_monday)
                continue
            
            break
        
        return slot
    
    def _find_conflicts(self, scheduled: List[Dict]) -> List[Dict]:
        """Find scheduling conflicts"""
        conflicts = []
        seen_times = {}
        
        for task in scheduled:
            time_key = task.get("scheduled_time", "")
            if time_key in seen_times:
                conflicts.append({
                    "task1": seen_times[time_key],
                    "task2": task.get("title", "Unknown"),
                    "time": time_key,
                    "type": "time_conflict"
                })
            seen_times[time_key] = task.get("title", "Unknown")
        
        return conflicts
    
    def _generate_recommendations(self, scheduled: List[Dict], conflicts: List[Dict]) -> List[str]:
        """Generate scheduling recommendations"""
        recommendations = []
        
        if not scheduled:
            return ["No tasks scheduled"]
        
        if conflicts:
            recommendations.append(f"Found {len(conflicts)} scheduling conflicts. Consider rescheduling.")
        
        # Check for overloaded days
        day_counts = {}
        for task in scheduled:
            day = task.get("scheduled_date", "")
            day_counts[day] = day_counts.get(day, 0) + 1
        
        for day, count in day_counts.items():
            if count > 10:
                recommendations.append(f"Day {day} has {count} tasks. Consider spreading out.")
        
        # Check for high-priority tasks
        high_priority = [t for t in scheduled if t.get("priority") in ["critical", "high"]]
        if high_priority:
            recommendations.append(f"{len(high_priority)} high-priority tasks scheduled. Ensure adequate time.")
        
        return recommendations


class DecisionEngineSkill(BaseSkill):
    """
    Skill: decision_engine
    
    Makes autonomous decisions about task handling based on rules and context.
    
    Input:
        - task: dict - Task to make decision about
        - rules: list - Decision rules from Company Handbook
        - context: dict - Current context (business goals, recent activity, etc.)
        - auto_approve_threshold: dict - Thresholds for auto-approval
    
    Output:
        - success: bool
        - data: dict containing:
            - decision: str (execute, approve, defer, reject)
            - confidence: float (0-1)
            - reasoning: list of reasons
            - required_actions: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="decision_engine",
            description="Make autonomous decisions about task handling",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        # Load decision rules from config or handbook
        self.rules = self.config.get("rules", [])
        self.auto_approve_threshold = self.config.get("auto_approve_threshold", {
            "payment_amount": 50,
            "email_recipients": 5,
            "social_posts_per_day": 3
        })
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "object",
                    "description": "Task to make decision about"
                },
                "rules": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Decision rules"
                },
                "context": {
                    "type": "object",
                    "description": "Current context"
                },
                "auto_approve_threshold": {
                    "type": "object",
                    "description": "Thresholds for auto-approval"
                }
            },
            "required": ["task"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "array"},
                        "required_actions": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the decision engine skill"""
        try:
            task = kwargs.get("task", {})
            rules = kwargs.get("rules", self.rules)
            context = kwargs.get("context", {})
            auto_approve_threshold = kwargs.get("auto_approve_threshold", self.auto_approve_threshold)
            
            if not task:
                raise SkillExecutionError("task is required")
            
            # Analyze task
            task_analysis = self._analyze_task(task)
            
            # Apply rules
            rule_matches = self._apply_rules(task, rules, context)
            
            # Check thresholds
            threshold_check = self._check_thresholds(task, auto_approve_threshold)
            
            # Make decision
            decision, confidence, reasoning = self._make_decision(
                task_analysis, rule_matches, threshold_check, context
            )
            
            # Determine required actions
            required_actions = self._determine_actions(decision, task)
            
            result = {
                "decision": decision,
                "confidence": confidence,
                "reasoning": reasoning,
                "required_actions": required_actions,
                "task_analysis": task_analysis,
                "rule_matches": rule_matches,
                "timestamp": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "make_decision",
                "task_title": task.get("title", ""),
                "decision": decision,
                "confidence": confidence,
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error in decision engine: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _analyze_task(self, task: Dict) -> Dict:
        """Analyze task characteristics"""
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()
        text = f"{title} {description}"
        
        analysis = {
            "type": self._determine_task_type(task),
            "urgency": self._determine_urgency(task),
            "complexity": self._determine_complexity(task),
            "risk_level": self._determine_risk_level(task),
            "requires_human": self._check_human_requirement(task)
        }
        
        return analysis
    
    def _determine_task_type(self, task: Dict) -> str:
        """Determine task type"""
        title = task.get("title", "").lower()
        
        types = {
            "communication": ["email", "message", "reply", "call"],
            "finance": ["payment", "invoice", "bill", "transfer"],
            "social": ["post", "linkedin", "tweet", "facebook"],
            "admin": ["document", "file", "organize", "update"]
        }
        
        for task_type, keywords in types.items():
            if any(kw in title for kw in keywords):
                return task_type
        
        return "general"
    
    def _determine_urgency(self, task: Dict) -> str:
        """Determine task urgency"""
        title = task.get("title", "").lower()
        priority = task.get("priority", "normal")
        
        if priority == "critical" or any(kw in title for kw in ["urgent", "asap", "emergency"]):
            return "critical"
        elif priority == "high" or "deadline" in task:
            return "high"
        elif priority == "low":
            return "low"
        
        return "normal"
    
    def _determine_complexity(self, task: Dict) -> str:
        """Determine task complexity"""
        # Simple heuristic based on description length and keywords
        description = task.get("description", "")
        
        if len(description) > 500 or any(kw in description.lower() for kw in ["complex", "multiple", "coordinate"]):
            return "high"
        elif len(description) > 200:
            return "medium"
        
        return "low"
    
    def _determine_risk_level(self, task: Dict) -> str:
        """Determine risk level"""
        title = task.get("title", "").lower()
        
        high_risk_keywords = ["payment", "transfer", "delete", "send", "approve", "contract"]
        medium_risk_keywords = ["email", "post", "schedule", "update"]
        
        if any(kw in title for kw in high_risk_keywords):
            return "high"
        elif any(kw in title for kw in medium_risk_keywords):
            return "medium"
        
        return "low"
    
    def _check_human_requirement(self, task: Dict) -> bool:
        """Check if task requires human intervention"""
        # Tasks that always require human input
        always_human = ["contract", "legal", "agreement", "terms"]
        title = task.get("title", "").lower()
        
        return any(kw in title for kw in always_human)
    
    def _apply_rules(self, task: Dict, rules: List[Dict], context: Dict) -> List[Dict]:
        """Apply decision rules"""
        matches = []
        
        for rule in rules:
            if self._rule_matches(task, rule, context):
                matches.append(rule)
        
        return matches
    
    def _rule_matches(self, task: Dict, rule: Dict, context: Dict) -> bool:
        """Check if a rule matches the task"""
        conditions = rule.get("conditions", {})
        
        # Check priority condition
        if "priority" in conditions:
            if task.get("priority") not in conditions["priority"]:
                return False
        
        # Check type condition
        if "type" in conditions:
            task_type = self._determine_task_type(task)
            if task_type not in conditions["type"]:
                return False
        
        # Check amount condition (for payments)
        if "max_amount" in conditions:
            amount = task.get("amount", 0)
            if amount > conditions["max_amount"]:
                return False
        
        return True
    
    def _check_thresholds(self, task: Dict, thresholds: Dict) -> Dict:
        """Check auto-approval thresholds"""
        results = {
            "within_threshold": True,
            "violations": []
        }
        
        # Check payment amount
        if "amount" in task:
            if task["amount"] > thresholds.get("payment_amount", 50):
                results["within_threshold"] = False
                results["violations"].append(f"Amount ${task['amount']} exceeds threshold")
        
        return results
    
    def _make_decision(
        self,
        task_analysis: Dict,
        rule_matches: List[Dict],
        threshold_check: Dict,
        context: Dict
    ) -> tuple:
        """Make final decision"""
        reasoning = []
        confidence = 0.5
        
        # Default decision
        decision = "execute"
        
        # Check if human required
        if task_analysis.get("requires_human"):
            decision = "approve"
            reasoning.append("Task requires human intervention")
            confidence += 0.3
        
        # Check risk level
        if task_analysis.get("risk_level") == "high":
            decision = "approve"
            reasoning.append("High risk task requires approval")
            confidence += 0.2
        
        # Check thresholds
        if not threshold_check.get("within_threshold", True):
            decision = "approve"
            reasoning.extend(threshold_check.get("violations", []))
            confidence += 0.2
        
        # Check rules
        for rule in rule_matches:
            if rule.get("action") == "require_approval":
                decision = "approve"
                reasoning.append(f"Rule matched: {rule.get('name', 'unnamed')}")
                confidence += 0.1
            elif rule.get("action") == "defer":
                decision = "defer"
                reasoning.append(f"Rule matched: {rule.get('name', 'unnamed')}")
        
        # Check urgency
        if task_analysis.get("urgency") == "critical":
            if decision != "approve":  # Don't auto-approve critical tasks
                decision = "execute"
                reasoning.append("Critical urgency - immediate execution")
            confidence += 0.2
        
        # Cap confidence
        confidence = min(confidence, 1.0)
        
        return decision, confidence, reasoning
    
    def _determine_actions(self, decision: str, task: Dict) -> List[str]:
        """Determine required actions based on decision"""
        actions = []
        
        if decision == "execute":
            actions = ["Proceed with task execution", "Log execution details"]
        elif decision == "approve":
            actions = ["Create approval request", "Wait for human decision", "Notify requester"]
        elif decision == "defer":
            actions = ["Schedule for later", "Add to backlog", "Set reminder"]
        elif decision == "reject":
            actions = ["Document rejection reason", "Notify requester", "Archive task"]
        
        return actions


class ActionExecutorSkill(BaseSkill):
    """
    Skill: action_executor
    
    Executes approved actions using available tools and MCP servers.
    
    Input:
        - action: dict - Action to execute
        - tools: list - Available tools/MCP servers
        - dry_run: bool - If True, don't actually execute
        - timeout: int - Execution timeout in seconds
    
    Output:
        - success: bool
        - data: dict containing:
            - execution_id: str
            - action_result: dict
            - execution_time: float
            - logs: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="action_executor",
            description="Execute approved actions using available tools",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.dry_run = self.config.get("dry_run", False)
        self.timeout = self.config.get("timeout", 300)  # 5 minutes
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "object",
                    "description": "Action to execute"
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Available tools/MCP servers"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If True, don't actually execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds"
                }
            },
            "required": ["action"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string"},
                        "action_result": {"type": "object"},
                        "execution_time": {"type": "number"},
                        "logs": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the action executor skill"""
        import time
        
        start_time = time.time()
        
        try:
            action = kwargs.get("action", {})
            tools = kwargs.get("tools", [])
            dry_run = kwargs.get("dry_run", self.dry_run)
            timeout = kwargs.get("timeout", self.timeout)
            
            if not action:
                raise SkillExecutionError("action is required")
            
            # Generate execution ID
            execution_id = f"EXEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Validate action has approval
            if not action.get("approved", False) and not dry_run:
                raise SkillExecutionError("Action not approved")
            
            # Execute action
            logs = []
            logs.append(f"Starting execution: {action.get('type', 'unknown')}")
            
            if dry_run:
                logs.append("[DRY RUN] Action would be executed")
                result = {"status": "dry_run", "message": "Action not executed (dry run mode)"}
            else:
                result = self._execute_action(action, tools, logs, timeout)
            
            execution_time = time.time() - start_time
            
            result_data = {
                "execution_id": execution_id,
                "action_result": result,
                "execution_time": round(execution_time, 2),
                "logs": logs,
                "executed_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "execute_action",
                "execution_id": execution_id,
                "action_type": action.get("type", ""),
                "execution_time": execution_time,
                "result": "success" if result.get("status") == "success" else "failed",
                "success": True
            })
            
            return {"success": True, "data": result_data, "error": None}
            
        except Exception as e:
            error_msg = f"Error executing action: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _execute_action(
        self,
        action: Dict,
        tools: List[str],
        logs: List[str],
        timeout: int
    ) -> Dict:
        """Execute the actual action"""
        action_type = action.get("type", "unknown")
        
        logs.append(f"Executing action type: {action_type}")
        
        # Route to appropriate executor based on action type
        executors = {
            "email_send": self._execute_email,
            "email_draft": self._execute_email_draft,
            "social_post": self._execute_social_post,
            "file_move": self._execute_file_move,
            "file_create": self._execute_file_create,
            "web_navigate": self._execute_web_navigate,
            "payment": self._execute_payment,
        }
        
        executor = executors.get(action_type, self._execute_generic)
        
        try:
            result = executor(action, logs)
            result["status"] = "success"
        except Exception as e:
            logs.append(f"Execution error: {str(e)}")
            result = {"status": "failed", "error": str(e)}
        
        return result
    
    def _execute_email(self, action: Dict, logs: List[str]) -> Dict:
        """Execute email send action"""
        logs.append(f"Sending email to: {action.get('to', 'unknown')}")
        
        if self.dry_run:
            return {"message": "Email would be sent"}
        
        # In production, this would call Email MCP server
        # For now, return simulated result
        return {"message": "Email sent successfully", "message_id": uuid.uuid4().hex}
    
    def _execute_email_draft(self, action: Dict, logs: List[str]) -> Dict:
        """Execute email draft action"""
        logs.append(f"Creating email draft to: {action.get('to', 'unknown')}")
        return {"message": "Draft created", "draft_id": uuid.uuid4().hex}
    
    def _execute_social_post(self, action: Dict, logs: List[str]) -> Dict:
        """Execute social media post action"""
        platform = action.get("platform", "unknown")
        logs.append(f"Posting to {platform}: {action.get('content', '')[:50]}...")
        
        if self.dry_run:
            return {"message": f"Post to {platform} would be published"}
        
        return {"message": f"Posted to {platform}", "post_id": uuid.uuid4().hex}
    
    def _execute_file_move(self, action: Dict, logs: List[str]) -> Dict:
        """Execute file move action"""
        source = action.get("source")
        dest = action.get("destination")
        logs.append(f"Moving file from {source} to {dest}")
        
        if not source or not dest:
            raise SkillExecutionError("source and destination required")
        
        if self.dry_run:
            return {"message": f"File would be moved from {source} to {dest}"}
        
        if self.vault_path:
            src_path = self.vault_path / source
            dest_path = self.vault_path / dest
            
            if src_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                src_path.rename(dest_path)
                return {"message": "File moved successfully"}
        
        return {"message": "File move simulated"}
    
    def _execute_file_create(self, action: Dict, logs: List[str]) -> Dict:
        """Execute file create action"""
        filepath = action.get("path")
        content = action.get("content", "")
        logs.append(f"Creating file: {filepath}")
        
        if self.dry_run:
            return {"message": f"File would be created: {filepath}"}
        
        if self.vault_path and filepath:
            full_path = self.vault_path / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return {"message": "File created successfully", "path": str(full_path)}
        
        return {"message": "File creation simulated"}
    
    def _execute_web_navigate(self, action: Dict, logs: List[str]) -> Dict:
        """Execute web navigation action"""
        url = action.get("url")
        logs.append(f"Navigating to: {url}")
        
        if self.dry_run:
            return {"message": f"Would navigate to: {url}"}
        
        # In production, this would use browser MCP
        return {"message": "Navigation simulated", "url": url}
    
    def _execute_payment(self, action: Dict, logs: List[str]) -> Dict:
        """Execute payment action"""
        amount = action.get("amount")
        recipient = action.get("recipient")
        logs.append(f"Processing payment: ${amount} to {recipient}")
        
        if self.dry_run:
            return {"message": f"Payment of ${amount} to {recipient} would be processed"}
        
        # In production, this would call banking MCP
        return {"message": "Payment processed", "transaction_id": uuid.uuid4().hex}
    
    def _execute_generic(self, action: Dict, logs: List[str]) -> Dict:
        """Execute generic action"""
        logs.append(f"Executing generic action: {action.get('type', 'unknown')}")
        
        if self.dry_run:
            return {"message": "Action would be executed"}
        
        return {"message": "Action executed", "action_id": uuid.uuid4().hex}


class ProgressTrackerSkill(BaseSkill):
    """
    Skill: progress_tracker
    
    Tracks progress of tasks and plans, updating status and generating reports.
    
    Input:
        - task_ids: list - Task IDs to track
        - plan_id: str - Plan ID to track
        - update_type: str - Type of update (start, progress, complete)
        - progress_data: dict - Progress information
    
    Output:
        - success: bool
        - data: dict containing:
            - tracked_items: list
            - overall_progress: float
            - status_summary: dict
            - recommendations: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="progress_tracker",
            description="Track progress of tasks and plans",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Task IDs to track"
                },
                "plan_id": {
                    "type": "string",
                    "description": "Plan ID to track"
                },
                "update_type": {
                    "type": "string",
                    "description": "Type of update",
                    "enum": ["start", "progress", "complete", "status"]
                },
                "progress_data": {
                    "type": "object",
                    "description": "Progress information"
                }
            },
            "required": []
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "tracked_items": {"type": "array"},
                        "overall_progress": {"type": "number"},
                        "status_summary": {"type": "object"},
                        "recommendations": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the progress tracker skill"""
        try:
            task_ids = kwargs.get("task_ids", [])
            plan_id = kwargs.get("plan_id")
            update_type = kwargs.get("update_type", "status")
            progress_data = kwargs.get("progress_data", {})
            
            # Track tasks
            tracked_tasks = []
            if task_ids:
                tracked_tasks = self._track_tasks(task_ids, update_type, progress_data)
            
            # Track plan
            plan_progress = None
            if plan_id:
                plan_progress = self._track_plan(plan_id, update_type, progress_data)
            
            # Calculate overall progress
            overall_progress = self._calculate_overall_progress(tracked_tasks, plan_progress)
            
            # Generate status summary
            status_summary = self._generate_status_summary(tracked_tasks, plan_progress)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(tracked_tasks, overall_progress)
            
            result = {
                "tracked_items": tracked_tasks,
                "plan_progress": plan_progress,
                "overall_progress": overall_progress,
                "status_summary": status_summary,
                "recommendations": recommendations,
                "tracked_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "track_progress",
                "task_count": len(tracked_tasks),
                "plan_id": plan_id,
                "overall_progress": overall_progress,
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error tracking progress: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _track_tasks(self, task_ids: List[str], update_type: str, progress_data: Dict) -> List[Dict]:
        """Track multiple tasks"""
        tracked = []
        
        for task_id in task_ids:
            task_info = self._get_task_info(task_id)
            
            if update_type == "start":
                task_info["status"] = "in_progress"
                task_info["started_at"] = datetime.now().isoformat()
            elif update_type == "progress":
                task_info["progress_percent"] = progress_data.get("percent", 0)
                task_info["last_updated"] = datetime.now().isoformat()
            elif update_type == "complete":
                task_info["status"] = "completed"
                task_info["completed_at"] = datetime.now().isoformat()
                task_info["progress_percent"] = 100
            
            tracked.append(task_info)
            
            # Update task file if vault path exists
            if self.vault_path:
                self._update_task_file(task_id, task_info)
        
        return tracked
    
    def _track_plan(self, plan_id: str, update_type: str, progress_data: Dict) -> Dict:
        """Track a plan"""
        plan_info = self._get_plan_info(plan_id)
        
        if update_type == "start":
            plan_info["status"] = "active"
            plan_info["started_at"] = datetime.now().isoformat()
        elif update_type == "progress":
            steps_complete = progress_data.get("steps_complete", [])
            plan_info["completed_steps"] = steps_complete
            plan_info["progress_percent"] = len(steps_complete) / max(len(plan_info.get("steps", [])), 1) * 100
        elif update_type == "complete":
            plan_info["status"] = "completed"
            plan_info["completed_at"] = datetime.now().isoformat()
            plan_info["progress_percent"] = 100
        
        # Update plan file
        if self.vault_path:
            self._update_plan_file(plan_id, plan_info)
        
        return plan_info
    
    def _get_task_info(self, task_id: str) -> Dict:
        """Get task information"""
        # In production, this would read from vault
        return {
            "task_id": task_id,
            "status": "pending",
            "progress_percent": 0
        }
    
    def _get_plan_info(self, plan_id: str) -> Dict:
        """Get plan information"""
        # In production, this would read from vault
        return {
            "plan_id": plan_id,
            "status": "planned",
            "steps": [],
            "completed_steps": [],
            "progress_percent": 0
        }
    
    def _calculate_overall_progress(self, tasks: List[Dict], plan: Dict) -> float:
        """Calculate overall progress"""
        total = 0
        count = 0
        
        for task in tasks:
            total += task.get("progress_percent", 0)
            count += 1
        
        if plan:
            total += plan.get("progress_percent", 0)
            count += 1
        
        return round(total / max(count, 1), 2)
    
    def _generate_status_summary(self, tasks: List[Dict], plan: Dict) -> Dict:
        """Generate status summary"""
        summary = {
            "total_tasks": len(tasks),
            "completed": sum(1 for t in tasks if t.get("status") == "completed"),
            "in_progress": sum(1 for t in tasks if t.get("status") == "in_progress"),
            "pending": sum(1 for t in tasks if t.get("status") == "pending"),
            "plan_status": plan.get("status") if plan else None
        }
        return summary
    
    def _generate_recommendations(self, tasks: List[Dict], overall_progress: float) -> List[str]:
        """Generate progress recommendations"""
        recommendations = []
        
        if not tasks:
            return ["No tasks being tracked"]
        
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        if pending > len(tasks) / 2:
            recommendations.append(f"{pending} tasks are pending. Consider starting some.")
        
        if overall_progress < 50:
            recommendations.append("Overall progress is below 50%. Focus on completing tasks.")
        
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
        if in_progress > 5:
            recommendations.append(f"{in_progress} tasks in progress. Consider focusing on fewer tasks.")
        
        return recommendations
    
    def _update_task_file(self, task_id: str, task_info: Dict) -> None:
        """Update task file in vault"""
        if not self.vault_path:
            return
        
        # Find task file
        needs_action = self.vault_path / "Needs_Action"
        done = self.vault_path / "Done"
        
        for folder in [needs_action, done]:
            for file in folder.glob(f"*{task_id}*.md"):
                # Read and update frontmatter
                content = file.read_text(encoding='utf-8')
                
                # Update status in content
                if task_info.get("status") == "completed":
                    content = content.replace("status: pending", "status: completed")
                    # Move to Done folder
                    dest = done / file.name
                    if dest != file:
                        file.rename(dest)
                
                file.write_text(content, encoding='utf-8')
                break
    
    def _update_plan_file(self, plan_id: str, plan_info: Dict) -> None:
        """Update plan file in vault"""
        if not self.vault_path:
            return
        
        plans_folder = self.vault_path / "Plans"
        
        for file in plans_folder.glob(f"*{plan_id}*.md"):
            content = file.read_text(encoding='utf-8')
            
            # Update status
            if "status:" in content:
                content = re.sub(
                    r'status: \w+',
                    f'status: {plan_info.get("status", "planned")}',
                    content
                )
            
            file.write_text(content, encoding='utf-8')


# Export all execution skills
__all__ = [
    "TaskCreationSkill",
    "TaskSchedulingSkill",
    "DecisionEngineSkill",
    "ActionExecutorSkill",
    "ProgressTrackerSkill"
]
