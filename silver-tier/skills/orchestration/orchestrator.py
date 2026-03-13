"""
Skill Orchestrator - Coordinates all AI Employee Skills

This module provides the orchestration layer that coordinates all skills,
manages workflows, and handles the Perception → Reasoning → Action cycle.

Silver Tier Implementation - Personal AI Employee Hackathon 0
"""

from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from datetime import datetime
import json
import logging
import time

from .core.base_skill import BaseSkill, SkillExecutionError
from .core.system_skills import (
    TaskExtractorSkill,
    TaskPrioritizerSkill,
    ExecutionPlannerSkill
)
from .perception.watcher_skills import (
    WhatsAppWatcherSkill,
    LinkedInWatcherSkill,
    GoogleWatcherSkill
)
from .action.execution_skills import (
    TaskCreationSkill,
    TaskSchedulingSkill,
    DecisionEngineSkill,
    ActionExecutorSkill,
    ProgressTrackerSkill
)
from .integration.vault_skills import (
    ReadVaultTasksSkill,
    WriteVaultTasksSkill,
    UpdateTaskStatusSkill,
    LogAgentActivitySkill
)


class OrchestratorConfig:
    """Configuration for the orchestrator"""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        self.vault_path = Path(config_dict.get("vault_path", "")) if config_dict else None
        self.log_level = config_dict.get("log_level", "INFO") if config_dict else "INFO"
        self.check_interval = config_dict.get("check_interval", 60) if config_dict else 60
        self.max_tasks_per_cycle = config_dict.get("max_tasks_per_cycle", 10) if config_dict else 10
        self.auto_approve_threshold = config_dict.get("auto_approve_threshold", {}) if config_dict else {}
        self.enabled_watchers = config_dict.get("enabled_watchers", ["whatsapp", "linkedin"]) if config_dict else []
        self.dry_run = config_dict.get("dry_run", False) if config_dict else False


class SkillOrchestrator:
    """
    Main orchestrator for the AI Employee skill system.
    
    Coordinates the Perception → Reasoning → Action cycle:
    1. Perception: Run watchers to detect new tasks
    2. Reasoning: Extract, prioritize, and plan tasks
    3. Action: Execute approved actions
    
    Attributes:
        config: Orchestrator configuration
        vault_path: Path to Obsidian vault
        skills: Dictionary of initialized skills
        logger: Logger instance
    """
    
    def __init__(self, config: OrchestratorConfig = None):
        """
        Initialize the skill orchestrator.
        
        Args:
            config: Orchestrator configuration
        """
        self.config = config or OrchestratorConfig()
        self.vault_path = self.config.vault_path
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize skills
        self.skills = self._initialize_skills()
        
        # State tracking
        self.running = False
        self.cycle_count = 0
        self.tasks_processed = 0
        
        self.logger.info("Skill Orchestrator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("orchestrator")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_skills(self) -> Dict[str, BaseSkill]:
        """Initialize all skills with configuration"""
        vault_path_str = str(self.vault_path) if self.vault_path else None
        
        skills = {
            # System skills
            "task_extractor": TaskExtractorSkill(vault_path=vault_path_str),
            "task_prioritizer": TaskPrioritizerSkill(vault_path=vault_path_str),
            "execution_planner": ExecutionPlannerSkill(vault_path=vault_path_str),
            
            # Watcher skills
            "whatsapp_watcher": WhatsAppWatcherSkill(vault_path=vault_path_str),
            "linkedin_watcher": LinkedInWatcherSkill(vault_path=vault_path_str),
            "google_watcher": GoogleWatcherSkill(vault_path=vault_path_str),
            
            # Execution skills
            "task_creation": TaskCreationSkill(vault_path=vault_path_str),
            "task_scheduling": TaskSchedulingSkill(vault_path=vault_path_str),
            "decision_engine": DecisionEngineSkill(vault_path=vault_path_str),
            "action_executor": ActionExecutorSkill(
                vault_path=vault_path_str,
                config={"dry_run": self.config.dry_run}
            ),
            "progress_tracker": ProgressTrackerSkill(vault_path=vault_path_str),
            
            # Vault skills
            "read_vault_tasks": ReadVaultTasksSkill(vault_path=vault_path_str),
            "write_vault_tasks": WriteVaultTasksSkill(vault_path=vault_path_str),
            "update_task_status": UpdateTaskStatusSkill(vault_path=vault_path_str),
            "log_agent_activity": LogAgentActivitySkill(vault_path=vault_path_str),
        }
        
        self.logger.info(f"Initialized {len(skills)} skills")
        return skills
    
    def run_cycle(self) -> Dict[str, Any]:
        """
        Run one complete Perception → Reasoning → Action cycle.
        
        Returns:
            Dictionary with cycle results
        """
        self.cycle_count += 1
        cycle_start = datetime.now()
        
        self.logger.info(f"Starting cycle {self.cycle_count}")
        
        results = {
            "cycle": self.cycle_count,
            "start_time": cycle_start.isoformat(),
            "perception": {},
            "reasoning": {},
            "action": {},
            "tasks_processed": 0
        }
        
        try:
            # Phase 1: Perception - Run watchers
            self.logger.info("Phase 1: Perception")
            perception_results = self._run_perception()
            results["perception"] = perception_results
            
            # Phase 2: Reasoning - Process detected tasks
            self.logger.info("Phase 2: Reasoning")
            reasoning_results = self._run_reasoning(perception_results)
            results["reasoning"] = reasoning_results
            
            # Phase 3: Action - Execute approved actions
            self.logger.info("Phase 3: Action")
            action_results = self._run_action(reasoning_results)
            results["action"] = action_results
            results["tasks_processed"] = action_results.get("tasks_executed", 0)
            self.tasks_processed += results["tasks_processed"]
            
            # Log cycle completion
            cycle_end = datetime.now()
            duration = (cycle_end - cycle_start).total_seconds()
            results["end_time"] = cycle_end.isoformat()
            results["duration_seconds"] = duration
            
            self.logger.info(f"Cycle {self.cycle_count} completed in {duration:.2f}s")
            
            # Log activity
            self.skills["log_agent_activity"].execute(
                activity_type="orchestrator_cycle",
                activity_data={
                    "cycle": self.cycle_count,
                    "duration": duration,
                    "tasks_processed": results["tasks_processed"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Cycle failed: {str(e)}")
            results["error"] = str(e)
            
            # Log error
            self.skills["log_agent_activity"].execute(
                activity_type="orchestrator_error",
                activity_data={"cycle": self.cycle_count, "error": str(e)},
                log_level="ERROR"
            )
        
        return results
    
    def _run_perception(self) -> Dict[str, Any]:
        """Run all enabled watchers"""
        results = {
            "watchers_run": [],
            "items_detected": 0,
            "details": {}
        }
        
        for watcher_name in self.config.enabled_watchers:
            skill_name = f"{watcher_name}_watcher"
            if skill_name not in self.skills:
                continue
            
            try:
                self.logger.info(f"Running {skill_name}")
                watcher = self.skills[skill_name]
                watcher_result = watcher.execute()
                
                if watcher_result["success"]:
                    data = watcher_result.get("data", {})
                    items_count = data.get("new_messages", []) or data.get("new_items", [])
                    count = len(items_count) if isinstance(items_count, list) else 0
                    
                    results["watchers_run"].append(watcher_name)
                    results["items_detected"] += count
                    results["details"][watcher_name] = {
                        "success": True,
                        "items_count": count
                    }
                    
                    self.logger.info(f"{watcher_name} found {count} items")
                else:
                    results["details"][watcher_name] = {
                        "success": False,
                        "error": watcher_result.get("error")
                    }
                    
            except Exception as e:
                self.logger.error(f"{skill_name} failed: {str(e)}")
                results["details"][watcher_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def _run_reasoning(self, perception_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process detected tasks through reasoning pipeline"""
        results = {
            "tasks_extracted": 0,
            "tasks_prioritized": 0,
            "plans_created": 0,
            "tasks": []
        }
        
        # Read tasks from Needs_Action folder
        try:
            read_result = self.skills["read_vault_tasks"].execute(
                folder="Needs_Action",
                limit=self.config.max_tasks_per_cycle
            )
            
            if read_result["success"]:
                tasks = read_result.get("data", {}).get("tasks", [])
                results["tasks_extracted"] = len(tasks)
                results["tasks"] = tasks
                
                self.logger.info(f"Found {len(tasks)} tasks to process")
                
                # Prioritize tasks
                if tasks:
                    priority_result = self.skills["task_prioritizer"].execute(
                        tasks=tasks
                    )
                    
                    if priority_result["success"]:
                        priority_data = priority_result.get("data", {})
                        results["tasks_prioritized"] = len(priority_data.get("prioritized_tasks", []))
                        results["prioritized_tasks"] = priority_data.get("prioritized_tasks", [])
                        
                        # Create plans for high priority tasks
                        for task in results["prioritized_tasks"][:5]:  # Top 5
                            plan_result = self.skills["execution_planner"].execute(
                                task=task
                            )
                            
                            if plan_result["success"]:
                                results["plans_created"] += 1
                                
                                # Create plan file
                                plan_data = plan_result.get("data", {})
                                self.skills["write_vault_tasks"].execute(
                                    task_data={
                                        "title": f"Plan: {task.get('title', 'Untitled')}",
                                        "type": "plan",
                                        "plan_data": plan_data,
                                        "related_task": task.get("task_id")
                                    },
                                    folder="Plans"
                                )
            
        except Exception as e:
            self.logger.error(f"Reasoning failed: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    def _run_action(self, reasoning_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute approved actions"""
        results = {
            "tasks_executed": 0,
            "actions_taken": [],
            "approvals_requested": 0
        }
        
        prioritized_tasks = reasoning_results.get("prioritized_tasks", [])
        
        for task in prioritized_tasks:
            try:
                # Make decision about task
                decision_result = self.skills["decision_engine"].execute(
                    task=task
                )
                
                if not decision_result["success"]:
                    continue
                
                decision_data = decision_result.get("data", {})
                decision = decision_data.get("decision", "execute")
                
                if decision == "execute":
                    # Execute the task
                    action_result = self.skills["action_executor"].execute(
                        action={
                            "type": "task_execution",
                            "task": task,
                            "approved": True
                        }
                    )
                    
                    if action_result["success"]:
                        results["tasks_executed"] += 1
                        results["actions_taken"].append({
                            "task": task.get("title"),
                            "result": "success"
                        })
                        
                        # Update task status
                        if task.get("task_id"):
                            self.skills["update_task_status"].execute(
                                task_id=task.get("task_id"),
                                new_status="completed"
                            )
                
                elif decision == "approve":
                    # Create approval request
                    results["approvals_requested"] += 1
                    
                    self.skills["write_vault_tasks"].execute(
                        task_data={
                            "title": f"Approval: {task.get('title', 'Untitled')}",
                            "type": "approval_request",
                            "task": task,
                            "decision_reasoning": decision_data.get("reasoning", [])
                        },
                        folder="Pending_Approval"
                    )
                    
                    self.logger.info(f"Created approval request for: {task.get('title')}")
                
            except Exception as e:
                self.logger.error(f"Action execution failed: {str(e)}")
                results["actions_taken"].append({
                    "task": task.get("title"),
                    "result": "failed",
                    "error": str(e)
                })
        
        return results
    
    def run_continuous(self, callback: Callable = None) -> None:
        """
        Run orchestrator continuously in a loop.
        
        Args:
            callback: Optional callback function called after each cycle
        """
        self.running = True
        self.logger.info(f"Starting continuous mode (interval: {self.config.check_interval}s)")
        
        try:
            while self.running:
                results = self.run_cycle()
                
                if callback:
                    callback(results)
                
                # Wait for next cycle
                time.sleep(self.config.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Stopped by user")
            self.running = False
        except Exception as e:
            self.logger.error(f"Continuous mode failed: {str(e)}")
            self.running = False
    
    def stop(self) -> None:
        """Stop continuous execution"""
        self.running = False
        self.logger.info("Orchestrator stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "tasks_processed": self.tasks_processed,
            "vault_path": str(self.vault_path) if self.vault_path else None,
            "enabled_watchers": self.config.enabled_watchers,
            "dry_run": self.config.dry_run,
            "skills_loaded": list(self.skills.keys())
        }
    
    def run_workflow(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a predefined workflow.
        
        Args:
            workflow_name: Name of workflow to run
            input_data: Input data for workflow
        
        Returns:
            Workflow results
        """
        workflows = {
            "process_inbox": self._workflow_process_inbox,
            "daily_briefing": self._workflow_daily_briefing,
            "task_cleanup": self._workflow_task_cleanup,
        }
        
        if workflow_name not in workflows:
            return {"error": f"Unknown workflow: {workflow_name}"}
        
        self.logger.info(f"Running workflow: {workflow_name}")
        return workflows[workflow_name](input_data)
    
    def _workflow_process_inbox(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process all items in inbox"""
        results = {
            "workflow": "process_inbox",
            "steps": []
        }
        
        # Read inbox
        read_result = self.skills["read_vault_tasks"].execute(folder="Inbox")
        if not read_result["success"]:
            return {"error": "Failed to read inbox"}
        
        inbox_items = read_result.get("data", {}).get("tasks", [])
        results["steps"].append({"step": "read_inbox", "items_found": len(inbox_items)})
        
        # Process each item
        processed = 0
        for item in inbox_items:
            # Extract tasks from content
            content = item.get("body", "")
            extract_result = self.skills["task_extractor"].execute(
                content=content,
                source_type=item.get("type", "general")
            )
            
            if extract_result["success"]:
                extracted_tasks = extract_result.get("data", {}).get("tasks", [])
                
                # Create task files
                for task in extracted_tasks:
                    self.skills["task_creation"].execute(
                        task_data=task,
                        task_type=item.get("type", "general"),
                        folder="Needs_Action"
                    )
                    processed += 1
        
        results["steps"].append({"step": "create_tasks", "tasks_created": processed})
        results["total_processed"] = processed
        
        return results
    
    def _workflow_daily_briefing(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily briefing"""
        results = {
            "workflow": "daily_briefing",
            "briefing_data": {}
        }
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get tasks from different folders
        needs_action = self.skills["read_vault_tasks"].execute(
            folder="Needs_Action", limit=20
        )
        completed = self.skills["read_vault_tasks"].execute(
            folder="Done", limit=20
        )
        pending_approval = self.skills["read_vault_tasks"].execute(
            folder="Pending_Approval", limit=10
        )
        
        # Generate briefing content
        briefing = f"""---
date: {today}
type: daily_briefing
generated: {datetime.now().isoformat()}
---

# Daily Briefing - {today}

## Summary

### Needs Action
{needs_action.get('data', {}).get('total_count', 0)} tasks pending

### Completed Recently
{completed.get('data', {}).get('total_count', 0)} tasks done

### Awaiting Approval
{pending_approval.get('data', {}).get('total_count', 0)} items

## Priority Tasks
"""
        
        # Add priority tasks
        tasks = needs_action.get("data", {}).get("tasks", [])[:5]
        for task in tasks:
            briefing += f"- {task.get('title', 'Untitled')} ({task.get('priority', 'normal')})\n"
        
        briefing += "\n## Recommendations\n- Review pending approvals\n- Focus on high priority tasks\n"
        
        # Write briefing
        self.skills["write_vault_tasks"].execute(
            task_data={
                "title": f"Daily Briefing - {today}",
                "type": "briefing",
                "content": briefing
            },
            folder="Briefings"
        )
        
        results["briefing_data"] = {
            "date": today,
            "needs_action_count": needs_action.get("data", {}).get("total_count", 0),
            "completed_count": completed.get("data", {}).get("total_count", 0),
            "pending_approval_count": pending_approval.get("data", {}).get("total_count", 0)
        }
        
        return results
    
    def _workflow_task_cleanup(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old completed tasks"""
        results = {
            "workflow": "task_cleanup",
            "actions": []
        }
        
        days_old = input_data.get("days_old", 30)
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        # Get completed tasks
        done_result = self.skills["read_vault_tasks"].execute(
            folder="Done", limit=100
        )
        
        if not done_result["success"]:
            return {"error": "Failed to read Done folder"}
        
        tasks = done_result.get("data", {}).get("tasks", [])
        archived = 0
        
        for task in tasks:
            created = task.get("created")
            if created:
                try:
                    created_ts = datetime.fromisoformat(created).timestamp()
                    if created_ts < cutoff_date:
                        # Move to archive (could implement archive folder)
                        archived += 1
                        results["actions"].append({
                            "task": task.get("title"),
                            "action": "archive"
                        })
                except Exception:
                    pass
        
        results["archived_count"] = archived
        
        return results


def create_orchestrator(
    vault_path: str,
    enabled_watchers: List[str] = None,
    dry_run: bool = False,
    log_level: str = "INFO"
) -> SkillOrchestrator:
    """
    Factory function to create configured orchestrator.
    
    Args:
        vault_path: Path to Obsidian vault
        enabled_watchers: List of watchers to enable
        dry_run: If True, don't execute real actions
        log_level: Logging level
    
    Returns:
        Configured SkillOrchestrator instance
    """
    config = OrchestratorConfig({
        "vault_path": vault_path,
        "enabled_watchers": enabled_watchers or ["whatsapp", "linkedin"],
        "dry_run": dry_run,
        "log_level": log_level,
        "check_interval": 60,
        "max_tasks_per_cycle": 10
    })
    
    return SkillOrchestrator(config)


__all__ = [
    "OrchestratorConfig",
    "SkillOrchestrator",
    "create_orchestrator"
]
