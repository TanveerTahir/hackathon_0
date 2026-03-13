# AI Employee Skill System - Silver Tier

> **Modular, reusable skill architecture for autonomous AI employees**

A comprehensive implementation of the **Silver Tier** skill system for the Personal AI Employee Hackathon 0. This system provides a modular, composable architecture for building autonomous AI agents that can perceive, reason, and act on your behalf.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Skill Reference](#skill-reference)
- [Usage Examples](#usage-examples)
- [Orchestration](#orchestration)
- [Configuration](#configuration)
- [Development](#development)

---

## Overview

This skill system implements the **Perception → Reasoning → Action** architecture described in the hackathon document:

| Layer | Skills | Purpose |
|-------|--------|---------|
| **Perception** | Watchers | Monitor WhatsApp, LinkedIn, Google for new tasks |
| **Reasoning** | System Skills | Extract, prioritize, and plan tasks |
| **Action** | Execution Skills | Create, schedule, decide, execute, track |
| **Integration** | Vault Skills | Read/write tasks, update status, log activity |

### Silver Tier Coverage

All Silver Tier requirements are implemented:

- ✅ **Two or more Watcher scripts** (WhatsApp, LinkedIn, Google)
- ✅ **Qwen reasoning loop** (task_extractor, task_prioritizer, execution_planner)
- ✅ **Human-in-the-loop approval workflow** (decision_engine with approval logic)
- ✅ **Task scheduling** (task_scheduling skill)
- ✅ **All AI functionality as reusable skills** (17 modular skills)

---

## Architecture

### Folder Structure

```
skills/
├── __init__.py                 # Package root with skill registry
├── core/                       # Base classes and system skills
│   ├── __init__.py
│   ├── base_skill.py          # Abstract base class for all skills
│   └── system_skills.py       # System skills (5 skills)
├── perception/                 # Watcher skills
│   ├── __init__.py
│   └── watcher_skills.py      # Watcher skills (3 skills)
├── action/                     # Execution skills
│   ├── __init__.py
│   └── execution_skills.py    # Execution skills (5 skills)
├── integration/                # Vault/memory skills
│   ├── __init__.py
│   └── vault_skills.py        # Vault skills (4 skills)
└── orchestration/              # Coordination layer
    ├── __init__.py
    └── orchestrator.py        # Skill orchestrator
```

### Skill Architecture

Each skill follows a consistent pattern:

```python
from skills.core.base_skill import BaseSkill

class MySkill(BaseSkill):
    def __init__(self, vault_path=None, config=None):
        super().__init__(
            name="my_skill",
            description="Does something useful",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Skill logic here
        return {"success": True, "data": {...}, "error": None}
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                         │
│  WhatsAppWatcher → LinkedInWatcher → GoogleWatcher          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                          │
│  TaskExtractor → TaskPrioritizer → ExecutionPlanner         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      ACTION LAYER                           │
│  DecisionEngine → ActionExecutor → ProgressTracker          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                         │
│  ReadVaultTasks ←→ WriteVaultTasks ←→ UpdateTaskStatus      │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Obsidian vault (optional, for vault operations)
- pip or poetry for dependency management

### Setup Steps

1. **Clone or download the project**

2. **Install dependencies** (if any external packages needed):
   ```bash
   pip install pyyaml
   ```

3. **Add to Python path**:
   ```bash
   # Add to PYTHONPATH or install as package
   pip install -e .
   ```

4. **Verify installation**:
   ```python
   from skills import list_skills
   print(list_skills())
   ```

---

## Quick Start

### Basic Usage

```python
from skills import get_skill

# Create a skill instance
task_extractor = get_skill(
    "task_extractor",
    vault_path="D:/path/to/your/vault"
)

# Execute the skill
result = task_extractor.execute(
    content="Please send me the invoice ASAP",
    source_type="whatsapp"
)

if result["success"]:
    tasks = result["data"]["tasks"]
    print(f"Found {len(tasks)} tasks")
```

### Using the Orchestrator

```python
from skills.orchestration import create_orchestrator

# Create orchestrator
orchestrator = create_orchestrator(
    vault_path="D:/path/to/your/vault",
    enabled_watchers=["whatsapp", "linkedin"],
    dry_run=False
)

# Run one cycle
results = orchestrator.run_cycle()
print(f"Processed {results['tasks_processed']} tasks")

# Or run continuously
orchestrator.run_continuous()
```

---

## Skill Reference

### System Skills (Core)

| Skill | Description | Input | Output |
|-------|-------------|-------|--------|
| `read_markdown_file` | Read and parse Markdown files | file_path, include_content | frontmatter, content, metrics |
| `parse_hackathon_requirements` | Parse hackathon document | document_path, tier | requirements, deliverables |
| `task_extractor` | Extract tasks from text | content, source_type | tasks, confidence score |
| `task_prioritizer` | Prioritize tasks | tasks, business_goals | prioritized_tasks, distribution |
| `execution_planner` | Create execution plans | task, resources | plan with steps, duration |

### Watcher Skills (Perception)

| Skill | Description | Monitors | Creates |
|-------|-------------|----------|---------|
| `google_watcher_skill` | Google services monitoring | Alerts, Search, Gmail | Action files in Needs_Action |
| `linkedin_watcher_skill` | LinkedIn updates | Messages, Posts, Jobs | Message/Job action files |
| `whatsapp_watcher_skill` | WhatsApp Web messages | Keywords in messages | WhatsApp action files |

### Execution Skills (Action)

| Skill | Description | Handles | Output |
|-------|-------------|---------|--------|
| `task_creation` | Create task files | task_data, type | task_id, file_path |
| `task_scheduling` | Schedule tasks | tasks, working_hours | scheduled_tasks, conflicts |
| `decision_engine` | Make decisions | task, rules, context | decision, confidence |
| `action_executor` | Execute actions | action, tools | execution_result, logs |
| `progress_tracker` | Track progress | task_ids, plan_id | progress, recommendations |

### Vault Skills (Integration)

| Skill | Description | Operations | Folders |
|-------|-------------|------------|---------|
| `read_vault_tasks` | Read tasks from vault | filter, sort, limit | Any vault folder |
| `write_vault_tasks` | Create/update tasks | create, update, upsert | Any vault folder |
| `update_task_status` | Update status | status change, move | Auto-moves between folders |
| `log_agent_activity` | Log activities | activity_type, data | /Logs folder |

---

## Usage Examples

### Example 1: Extract Tasks from WhatsApp Message

```python
from skills import get_skill

# Initialize skill
extractor = get_skill(
    "task_extractor",
    vault_path="D:/MyVault"
)

# Extract tasks
result = extractor.execute(
    content="""
    Hi! Can you please send me the invoice for January? 
    Also, we need to schedule a meeting ASAP to discuss the project.
    """,
    source_type="whatsapp",
    priority_keywords=["urgent", "asap", "invoice"]
)

if result["success"]:
    for task in result["data"]["tasks"]:
        print(f"Task: {task['title']}")
        print(f"Priority: {task['priority']}")
```

### Example 2: Prioritize Tasks

```python
from skills import get_skill

prioritizer = get_skill("task_prioritizer")

tasks = [
    {"title": "Send invoice to Client A", "priority": "high"},
    {"title": "Schedule team meeting", "priority": "normal"},
    {"title": "Review quarterly report", "priority": "low"},
    {"title": "URGENT: Fix payment issue", "priority": "normal"}
]

result = prioritizer.execute(
    tasks=tasks,
    business_goals={"keywords": ["invoice", "payment", "revenue"]}
)

if result["success"]:
    for task in result["data"]["prioritized_tasks"]:
        print(f"{task['priority_level']}: {task['title']} (score: {task['priority_score']})")
```

### Example 3: Create Execution Plan

```python
from skills import get_skill

planner = get_skill("execution_planner")

task = {
    "title": "Send invoice to Client A",
    "description": "Generate and email invoice for January services",
    "priority": "high",
    "amount": 1500
}

result = planner.execute(
    task=task,
    available_resources=["email_mcp", "file_system"],
    constraints={"time_limit": "2 hours"}
)

if result["success"]:
    plan = result["data"]
    print(f"Plan ID: {plan['plan_id']}")
    print(f"Steps: {len(plan['steps'])}")
    for step in plan["steps"]:
        print(f"  {step['step_number']}. {step['title']}")
```

### Example 4: Make Decision About Task

```python
from skills import get_skill

decision_engine = get_skill(
    "decision_engine",
    config={
        "auto_approve_threshold": {
            "payment_amount": 100
        }
    }
)

task = {
    "title": "Send payment to vendor",
    "amount": 50,
    "priority": "normal"
}

result = decision_engine.execute(
    task=task,
    context={"business_goals": {"cost_control": True}}
)

if result["success"]:
    data = result["data"]
    print(f"Decision: {data['decision']}")
    print(f"Confidence: {data['confidence']}")
    print(f"Reasoning: {data['reasoning']}")
```

### Example 5: Read and Process Vault Tasks

```python
from skills import get_skill

reader = get_skill("read_vault_tasks", vault_path="D:/MyVault")

# Read high priority tasks
result = reader.execute(
    folder="Needs_Action",
    filters={"priority": ["high", "critical"]},
    sort_by="created",
    sort_order="desc",
    limit=10
)

if result["success"]:
    tasks = result["data"]["tasks"]
    print(f"Found {result['data']['total_count']} high priority tasks")
    for task in tasks:
        print(f"- {task['title']}")
```

### Example 6: Update Task Status

```python
from skills import get_skill

updater = get_skill("update_task_status", vault_path="D:/MyVault")

# Mark task as completed
result = updater.execute(
    task_id="TASK_20260107_123456",
    new_status="completed",
    additional_updates={"notes": "Completed successfully"}
)

if result["success"]:
    print(f"Task moved to: {result['data']['new_file_path']}")
    print(f"File moved: {result['data']['file_moved']}")
```

### Example 7: Log Agent Activity

```python
from skills import get_skill

logger = get_skill("log_agent_activity", vault_path="D:/MyVault")

# Log an action
result = logger.execute(
    activity_type="task_completed",
    activity_data={
        "task_id": "TASK_123",
        "task_title": "Send invoice",
        "duration_seconds": 45
    },
    agent_id="ai_employee_001",
    session_id="20260107_session"
)

if result["success"]:
    print(f"Logged: {result['data']['log_id']}")
```

---

## Orchestration

### The Orchestrator

The `SkillOrchestrator` coordinates all skills through the Perception → Reasoning → Action cycle:

```python
from skills.orchestration import create_orchestrator

orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    enabled_watchers=["whatsapp", "linkedin"],
    dry_run=False,
    log_level="INFO"
)

# Run single cycle
results = orchestrator.run_cycle()
print(f"Cycle {results['cycle']} completed")
print(f"Tasks processed: {results['tasks_processed']}")

# Get status
status = orchestrator.get_status()
print(f"Running: {status['running']}")
print(f"Total tasks processed: {status['tasks_processed']}")
```

### Running Continuously

```python
def on_cycle_complete(results):
    print(f"Cycle complete: {results['tasks_processed']} tasks")

orchestrator.run_continuous(callback=on_cycle_complete)
```

### Predefined Workflows

```python
# Process inbox workflow
result = orchestrator.run_workflow(
    "process_inbox",
    input_data={}
)

# Daily briefing workflow
result = orchestrator.run_workflow(
    "daily_briefing",
    input_data={}
)

# Task cleanup workflow
result = orchestrator.run_workflow(
    "task_cleanup",
    input_data={"days_old": 30}
)
```

---

## Configuration

### Orchestrator Configuration

```python
from skills.orchestration import OrchestratorConfig, SkillOrchestrator

config = OrchestratorConfig({
    "vault_path": "D:/MyVault",
    "log_level": "INFO",
    "check_interval": 60,  # seconds
    "max_tasks_per_cycle": 10,
    "auto_approve_threshold": {
        "payment_amount": 50,
        "email_recipients": 5
    },
    "enabled_watchers": ["whatsapp", "linkedin", "google"],
    "dry_run": False
})

orchestrator = SkillOrchestrator(config)
```

### Skill Configuration

Each skill accepts a `config` dictionary:

```python
from skills import get_skill

# WhatsApp watcher with custom keywords
whatsapp = get_skill(
    "whatsapp_watcher_skill",
    config={
        "keywords": ["urgent", "asap", "invoice", "payment", "help"],
        "check_interval": 30,
        "session_path": "/path/to/session"
    }
)

# Decision engine with custom rules
decision = get_skill(
    "decision_engine",
    config={
        "rules": [
            {
                "name": "high_value_payment",
                "conditions": {"max_amount": 100},
                "action": "require_approval"
            }
        ],
        "auto_approve_threshold": {"payment_amount": 50}
    }
)
```

---

## Development

### Creating a New Skill

1. **Inherit from BaseSkill**:
   ```python
   from skills.core.base_skill import BaseSkill
   
   class MyNewSkill(BaseSkill):
       def __init__(self, vault_path=None, config=None):
           super().__init__(
               name="my_new_skill",
               description="Does something amazing",
               version="1.0.0",
               vault_path=vault_path,
               config=config
           )
       
       def _get_input_schema(self) -> Dict[str, Any]:
           return {
               "type": "object",
               "properties": {
                   "param1": {"type": "string", "description": "Description"}
               },
               "required": ["param1"]
           }
       
       def execute(self, **kwargs) -> Dict[str, Any]:
           # Implementation
           return {"success": True, "data": {...}, "error": None}
   ```

2. **Add to registry** in `skills/__init__.py`:
   ```python
   SKILL_REGISTRY["my_new_skill"] = MyNewSkill
   SKILL_CATEGORIES["action"].append("my_new_skill")
   ```

3. **Export from module** in appropriate `__init__.py`

### Testing Skills

```python
import unittest
from skills import get_skill

class TestTaskExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = get_skill("task_extractor")
    
    def test_extract_task(self):
        result = self.extractor.execute(
            content="Please send invoice ASAP"
        )
        self.assertTrue(result["success"])
        self.assertGreater(len(result["data"]["tasks"]), 0)

if __name__ == "__main__":
    unittest.main()
```

---

## Error Handling

All skills return consistent error format:

```python
result = skill.execute(...)

if not result["success"]:
    print(f"Error: {result['error']}")
    # Handle error
```

Skill-specific exceptions:

- `SkillError` - Base exception
- `SkillConfigurationError` - Invalid configuration
- `SkillExecutionError` - Execution failure

---

## Logging

Skills log to two destinations:

1. **Console/Stream** - Via Python logging
2. **Vault Logs** - JSON files in `/Logs` folder

```python
# Access logs
from skills import get_skill

logger = get_skill("log_agent_activity", vault_path="D:/MyVault")

# Get logs for date range
logs = logger.get_logs(
    start_date="2026-01-01",
    end_date="2026-01-07",
    activity_type="task_completed"
)

# Generate report
report = logger.generate_report(
    start_date="2026-01-01",
    end_date="2026-01-07"
)
print(report)
```

---

## Best Practices

### 1. Use Dry Run Mode

Test skills without real effects:

```python
orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    dry_run=True  # Safe testing
)
```

### 2. Implement Approval Workflows

For sensitive actions:

```python
decision_result = decision_engine.execute(task=task)
if decision_result["data"]["decision"] == "approve":
    # Create approval request
    write_vault_tasks.execute(
        task_data={...},
        folder="Pending_Approval"
    )
```

### 3. Log Everything

```python
log_agent_activity.execute(
    activity_type="action_taken",
    activity_data={"action": "...", "result": "..."}
)
```

### 4. Handle Errors Gracefully

```python
result = skill.execute(...)
if not result["success"]:
    logger.error(f"Skill failed: {result['error']}")
    # Implement retry or fallback
```

---

## Troubleshooting

### Common Issues

**Skill not found:**
```
ValueError: Unknown skill: skill_name
```
→ Check skill name in `SKILL_REGISTRY`

**Vault path not configured:**
```
SkillExecutionError: vault_path not configured
```
→ Pass `vault_path` when creating skill

**No tasks detected:**
→ Check watcher keywords and source content

### Getting Help

1. Check skill logs in `/Logs` folder
2. Enable DEBUG logging: `log_level="DEBUG"`
3. Review skill schema: `skill.get_schema()`

---

## Resources

- [Hackathon Main Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Silver Tier README](./SILVER_TIER_README.md)
- [Qwen Code Agent Skills](https://platform.qwen.com/docs/en/agents-and-tools/agent-skills/overview)

---

*AI Employee Skill System v1.0.0 - Silver Tier Implementation*
