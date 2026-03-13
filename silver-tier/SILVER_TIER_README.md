# Silver Tier - Personal AI Employee Hackathon 0

**Functional Assistant** - Complete Silver Tier implementation for the Personal AI Employee Hackathon 0.

## Overview

This directory contains all the skills required to complete the **Silver Tier** of the Personal AI Employee Hackathon 0. The Silver Tier builds upon the Bronze Tier foundation and adds functional automation capabilities including multiple watchers, automated posting, planning, email integration, approval workflows, and scheduling.

## Silver Tier Requirements (All Complete ✓)

1. ✓ **All Bronze requirements** (Foundation layer complete)
2. ✓ **Two or more Watcher scripts** (WhatsApp + LinkedIn)
3. ✓ **Automatically Post on LinkedIn** about business to generate sales
4. ✓ **Qwen reasoning loop** that creates Plan.md files
5. ✓ **One working MCP server** for external action (Email MCP)
6. ✓ **Human-in-the-loop approval workflow** for sensitive actions
7. ✓ **Basic scheduling** via cron or Task Scheduler
8. ✓ **All AI functionality implemented as Agent Skills**

## Installed Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `browsing-with-playwright` | Browser automation (Bronze) | ✓ Complete |
| `whatsapp-watcher` | WhatsApp Web monitoring | ✓ Complete |
| `linkedin-poster` | LinkedIn automated posting | ✓ Complete |
| `plan-generator` | Plan.md creation for Qwen | ✓ Complete |
| `email-mcp` | Gmail API MCP server | ✓ Complete |
| `hitl-approval` | Human-in-the-loop approvals | ✓ Complete |
| `scheduler` | Task scheduling (cron/Windows) | ✓ Complete |

## Quick Start

### Prerequisites

Before setting up Silver Tier skills, ensure you have:

- [ ] **Bronze Tier complete** (Obsidian vault, basic structure)
- [ ] **Python 3.13+** installed
- [ ] **Node.js 18+** installed
- [ ] **Playwright** installed (`pip install playwright`)
- [ ] **Google Cloud Project** with Gmail API enabled (for Email MCP)

### Installation Steps

#### 1. Install Python Dependencies

```bash
# Navigate to bronze-tier directory
cd D:\Quarter 4\qwen-e-commerce\hackathon_0\bronz-tier

# Install Playwright
pip install playwright
playwright install chromium

# Install Google API dependencies (for Email MCP)
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### 2. Configure Each Skill

Each skill has its own `config.json` file that needs to be updated with your paths:

```bash
# WhatsApp Watcher
# Edit: .qwen/skills/whatsapp-watcher/scripts/config.json

# LinkedIn Poster
# Edit: .qwen/skills/linkedin-poster/scripts/config.json

# Plan Generator
# Edit: .qwen/skills/plan-generator/scripts/config.json

# Email MCP
# Edit: .qwen/skills/email-mcp/scripts/config.json
# Run OAuth setup: python .qwen/skills/email-mcp/scripts/oauth_setup.py

# HITL Approval
# Edit: .qwen/skills/hitl-approval/scripts/config.json

# Scheduler
# Edit: .qwen/skills/scheduler/scripts/config.json
```

#### 3. Set Up Email MCP (Gmail API)

```bash
# 1. Create Google Cloud Project and enable Gmail API
# 2. Download client_secret.json to:
#    .qwen/skills/email-mcp/credentials/client_secret.json

# 3. Run OAuth setup
python .qwen/skills/email-mcp/scripts/oauth_setup.py

# 4. Test the MCP server
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --test
```

#### 4. Test Each Skill

```bash
# WhatsApp Watcher (test run)
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py

# LinkedIn Poster (create a draft)
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py --draft --content "Test post"

# Plan Generator (list templates)
python .qwen/skills/plan-generator/scripts/plan_generator.py --list-templates

# HITL Approval (list pending)
python .qwen/skills/hitl-approval/scripts/approval_manager.py --list-pending

# Scheduler (list tasks)
python .qwen/skills/scheduler/scripts/task_scheduler.py --list
```

## Skill Usage Examples

### WhatsApp Watcher

Monitor WhatsApp for urgent messages:

```bash
# Start the watcher (runs continuously)
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py

# Or run with PM2 for persistence
pm2 start .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --name whatsapp-watcher --interpreter python
```

### LinkedIn Poster

Post to LinkedIn automatically:

```bash
# Create a draft for approval
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py --draft --content "Exciting business update!"

# Use a template
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py --template "achievement"

# Auto-post (if approval not required)
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py --content "Post content" --auto-post
```

### Plan Generator

Create structured plans for Qwen:

```bash
# Create a plan
python .qwen/skills/plan-generator/scripts/plan_generator.py \
  --title "Process Client Invoices" \
  --type "invoice_processing" \
  --priority "high"

# Update plan progress
python .qwen/skills/plan-generator/scripts/plan_generator.py \
  --update-plan "Plans/PLAN_process_client_invoices_*.md" \
  --completed-steps "1,2,3"

# List available templates
python .qwen/skills/plan-generator/scripts/plan_generator.py --list-templates
```

### Email MCP

Send emails via Gmail:

```bash
# Start the MCP server
python .qwen/skills/email-mcp/scripts/email_mcp_server.py

# Test authentication
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --test
```

### HITL Approval

Manage approval workflows:

```bash
# List pending approvals
python .qwen/skills/hitl-approval/scripts/approval_manager.py --list-pending

# List approved actions awaiting execution
python .qwen/skills/hitl-approval/scripts/approval_manager.py --list-approved

# Check for expired approvals
python .qwen/skills/hitl-approval/scripts/approval_manager.py --check-expiry

# Archive old approvals
python .qwen/skills/hitl-approval/scripts/approval_manager.py --archive
```

### Scheduler

Schedule automated tasks:

```bash
# Create a daily briefing task
python .qwen/skills/scheduler/scripts/task_scheduler.py --create \
  --name "Daily CEO Briefing" \
  --schedule "0 8 * * *" \
  --command "python" \
  --args ".qwen/skills/plan-generator/scripts/plan_generator.py --title Daily Briefing --type weekly_briefing"

# List all scheduled tasks
python .qwen/skills/scheduler/scripts/task_scheduler.py --list

# Run a task manually
python .qwen/skills/scheduler/scripts/task_scheduler.py --run --name "Daily CEO Briefing"
```

## Integration Examples

### Complete Workflow: WhatsApp → Plan → Email → Approval

1. **WhatsApp Watcher** detects urgent message about invoice request
2. **Plan Generator** creates a plan to process the invoice
3. **Email MCP** creates draft email with invoice
4. **HITL Approval** creates approval request file
5. **Human** reviews and moves file to /Approved
6. **Email MCP** sends the email
7. **Plan Generator** updates plan progress

### Scheduled Daily Briefing

1. **Scheduler** triggers at 8 AM daily
2. **Plan Generator** creates daily briefing plan
3. **Qwen Code** executes plan steps
4. **LinkedIn Poster** posts business update
5. **HITL Approval** manages any sensitive actions

## Folder Structure

```
bronz-tier/
├── .qwen/
│   └── skills/
│       ├── browsing-with-playwright/  # Bronze (existing)
│       ├── whatsapp-watcher/          # Silver (new)
│       ├── linkedin-poster/           # Silver (new)
│       ├── plan-generator/            # Silver (new)
│       ├── email-mcp/                 # Silver (new)
│       ├── hitl-approval/             # Silver (new)
│       └── scheduler/                 # Silver (new)
├── ai_employee_vault/
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Done/
│   ├── Plans/
│   ├── Scheduled_Tasks/
│   ├── Logs/
│   └── ...
└── skills-lock.json  # Updated with Silver Tier skills
```

## Configuration Files

Each skill requires configuration. Update these paths for your system:

### Common Configuration Fields

```json
{
  "vault_path": "D:/Quarter 4/qwen-e-commerce/hackathon_0/bronz-tier/ai_employee_vault",
  "log_level": "INFO",
  "require_approval": true
}
```

### Skill-Specific Configuration

See each skill's `SKILL.md` file for detailed configuration options:

- `.qwen/skills/whatsapp-watcher/SKILL.md`
- `.qwen/skills/linkedin-poster/SKILL.md`
- `.qwen/skills/plan-generator/SKILL.md`
- `.qwen/skills/email-mcp/SKILL.md`
- `.qwen/skills/hitl-approval/SKILL.md`
- `.qwen/skills/scheduler/SKILL.md`

## Testing Checklist

Before considering Silver Tier complete, verify:

- [ ] WhatsApp Watcher creates files in `/Needs_Action` when messages arrive
- [ ] LinkedIn Poster can create drafts and publish posts
- [ ] Plan Generator creates properly formatted Plan.md files
- [ ] Email MCP can authenticate and send emails
- [ ] HITL Approval workflow moves files between folders correctly
- [ ] Scheduler can create and run scheduled tasks
- [ ] All skills log to `/Logs` directory
- [ ] Qwen Code can use all skills via Agent Skills

## Troubleshooting

### Common Issues

**Playwright browser not found:**
```bash
playwright install chromium
```

**Gmail API authentication failed:**
```bash
python .qwen/skills/email-mcp/scripts/oauth_setup.py
```

**Task scheduler permission denied:**
- Windows: Run as Administrator
- Linux/Mac: Check cron daemon: `sudo systemctl status cron`

**Approval files not moving:**
- Check folder permissions
- Verify folder names match config

### Getting Help

1. Check each skill's `SKILL.md` documentation
2. Review logs in `/Logs` directory
3. Check reference documentation in each skill's `references/` folder

## Next Steps: Gold Tier

After completing Silver Tier, consider advancing to Gold Tier:

- [ ] Full cross-domain integration (Personal + Business)
- [ ] Odoo Community ERP integration
- [ ] Facebook and Instagram integration
- [ ] Twitter (X) integration
- [ ] Weekly Business and Accounting Audit
- [ ] Orchestrator loop for autonomous completion

## Resources

- [Hackathon Main Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Agent Skills](https://platform.qwen.com/docs/en/agents-and-tools/agent-skills/overview)
- [Playwright Documentation](https://playwright.dev/python/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

Part of the Personal AI Employee Hackathon 0 project.
