# QWEN.md - Gold Tier Project Context (Qwen Code Aligned)

## Directory Overview

This is the **Gold Tier** project directory for the **Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026**. 

**AI Brain:** Qwen Code (not Claude Code)

The Gold Tier represents an **Autonomous Employee** with full cross-domain integration including:
- Odoo ERP integration (accounting, invoices, payments)
- Facebook & Instagram integration (posts, messages, insights)
- Twitter (X) integration (tweets, mentions, analytics)
- Weekly Business and Accounting Audit with CEO Briefing
- Error recovery and graceful degradation
- Comprehensive audit logging

**Purpose:** This directory contains the complete Gold Tier implementation with all watchers, MCP servers, processors, and **Qwen Code Agent Skills**.

---

## Qwen Code Skills Architecture

Skills for Qwen Code are organized in `.qwen/skills/` directory:

```
.qwen/
├── skills/
│   ├── gold-tier-tasks/       # Task management
│   ├── gold-tier-odoo/        # Odoo ERP integration
│   ├── gold-tier-social/      # Social media (Facebook, Twitter, Instagram)
│   └── gold-tier-dashboard/   # Dashboard & briefings
├── mcp.json                   # MCP server configuration
└── config.json                # Qwen configuration
```

### Using Skills with Qwen Code

**Method 1: Run skill scripts directly**
```bash
python .qwen/skills/gold-tier-tasks/scripts/task_manager.py list
python .qwen/skills/gold-tier-odoo/scripts/odoo_connector.py get-invoices
python .qwen/skills/gold-tier-social/scripts/social_poster.py post --platform all --message "Hello"
```

**Method 2: Qwen Code prompts**
When using Qwen Code, reference skills in prompts:
```
Using the gold-tier-tasks skill, process all pending tasks
With gold-tier-odoo, get unpaid invoices from Odoo
Use gold-tier-social to post to Facebook and Twitter
```

**Method 3: MCP servers**
Start MCP servers for external API access:
```bash
python src/mcp/odoo_mcp_server.py
python src/mcp/facebook_mcp_server.py
python src/mcp/twitter_mcp_server.py
```

---

## Key Files

| File/Directory | Purpose |
|----------------|---------|
| `README.md` | Complete Gold Tier documentation |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Odoo ERP container configuration |
| `.env.example` | Environment variables template |
| `src/` | Source code (watchers, processors, MCP servers) |
| `ai_employee_vault/` | Obsidian vault for knowledge management |
| `.qwen/skills/` | Agent Skills for Claude Code |

---

## Project Structure

```
gold-tier/
├── ai_employee_vault/           # Obsidian vault
│   ├── Inbox/Drop/             # Drop files here
│   ├── Needs_Action/           # Tasks awaiting processing
│   ├── Plans/                  # Action plans
│   ├── Pending_Approval/       # Awaiting approval
│   ├── Approved/               # Approved tasks
│   ├── Rejected/               # Rejected tasks
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Activity logs
│   ├── Accounting/             # Financial records
│   ├── Briefings/              # CEO briefings
│   ├── Social_Media/           # Social media content
│   ├── Integrations/           # Integration configs
│   ├── Dashboard.md            # Main dashboard
│   ├── Company_Handbook.md     # Rules
│   └── Business_Goals.md       # Objectives
├── src/
│   ├── watchers/
│   │   ├── base_watcher.py     # Base watcher class
│   │   ├── filesystem_watcher.py
│   │   ├── facebook_watcher.py
│   │   ├── twitter_watcher.py
│   │   ├── odoo_watcher.py
│   │   └── __init__.py
│   ├── processors/
│   │   ├── task_processor.py
│   │   ├── briefing_generator.py
│   │   └── __init__.py
│   ├── mcp/
│   │   ├── facebook_mcp_server.py
│   │   ├── twitter_mcp_server.py
│   │   └── odoo_mcp_server.py
│   ├── integrations/
│   │   ├── error_handler.py
│   │   ├── audit_logger.py
│   │   └── __init__.py
│   ├── skills/
│   │   ├── gold-tier-tasks.md
│   │   ├── gold-tier-dashboard.md
│   │   ├── gold-tier-odoo.md
│   │   └── gold-tier-social-media.md
│   ├── orchestrator.py
│   ├── run_watcher.py
│   └── __init__.py
├── docker/
│   └── docker-compose.yml
├── requirements.txt
├── README.md
└── QWEN.md
```

---

## Usage

### Prerequisites

1. **Docker Desktop** installed and running
2. **Python 3.13+** installed
3. **Node.js 18+** installed (for MCP servers)
4. **Obsidian** for vault GUI
5. **Claude Code** subscription

### Quick Start

#### 1. Install Dependencies

```bash
cd gold-tier
pip install -r requirements.txt
playwright install chromium
```

#### 2. Start Odoo ERP

```bash
docker-compose up -d
# Wait 2-3 minutes for Odoo to initialize
# Access at: http://localhost:8069
# Default: admin / admin
```

#### 3. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your credentials
```

#### 4. Start Watchers

```bash
# Run orchestrator with all watchers
python -m src.orchestrator ai_employee_vault \
  --watchers filesystem,facebook,twitter,odoo \
  --daemon \
  --interval 60
```

#### 5. Start MCP Servers

```bash
# In separate terminals:
python src/mcp/facebook_mcp_server.py
python src/mcp/twitter_mcp_server.py
python src/mcp/odoo_mcp_server.py
```

#### 6. Use with Claude Code

```bash
claude
cd ai_employee_vault

# Reference skills
@gold-tier-tasks
@gold-tier-dashboard
@gold-tier-odoo
@gold-tier-social-media
```

---

## Environment Variables

Create `.env` file with:

```bash
# Facebook/Meta
FACEBOOK_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=
INSTAGRAM_ACCOUNT_ID=

# Twitter/X
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=hackathon_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Gmail (from Silver Tier)
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REFRESH_TOKEN=
```

---

## Gold Tier Requirements (All Complete ✓)

1. ✅ All Silver Tier requirements
2. ✅ Full cross-domain integration (Personal + Business)
3. ✅ Odoo Community ERP via Docker + MCP
4. ✅ Facebook & Instagram integration
5. ✅ Twitter (X) integration
6. ✅ Multiple MCP servers
7. ✅ Weekly Business and Accounting Audit
8. ✅ Error recovery and graceful degradation
9. ✅ Comprehensive audit logging
10. ✅ Ralph Wiggum loop implementation
11. ✅ Complete documentation

---

## Agent Skills

### Task Management (`gold-tier-tasks.md`)
- List pending tasks
- Read task files
- Create action plans
- Create approval requests
- Move tasks through workflow

### Dashboard (`gold-tier-dashboard.md`)
- Read dashboard
- Update statistics
- Generate daily summaries
- Generate weekly briefings

### Odoo Integration (`gold-tier-odoo.md`)
- Connect to Odoo
- Get/create invoices
- Register payments
- Search partners
- Get financial reports

### Social Media (`gold-tier-social-media.md`)
- Post to Facebook/Instagram/Twitter
- Get insights
- Reply to messages
- Search mentions

---

## External Resources

- **Hackathon Main Document:** [Personal AI Employee Hackathon 0](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **Claude Code Agent Skills:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Odoo Documentation:** https://www.odoo.com/documentation/
- **Facebook Graph API:** https://developers.facebook.com/docs/graph-api/
- **Twitter API v2:** https://developer.twitter.com/en/docs/twitter-api
- **Model Context Protocol:** https://modelcontextprotocol.io/

---

## Notes for AI Assistants

- This is a **complete Gold Tier implementation**
- All watchers follow the base_watcher pattern with error recovery
- MCP servers use stdio transport for Claude Code integration
- Audit logging is comprehensive (JSONL format)
- Briefing generator creates weekly CEO reports
- Error handler provides retry logic with exponential backoff
- Circuit breaker pattern prevents cascade failures

---

*Gold Tier - Building Autonomous FTEs in 2026*
