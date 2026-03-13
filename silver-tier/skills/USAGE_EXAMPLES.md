# AI Employee Skill System - Usage Examples

Practical examples for using the AI Employee Skill System.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Intermediate Examples](#intermediate-examples)
3. [Advanced Workflows](#advanced-workflows)
4. [Integration Examples](#integration-examples)

---

## Basic Examples

### Example 1: Read a Markdown File

```python
from skills import get_skill

# Initialize skill
reader = get_skill(
    "read_markdown_file",
    vault_path="D:/MyVault"
)

# Read a file
result = reader.execute(
    file_path="Dashboard.md",
    include_content=True,
    parse_frontmatter=True
)

if result["success"]:
    data = result["data"]
    print(f"File exists: {data['exists']}")
    print(f"Word count: {data['word_count']}")
    print(f"Frontmatter: {data['frontmatter']}")
    print(f"Content preview: {data['content'][:200]}...")
```

### Example 2: Extract Tasks from Text

```python
from skills import get_skill

extractor = get_skill("task_extractor")

# Email content
email = """
Dear Team,

Please review the Q1 financial report by Friday. 
We also need to schedule a client meeting urgently.
The invoice for Project X should be sent today.

Best regards,
John
"""

result = extractor.execute(
    content=email,
    source_type="email",
    priority_keywords=["urgent", "asap", "today", "friday"]
)

if result["success"]:
    print(f"Confidence: {result['data']['confidence']}")
    for task in result["data"]["tasks"]:
        print(f"\nTask: {task['title']}")
        print(f"Priority: {task['priority']}")
        print(f"Description: {task['description'][:100]}...")
```

### Example 3: Prioritize Tasks

```python
from skills import get_skill

prioritizer = get_skill("task_prioritizer")

tasks = [
    {"title": "Send invoice to Client A", "priority": "high"},
    {"title": "Reply to team emails", "priority": "normal"},
    {"title": "URGENT: Fix payment gateway", "priority": "normal"},
    {"title": "Update website content", "priority": "low"},
    {"title": "Prepare monthly report", "priority": "normal"}
]

business_goals = {
    "keywords": ["invoice", "payment", "revenue", "client"],
    "quarter": "Q1",
    "focus": "revenue_growth"
}

result = prioritizer.execute(
    tasks=tasks,
    business_goals=business_goals,
    max_priority_tasks=3
)

if result["success"]:
    data = result["data"]
    print("Priority Distribution:")
    print(data["priority_distribution"])
    
    print("\nPrioritized Tasks:")
    for task in data["prioritized_tasks"]:
        print(f"  [{task['priority_level']}] {task['title']} (score: {task['priority_score']})")
    
    print("\nRecommendations:")
    for rec in data["recommendations"]:
        print(f"  - {rec}")
```

---

## Intermediate Examples

### Example 4: Create Execution Plan

```python
from skills import get_skill

planner = get_skill("execution_planner")

task = {
    "title": "Process Client Invoice",
    "description": """
    Generate invoice for Client A for January services.
    Amount: $1,500 for consulting services.
    Send via email to client@example.com.
    """,
    "priority": "high",
    "type": "invoice_generation",
    "amount": 1500,
    "client": "Client A"
}

available_resources = [
    "email_mcp",
    "file_system",
    "pdf_generator"
]

constraints = {
    "time_limit": "2 hours",
    "require_approval": True,
    "budget_limit": None
}

result = planner.execute(
    task=task,
    available_resources=available_resources,
    constraints=constraints
)

if result["success"]:
    plan = result["data"]
    print(f"Plan ID: {plan['plan_id']}")
    print(f"Task Type: {plan['task_type']}")
    print(f"Estimated Duration: {plan['estimated_duration']}")
    print(f"\nSteps:")
    for step in plan["steps"]:
        status = "✓" if step.get("completed") else "○"
        print(f"  {status}. {step['title']} ({step['estimated_minutes']} min)")
    
    print(f"\nRequired Approvals: {plan['required_approvals']}")
    print(f"Resources Needed: {plan['resources_needed']}")
```

### Example 5: Decision Engine

```python
from skills import get_skill

decision_engine = get_skill(
    "decision_engine",
    config={
        "rules": [
            {
                "name": "small_payment_auto_approve",
                "conditions": {"max_amount": 50},
                "action": "auto_approve"
            },
            {
                "name": "large_payment_require_approval",
                "conditions": {"max_amount": 500},
                "action": "require_approval"
            }
        ],
        "auto_approve_threshold": {
            "payment_amount": 50,
            "email_recipients": 5
        }
    }
)

# Test different tasks
tasks = [
    {
        "title": "Send $30 software subscription payment",
        "type": "payment",
        "amount": 30
    },
    {
        "title": "Send $200 vendor payment",
        "type": "payment",
        "amount": 200
    },
    {
        "title": "Reply to client email",
        "type": "communication"
    }
]

for task in tasks:
    result = decision_engine.execute(
        task=task,
        context={"business_goals": {"cost_control": True}}
    )
    
    if result["success"]:
        data = result["data"]
        print(f"\nTask: {task['title']}")
        print(f"  Decision: {data['decision']}")
        print(f"  Confidence: {data['confidence']}")
        print(f"  Reasoning: {data['reasoning']}")
```

### Example 6: Task Scheduling

```python
from skills import get_skill

scheduler = get_skill("task_scheduling")

tasks = [
    {
        "title": "Morning team standup",
        "priority": "high",
        "estimated_duration": 30
    },
    {
        "title": "Process client invoices",
        "priority": "high",
        "estimated_duration": 60
    },
    {
        "title": "Reply to emails",
        "priority": "normal",
        "estimated_duration": 45
    },
    {
        "title": "Update project documentation",
        "priority": "low",
        "estimated_duration": 90
    }
]

working_hours = {
    "start": 9,   # 9 AM
    "end": 17,    # 5 PM
    "timezone": "UTC"
}

blackout_dates = ["2026-01-15", "2026-01-16"]  # Holidays

result = scheduler.execute(
    tasks=tasks,
    working_hours=working_hours,
    blackout_dates=blackout_dates
)

if result["success"]:
    data = result["data"]
    print("Scheduled Tasks:\n")
    for task in data["scheduled_tasks"]:
        print(f"  {task['scheduled_date']} {task['scheduled_time_only']}")
        print(f"    → {task['title']} ({task['priority']})")
    
    if data["schedule_conflicts"]:
        print("\nConflicts:")
        for conflict in data["schedule_conflicts"]:
            print(f"  ⚠ {conflict['task1']} vs {conflict['task2']}")
    
    print("\nRecommendations:")
    for rec in data["recommendations"]:
        print(f"  • {rec}")
```

---

## Advanced Workflows

### Example 7: Complete Task Processing Pipeline

```python
from skills import get_skill

# Initialize all skills
extractor = get_skill("task_extractor")
prioritizer = get_skill("task_prioritizer")
planner = get_skill("execution_planner")
decision_engine = get_skill("decision_engine")
task_creator = get_skill("task_creation", vault_path="D:/MyVault")
vault_writer = get_skill("write_vault_tasks", vault_path="D:/MyVault")

# Raw message content
message = """
Hi! This is John from Client A. 

We urgently need the invoice for January services. 
The amount should be $1,500 for the consulting work we discussed.

Also, can we schedule a meeting next week to discuss the new project?
Please let me know your availability.

Thanks!
"""

print("=== Task Processing Pipeline ===\n")

# Step 1: Extract tasks
print("Step 1: Extracting tasks...")
extract_result = extractor.execute(
    content=message,
    source_type="whatsapp"
)

if not extract_result["success"]:
    print(f"Extraction failed: {extract_result['error']}")
    exit(1)

tasks = extract_result["data"]["tasks"]
print(f"Extracted {len(tasks)} tasks\n")

# Step 2: Prioritize tasks
print("Step 2: Prioritizing tasks...")
priority_result = prioritizer.execute(
    tasks=tasks,
    business_goals={"keywords": ["invoice", "payment", "client"]}
)

prioritized = priority_result["data"]["prioritized_tasks"]
print(f"Prioritized {len(prioritized)} tasks\n")

# Step 3: Create plans
print("Step 3: Creating execution plans...")
for task in prioritized:
    plan_result = planner.execute(task=task)
    if plan_result["success"]:
        print(f"  Created plan for: {task['title']}")

# Step 4: Make decisions
print("\nStep 4: Making decisions...")
for task in prioritized:
    decision_result = decision_engine.execute(task=task)
    if decision_result["success"]:
        decision = decision_result["data"]["decision"]
        print(f"  {task['title']}: {decision}")

# Step 5: Create task files
print("\nStep 5: Creating task files in vault...")
for task in prioritized:
    create_result = task_creator.execute(
        task_data=task,
        task_type="whatsapp",
        auto_categorize=True,
        destination_folder="Needs_Action"
    )
    if create_result["success"]:
        print(f"  Created: {create_result['data']['file_path']}")

print("\n=== Pipeline Complete ===")
```

### Example 8: WhatsApp Monitoring Workflow

```python
from skills import get_skill
import time

# Initialize watcher
whatsapp = get_skill(
    "whatsapp_watcher_skill",
    vault_path="D:/MyVault",
    config={
        "keywords": ["urgent", "asap", "invoice", "payment", "help"],
        "check_interval": 30
    }
)

# Initialize task creator
task_creator = get_skill("task_creation", vault_path="D:/MyVault")

# Initialize logger
logger = get_skill("log_agent_activity", vault_path="D:/MyVault")

def process_new_messages(result):
    """Callback to process new messages"""
    if not result["success"]:
        print(f"Watcher error: {result['error']}")
        return
    
    data = result["data"]
    messages = data.get("new_messages", [])
    
    if messages:
        print(f"\n📱 Found {len(messages)} new messages")
        
        for msg in messages:
            print(f"  From: {msg.get('contact', 'Unknown')}")
            print(f"  Text: {msg.get('text', '')[:50]}...")
            
            # Create task file
            task_creator.execute(
                task_data={
                    "title": f"WhatsApp: {msg.get('contact', 'Unknown')}",
                    "description": msg.get("text", ""),
                    "priority": "high" if msg.get("priority") == "high" else "normal",
                    "source": "WhatsApp"
                },
                task_type="whatsapp",
                destination_folder="Needs_Action"
            )
            
            # Log activity
            logger.execute(
                activity_type="whatsapp_message_processed",
                activity_data={
                    "contact": msg.get("contact"),
                    "keywords_matched": msg.get("matched_keywords", [])
                }
            )
    else:
        print("No new messages")

# Run watcher once (for demo)
print("Checking WhatsApp for new messages...")
result = whatsapp.execute()
process_new_messages(result)

# For continuous monitoring:
# whatsapp.start_continuous_monitoring(callback=process_new_messages)
```

### Example 9: Daily Briefing Generation

```python
from skills import get_skill
from datetime import datetime

# Initialize skills
read_tasks = get_skill("read_vault_tasks", vault_path="D:/MyVault")
write_tasks = get_skill("write_vault_tasks", vault_path="D:/MyVault")

today = datetime.now().strftime("%Y-%m-%d")

print(f"Generating Daily Briefing for {today}...\n")

# Get tasks from different folders
needs_action = read_tasks.execute(folder="Needs_Action", limit=20)
completed = read_tasks.execute(folder="Done", limit=10)
pending_approval = read_tasks.execute(folder="Pending_Approval", limit=10)

# Build briefing content
briefing = f"""---
date: {today}
type: daily_briefing
generated: {datetime.now().isoformat()}
---

# Daily Briefing - {today}

## Executive Summary

Good morning! Here's your daily briefing.

## Tasks Requiring Action

**Total:** {needs_action.get('data', {}).get('total_count', 0)} tasks

"""

# Add priority tasks
tasks = needs_action.get("data", {}).get("tasks", [])
high_priority = [t for t in tasks if t.get("priority") in ["high", "critical"]]

if high_priority:
    briefing += "### High Priority\n\n"
    for task in high_priority[:5]:
        briefing += f"- [ ] {task.get('title', 'Untitled')}\n"
    briefing += "\n"

briefing += """
## Completed Recently

"""

completed_tasks = completed.get("data", {}).get("tasks", [])
if completed_tasks:
    for task in completed_tasks[:5]:
        briefing += f"- [x] {task.get('title', 'Untitled')}\n"
else:
    briefing += "No recently completed tasks.\n"

briefing += """
## Awaiting Your Approval

"""

approval_tasks = pending_approval.get("data", {}).get("tasks", [])
if approval_tasks:
    for task in approval_tasks:
        briefing += f"- ⏳ {task.get('title', 'Untitled')}\n"
else:
    briefing += "No pending approvals.\n"

briefing += """
## Recommendations

1. Review high priority tasks first
2. Approve pending items in /Pending_Approval
3. Check the Dashboard for overall status

---
*Generated by AI Employee Skill System*
"""

# Write briefing
result = write_tasks.execute(
    task_data={
        "title": f"Daily Briefing - {today}",
        "type": "briefing",
        "content": briefing
    },
    folder="Briefings"
)

if result["success"]:
    print(f"✓ Briefing created: {result['data']['file_path']}")
    print(f"\nSummary:")
    print(f"  - Needs Action: {needs_action.get('data', {}).get('total_count', 0)}")
    print(f"  - Completed: {len(completed_tasks)}")
    print(f"  - Pending Approval: {len(approval_tasks)}")
```

---

## Integration Examples

### Example 10: Using with Qwen Code

Create a skill file for Qwen Code:

```markdown
# AI Employee Skills for Qwen Code

## Available Skills

### Task Management
- `read_vault_tasks` - Read tasks from vault folders
- `write_vault_tasks` - Create/update task files
- `update_task_status` - Update task status and move files
- `task_extractor` - Extract tasks from text content

### Workflow
- `task_prioritizer` - Prioritize tasks by importance
- `execution_planner` - Create execution plans
- `decision_engine` - Make autonomous decisions
- `action_executor` - Execute approved actions

### Monitoring
- `whatsapp_watcher_skill` - Monitor WhatsApp messages
- `linkedin_watcher_skill` - Monitor LinkedIn updates
- `google_watcher_skill` - Monitor Google services

## Usage Examples

### Process All Pending Tasks

```
Using the AI Employee skills:
1. Read all tasks from Needs_Action folder
2. Prioritize them by urgency and business goals
3. Create execution plans for top 5 tasks
4. Make decisions about each task
5. Execute approved actions
6. Move completed tasks to Done
```

### Generate Daily Briefing

```
Using the AI Employee skills:
1. Read tasks from Needs_Action, Done, and Pending_Approval
2. Count tasks in each folder
3. Generate a briefing markdown file
4. Save to Briefings folder with today's date
```

### Monitor WhatsApp

```
Using the whatsapp_watcher_skill:
1. Check for new messages containing keywords
2. Extract any tasks from messages
3. Create task files in Needs_Action
4. Log the activity
```
```

### Example 11: Orchestrator Integration

```python
from skills.orchestration import create_orchestrator

# Create orchestrator
orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    enabled_watchers=["whatsapp", "linkedin"],
    dry_run=False
)

# Custom callback for each cycle
def on_cycle(results):
    print(f"\n=== Cycle {results['cycle']} Complete ===")
    print(f"Duration: {results['duration_seconds']:.2f}s")
    print(f"Tasks processed: {results['tasks_processed']}")
    
    # Check for errors
    if "error" in results:
        print(f"ERROR: {results['error']}")
    
    # Check perception results
    perception = results.get("perception", {})
    if perception.get("items_detected", 0) > 0:
        print(f"New items detected: {perception['items_detected']}")
    
    # Check reasoning results
    reasoning = results.get("reasoning", {})
    if reasoning.get("plans_created", 0) > 0:
        print(f"Plans created: {reasoning['plans_created']}")
    
    # Check action results
    action = results.get("action", {})
    if action.get("approvals_requested", 0) > 0:
        print(f"Approvals requested: {action['approvals_requested']}")

# Run with callback
print("Starting orchestrator (press Ctrl+C to stop)...")
try:
    orchestrator.run_continuous(callback=on_cycle)
except KeyboardInterrupt:
    print("\nStopping orchestrator...")
    orchestrator.stop()
    print(f"Final status: {orchestrator.get_status()}")
```

---

## Tips and Best Practices

### 1. Start with Dry Run

```python
# Test without real effects
orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    dry_run=True  # Safe mode
)
```

### 2. Use Appropriate Logging

```python
# Enable detailed logging
orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    log_level="DEBUG"  # or INFO, WARNING, ERROR
)
```

### 3. Configure Watchers Wisely

```python
# Only enable needed watchers
orchestrator = create_orchestrator(
    vault_path="D:/MyVault",
    enabled_watchers=["whatsapp"]  # Only WhatsApp
)
```

### 4. Set Reasonable Limits

```python
# Limit tasks per cycle
config = {
    "max_tasks_per_cycle": 10,  # Process max 10 tasks per cycle
    "check_interval": 60  # Check every 60 seconds
}
```

### 5. Monitor and Adjust

```python
# Check orchestrator status
status = orchestrator.get_status()
print(f"Tasks processed: {status['tasks_processed']}")
print(f"Cycle count: {status['cycle_count']}")
```

---

*AI Employee Skill System - Usage Examples v1.0.0*
