"""
AI Employee Skills Package

A modular skill system for building autonomous AI employees.
Silver Tier Implementation - Personal AI Employee Hackathon 0

This package provides a comprehensive set of skills organized into layers:
- Core: Base classes and system skills
- Perception: Watcher skills for monitoring external sources
- Action: Execution skills for autonomous task handling
- Integration: Vault/memory management skills
"""

__version__ = "1.0.0"
__author__ = "AI Employee Hackathon Contributors"
__description__ = "Modular skill system for autonomous AI employees"

# Import all skill modules
from .core.base_skill import (
    BaseSkill,
    SkillError,
    SkillConfigurationError,
    SkillExecutionError
)

from .core.system_skills import (
    ReadMarkdownFileSkill,
    ParseHackathonRequirementsSkill,
    TaskExtractorSkill,
    TaskPrioritizerSkill,
    ExecutionPlannerSkill
)

from .perception.watcher_skills import (
    GoogleWatcherSkill,
    LinkedInWatcherSkill,
    WhatsAppWatcherSkill
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

# Registry of all available skills
SKILL_REGISTRY = {
    # System Skills
    "read_markdown_file": ReadMarkdownFileSkill,
    "parse_hackathon_requirements": ParseHackathonRequirementsSkill,
    "task_extractor": TaskExtractorSkill,
    "task_prioritizer": TaskPrioritizerSkill,
    "execution_planner": ExecutionPlannerSkill,
    
    # Watcher Skills
    "google_watcher_skill": GoogleWatcherSkill,
    "linkedin_watcher_skill": LinkedInWatcherSkill,
    "whatsapp_watcher_skill": WhatsAppWatcherSkill,
    
    # Execution Skills
    "task_creation": TaskCreationSkill,
    "task_scheduling": TaskSchedulingSkill,
    "decision_engine": DecisionEngineSkill,
    "action_executor": ActionExecutorSkill,
    "progress_tracker": ProgressTrackerSkill,
    
    # Vault Skills
    "read_vault_tasks": ReadVaultTasksSkill,
    "write_vault_tasks": WriteVaultTasksSkill,
    "update_task_status": UpdateTaskStatusSkill,
    "log_agent_activity": LogAgentActivitySkill,
}

# Skill categories for organization
SKILL_CATEGORIES = {
    "system": [
        "read_markdown_file",
        "parse_hackathon_requirements",
        "task_extractor",
        "task_prioritizer",
        "execution_planner"
    ],
    "perception": [
        "google_watcher_skill",
        "linkedin_watcher_skill",
        "whatsapp_watcher_skill"
    ],
    "action": [
        "task_creation",
        "task_scheduling",
        "decision_engine",
        "action_executor",
        "progress_tracker"
    ],
    "integration": [
        "read_vault_tasks",
        "write_vault_tasks",
        "update_task_status",
        "log_agent_activity"
    ]
}


def get_skill(skill_name: str, **kwargs):
    """
    Factory function to create skill instances.
    
    Args:
        skill_name: Name of the skill to create
        **kwargs: Arguments to pass to skill constructor
    
    Returns:
        Instantiated skill object
    
    Raises:
        ValueError: If skill name is not found
    """
    if skill_name not in SKILL_REGISTRY:
        available = ", ".join(SKILL_REGISTRY.keys())
        raise ValueError(f"Unknown skill: {skill_name}. Available: {available}")
    
    skill_class = SKILL_REGISTRY[skill_name]
    return skill_class(**kwargs)


def list_skills(category: str = None) -> list:
    """
    List available skills, optionally filtered by category.
    
    Args:
        category: Optional category filter (system, perception, action, integration)
    
    Returns:
        List of skill names
    """
    if category:
        return SKILL_CATEGORIES.get(category, [])
    return list(SKILL_REGISTRY.keys())


def get_skill_info(skill_name: str) -> dict:
    """
    Get information about a skill.
    
    Args:
        skill_name: Name of the skill
    
    Returns:
        Dictionary with skill information
    """
    if skill_name not in SKILL_REGISTRY:
        return {"error": f"Unknown skill: {skill_name}"}
    
    # Create instance to get schema
    try:
        skill = SKILL_REGISTRY[skill_name]()
        return {
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
            "schema": skill.get_schema(),
            "category": _get_skill_category(skill_name)
        }
    except Exception as e:
        return {"error": str(e)}


def _get_skill_category(skill_name: str) -> str:
    """Get category for a skill name"""
    for category, skills in SKILL_CATEGORIES.items():
        if skill_name in skills:
            return category
    return "unknown"


__all__ = [
    # Version info
    "__version__",
    
    # Base classes
    "BaseSkill",
    "SkillError",
    "SkillConfigurationError",
    "SkillExecutionError",
    
    # All skill classes
    "ReadMarkdownFileSkill",
    "ParseHackathonRequirementsSkill",
    "TaskExtractorSkill",
    "TaskPrioritizerSkill",
    "ExecutionPlannerSkill",
    "GoogleWatcherSkill",
    "LinkedInWatcherSkill",
    "WhatsAppWatcherSkill",
    "TaskCreationSkill",
    "TaskSchedulingSkill",
    "DecisionEngineSkill",
    "ActionExecutorSkill",
    "ProgressTrackerSkill",
    "ReadVaultTasksSkill",
    "WriteVaultTasksSkill",
    "UpdateTaskStatusSkill",
    "LogAgentActivitySkill",
    
    # Registry and utilities
    "SKILL_REGISTRY",
    "SKILL_CATEGORIES",
    "get_skill",
    "list_skills",
    "get_skill_info",
]
