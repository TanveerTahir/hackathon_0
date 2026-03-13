# Digital FTE - AI Employee System (Bronze Tier)

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A comprehensive implementation of the Bronze Tier Digital FTE (Full-Time Equivalent) system - an AI agent that proactively manages personal and business affairs using Qwen Code as the reasoning engine and Obsidian as the knowledge dashboard.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Agent Skills](#agent-skills)
- [Development](#development)

---

## Overview

This system implements the **Perception → Reasoning → Action** architecture:

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception** | Watchers | Monitor Gmail, filesystem, etc. for new items |
| **Reasoning** | Task Processor | Analyze tasks, generate plans |
| **Action** | Qwen Code + MCP | Execute approved actions |

### Bronze Tier Deliverables

- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ File System Watcher (working)
- ✅ Gmail Watcher (requires API setup)
- ✅ Task processing workflow
- ✅ Human-in-the-loop approval system
- ✅ Agent Skills for Qwen Code

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Employee System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Perception  │───▶│  Reasoning   │───▶│    Action    │  │
│  │   (Watchers) │    │  (Processor) │    │ (Qwen+MCP)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Gmail        │    │ Task Files   │    │ Email Send   │  │
│  │ Filesystem   │    │ Plans        │    │ File Move    │  │
│  │ WhatsApp*    │    │ Approvals    │    │ Dashboard    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Obsidian Vault      │
              │   (Memory/GUI)        │
              └───────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Obsidian (for the vault GUI)
- Qwen Code (for AI reasoning)

### Setup Steps

1. **Clone or download this project**

2. **Install Python dependencies** (optional, for Gmail watcher):
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

3. **Open the vault in Obsidian**
   - Open Obsidian
   - Click "Open folder as vault"
   - Select `ai_employee_vault` folder

4. **Configure Qwen Code** (optional)
   - Copy skills to Qwen Code skills folder:
     ```bash
     cp src/skills/*.md ~/.qwen/skills/
     ```

---

## Quick Start

### 1. Start the File System Watcher

```bash
# Run once (single check)
python src/run_watcher.py ai_employee_vault filesystem

# Run continuously (daemon mode)
python src/run_watcher.py ai_employee_vault filesystem --daemon --interval 30
```

### 2. Drop a File for Processing

```bash
# On Windows
copy somefile.pdf ai_employee_vault\Inbox\Drop\

# On Mac/Linux
cp somefile.pdf ai_employee_vault/Inbox/Drop/
```

### 3. Process Tasks

```bash
# Run the orchestrator (single cycle)
python -m src.orchestrator ai_employee_vault

# Or run continuously
python -m src.orchestrator ai_employee_vault --daemon --interval 60
```

### 4. Check the Dashboard

Open `ai_employee_vault/Dashboard.md` in Obsidian to see:
- Pending tasks count
- Completed tasks
- System status

---

## Usage

### Running Watchers

#### File System Watcher

Monitors a drop folder for new files:

```bash
# Single check
python src/run_watcher.py ai_employee_vault filesystem

# Continuous monitoring
python src/run_watcher.py ai_employee_vault filesystem --daemon

# Custom interval (check every 30 seconds)
python src/run_watcher.py ai_employee_vault filesystem --daemon --interval 30
```

#### Gmail Watcher

Monitors Gmail for new messages (requires API setup):

```bash
# First, set up Gmail API credentials
# 1. Go to Google Cloud Console
# 2. Enable Gmail API
# 3. Create OAuth 2.0 credentials
# 4. Download as gmail_credentials.json
# 5. Place in src/config/

# Run Gmail watcher
python src/run_watcher.py ai_employee_vault gmail --daemon
```

### Running the Orchestrator

The orchestrator coordinates all watchers and task processing:

```bash
# Show status
python -m src.orchestrator ai_employee_vault --status

# Run one cycle
python -m src.orchestrator ai_employee_vault

# Run continuously with both watchers
python -m src.orchestrator ai_employee_vault --watchers filesystem,gmail --daemon

# Custom interval, no auto-processing
python -m src.orchestrator ai_employee_vault --interval 120 --no-process
```

### Using with Qwen Code

1. **Open your vault in Qwen Code:**
   ```bash
   qwen
   cd ai_employee_vault
   ```

2. **Use the Agent Skills:**
   ```
   @skills/digital-fte-tasks
   @skills/digital-fte-dashboard
   ```

3. **Common prompts:**
   ```
   Process all tasks in Needs_Action folder
   Generate a weekly briefing
   Update the dashboard
   What tasks are pending approval?
   ```

---

## Folder Structure

### Project Structure

```
bronz-tier/
├── ai_employee_vault/       # Obsidian vault
│   ├── Inbox/
│   │   └── Drop/           # Drop files here for processing
│   ├── Needs_Action/       # Tasks awaiting processing
│   ├── Plans/              # Generated action plans
│   ├── Pending_Approval/   # Awaiting human approval
│   ├── Approved/           # Approved for execution
│   ├── Rejected/           # Rejected tasks
│   ├── Done/               # Completed tasks
│   ├── Logs/               # Activity logs
│   ├── Accounting/         # Financial records
│   ├── Briefings/          # CEO briefings
│   ├── Dashboard.md        # Main dashboard
│   ├── Company_Handbook.md # Rules and guidelines
│   └── Business_Goals.md   # Business objectives
├── src/
│   ├── watchers/
│   │   ├── base_watcher.py
│   │   ├── filesystem_watcher.py
│   │   ├── gmail_watcher.py
│   │   └── __init__.py
│   ├── processors/
│   │   ├── task_processor.py
│   │   └── __init__.py
│   ├── skills/
│   │   ├── digital-fte-tasks.md
│   │   └── digital-fte-dashboard.md
│   ├── orchestrator.py
│   ├── run_watcher.py
│   └── __init__.py
├── README.md
└── QWEN.md
```

### Vault Structure

| Folder | Purpose |
|--------|---------|
| `Inbox/Drop` | Drop files here for automatic processing |
| `Needs_Action` | Tasks created by watchers |
| `Plans` | Action plans generated by AI |
| `Pending_Approval` | Tasks requiring human approval |
| `Approved` | Approved tasks ready for execution |
| `Rejected` | Rejected tasks with reasons |
| `Done` | Completed tasks |
| `Logs` | System activity logs |

---

## Agent Skills

### Task Management Skills

Located in `src/skills/digital-fte-tasks.md`:
- List pending tasks
- Read task files
- Create action plans
- Create approval requests
- Move tasks to Done
- Update dashboard

### Dashboard Skills

Located in `src/skills/digital-fte-dashboard.md`:
- Read dashboard
- Update statistics
- Generate daily summaries
- Generate weekly briefings

### Using Skills with Qwen Code

```bash
# Start Qwen Code
qwen

# Navigate to vault
cd ai_employee_vault

# Reference skills in prompts
"Using the digital-fte-tasks skill, process all pending tasks"
"Using the digital-fte-dashboard skill, generate a weekly briefing"
```

---

## Development

### Adding a New Watcher

1. Create a new file in `src/watchers/`:
   ```python
   from .base_watcher import BaseWatcher

   class MyWatcher(BaseWatcher):
       def check_for_updates(self):
           # Implement check logic
           pass

       def create_action_file(self, item):
           # Implement file creation
           pass
   ```

2. Update `src/watchers/__init__.py` to export the new watcher

3. Add to orchestrator's `_load_watchers()` method

### Task File Format

```markdown
---
type: email
from: "John Doe"
subject: "Meeting Request"
priority: "normal"
status: "pending"
---

# 📧 Email: Meeting Request

## Content

[Email content here]

## Suggested Actions

- [ ] Review request
- [ ] Check calendar
- [ ] Draft reply
```

### Plan File Format

```markdown
---
type: plan
task_file: "TASK_FILENAME.md"
priority: "normal"
status: "planned"
needs_approval: false
---

# 📋 Action Plan

## Action Steps

1. [ ] Step 1
2. [ ] Step 2
3. [ ] Step 3

## Approval Required

No - This task can be executed automatically.
```

---

## Troubleshooting

### Watcher Not Creating Files

1. Check the Logs folder for errors
2. Verify the drop folder path is correct
3. Ensure file permissions allow reading/writing

### Gmail Watcher Fails

1. Verify credentials.json is in `src/config/`
2. Ensure Gmail API is enabled in Google Cloud Console
3. Run once interactively to authorize

### Dashboard Not Updating

1. Check that Dashboard.md exists
2. Verify file permissions
3. Run orchestrator with `--status` to check state

---

## Next Steps (Silver Tier)

To extend beyond Bronze Tier:

1. **Add WhatsApp Watcher** - Monitor WhatsApp Web for messages
2. **Implement MCP Servers** - For email sending, social media posting
3. **Add Scheduling** - Use cron/Task Scheduler for automated runs
4. **Enhance Approval Workflow** - Add email notifications for approvals

---

## Resources

- [Personal AI Employee Hackathon Documentation](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Agent Skills](https://platform.qwen.com/docs/en/agents-and-tools/agent-skills/overview)
- [Obsidian](https://obsidian.md/)

---

*Digital FTE Bronze Tier - Building Autonomous FTEs in 2026*
