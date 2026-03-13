# AI Employee Skill System

> **Modular, reusable skill architecture for autonomous AI employees**

A comprehensive implementation of the **Silver Tier** skill system for the Personal AI Employee Hackathon 0.

## 📦 What's Included

This package contains **17 modular skills** organized into 4 architectural layers:

### Core Skills (System/Reasoning)
- `read_markdown_file` - Read and parse Markdown files
- `parse_hackathon_requirements` - Extract requirements from documents
- `task_extractor` - Extract tasks from text content
- `task_prioritizer` - Prioritize tasks by importance
- `execution_planner` - Create execution plans

### Perception Skills (Watchers)
- `google_watcher_skill` - Monitor Google Alerts, Search, Gmail
- `linkedin_watcher_skill` - Monitor LinkedIn updates
- `whatsapp_watcher_skill` - Monitor WhatsApp Web messages

### Action Skills (Execution)
- `task_creation` - Create task files in vault
- `task_scheduling` - Schedule tasks with working hours
- `decision_engine` - Make autonomous decisions
- `action_executor` - Execute approved actions
- `progress_tracker` - Track task progress

### Integration Skills (Vault/Memory)
- `read_vault_tasks` - Read tasks from vault folders
- `write_vault_tasks` - Create/update task files
- `update_task_status` - Update status and move files
- `log_agent_activity` - Log activities for audit

## 🚀 Quick Start

### Install

Skills are already in place. Just import:

```python
from skills import get_skill
```

### Basic Usage

```python
from skills import get_skill

# Create a skill
extractor = get_skill(
    "task_extractor",
    vault_path="D:/MyVault"
)

# Execute
result = extractor.execute(
    content="Please send invoice ASAP",
    source_type="whatsapp"
)

if result["success"]:
    tasks = result["data"]["tasks"]
    print(f"Found {len(tasks)} tasks")
```

### Using the Orchestrator

```python
from skills.orchestration import create_orchestrator

orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    enabled_watchers=["whatsapp", "linkedin"],
    dry_run=False
)

# Run one cycle
results = orchestrator.run_cycle()

# Or run continuously
orchestrator.run_continuous()
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SKILLS_DOCUMENTATION.md](./SKILLS_DOCUMENTATION.md) | Complete skill reference and API docs |
| [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) | Practical usage examples |
| [ARCHITECTURE_SUMMARY.md](./ARCHITECTURE_SUMMARY.md) | Architecture overview and design |

## 📁 Structure

```
skills/
├── __init__.py              # Package root with registry
├── core/                    # System skills
│   ├── base_skill.py       # Base class
│   └── system_skills.py    # 5 system skills
├── perception/              # Watcher skills
│   └── watcher_skills.py   # 3 watcher skills
├── action/                  # Execution skills
│   └── execution_skills.py # 5 execution skills
├── integration/             # Vault skills
│   └── vault_skills.py     # 4 vault skills
└── orchestration/           # Coordination
    └── orchestrator.py     # Skill orchestrator
```

## 🎯 Silver Tier Coverage

All Silver Tier requirements implemented:

- ✅ **Two or more Watcher scripts** (WhatsApp, LinkedIn, Google)
- ✅ **Qwen reasoning loop** (task_extractor, task_prioritizer, execution_planner)
- ✅ **Human-in-the-loop approval** (decision_engine with approval workflow)
- ✅ **Task scheduling** (task_scheduling skill)
- ✅ **All AI functionality as skills** (17 modular skills)

## 🔧 Configuration

```python
from skills.orchestration import OrchestratorConfig, SkillOrchestrator

config = OrchestratorConfig({
    "vault_path": "D:/MyVault",
    "log_level": "INFO",
    "check_interval": 60,
    "max_tasks_per_cycle": 10,
    "enabled_watchers": ["whatsapp", "linkedin"],
    "dry_run": False
})

orchestrator = SkillOrchestrator(config)
```

## 🧪 Testing

```python
from skills import get_skill

# Test task extraction
extractor = get_skill("task_extractor")
result = extractor.execute(content="Send invoice ASAP")
assert result["success"]
assert len(result["data"]["tasks"]) > 0
```

## 📋 Features

- **Modular** - Each skill is independent and reusable
- **Composable** - Skills can be combined in workflows
- **Type-safe** - Input/output schemas for all skills
- **Logged** - All activities logged for audit
- **Configurable** - Extensive configuration options
- **Safe** - Dry-run mode for testing

## 🛠️ Development

### Adding a New Skill

```python
from skills.core.base_skill import BaseSkill

class MyNewSkill(BaseSkill):
    def __init__(self, vault_path=None, config=None):
        super().__init__(
            name="my_new_skill",
            description="Does something useful",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Implementation
        return {"success": True, "data": {...}, "error": None}
```

## 📖 Resources

- [Hackathon Main Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Silver Tier README](./SILVER_TIER_README.md)
- [Qwen Code Agent Skills](https://platform.qwen.com/docs/en/agents-and-tools/agent-skills/overview)

## 📄 License

Part of the Personal AI Employee Hackathon 0 project.

---

*AI Employee Skill System v1.0.0 - Silver Tier Implementation*
