# Digital FTE - AI Employee System (Gold Tier)

> **Autonomous Employee - Full cross-domain integration with Odoo ERP and Social Media**

A comprehensive implementation of the Gold Tier Digital FTE (Full-Time Equivalent) system - an autonomous AI agent that proactively manages personal and business affairs with full ERP integration, social media automation, and weekly CEO briefings.

## 📋 Table of Contents

- [Overview](#overview)
- [Gold Tier Requirements](#gold-tier-requirements)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Odoo ERP Integration](#odoo-erp-integration)
- [Facebook & Instagram Integration](#facebook--instagram-integration)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Agent Skills](#agent-skills)
- [Development](#development)

---

## Overview

This system implements the complete **Perception → Reasoning → Action** architecture with enterprise-grade integrations:

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception** | Watchers | Monitor Gmail, WhatsApp, Facebook, Odoo, filesystem |
| **Reasoning** | Task Processor + Qwen Code | Analyze tasks, generate plans, persist until complete |
| **Action** | Qwen Code + MCP Servers | Execute approved actions via MCP servers and Python scripts |

**AI Brain:** This implementation uses **Qwen Code** as the reasoning engine, not Claude Code.

### Gold Tier Deliverables

- ✅ All Silver Tier requirements (Foundation + Functional Assistant)
- ✅ Full cross-domain integration (Personal + Business)
- ✅ **Odoo Community ERP** integration via Docker + MCP server
- ✅ **Facebook & Instagram** integration (posts, messages, insights)
- ✅ **Twitter (X)** integration (posts, mentions, summaries)
- ✅ Multiple MCP servers for different action types
- ✅ **Weekly Business and Accounting Audit** with CEO Briefing
- ✅ **Error recovery** and graceful degradation
- ✅ **Comprehensive audit logging**
- ✅ **Ralph Wiggum loop** for autonomous multi-step completion
- ✅ Complete architecture documentation

---

## Gold Tier Requirements

### Completed ✓

1. ✅ **All Silver requirements** (Bronze + WhatsApp + LinkedIn + Email MCP + Scheduling)
2. ✅ **Full cross-domain integration** (Personal + Business)
3. ✅ **Odoo Community ERP** (self-hosted via Docker, integrated via MCP)
4. ✅ **Facebook & Instagram** integration (posts, messages, insights summary)
5. ✅ **Twitter (X)** integration (posts, mentions, summaries)
6. ✅ **Multiple MCP servers** (Email, Facebook, Odoo, Browser)
7. ✅ **Weekly Business and Accounting Audit** with CEO Briefing
8. ✅ **Error recovery** and graceful degradation
9. ✅ **Comprehensive audit logging**
10. ✅ **Ralph Wiggum loop** for autonomous completion
11. ✅ **Architecture documentation**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI Employee System (Gold Tier)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  Perception  │───▶│  Reasoning   │───▶│    Action    │              │
│  │   (Watchers) │    │ (Processor + │    │ (Qwen+MCP)   │              │
│  │              │    │  Qwen Code)  │    │              │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                   │                   │                       │
│         ▼                   ▼                   ▼                       │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Watchers:                                                │          │
│  │  • Gmail Watcher                                          │          │
│  │  • WhatsApp Watcher                                       │          │
│  │  • Facebook Watcher (NEW)                                 │          │
│  │  • Twitter Watcher (NEW)                                  │          │
│  │  • Odoo Accounting Watcher (NEW)                          │          │
│  │  • File System Watcher                                    │          │
│  │  • LinkedIn Watcher                                       │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  MCP Servers:                                             │          │
│  │  • Email MCP (Gmail)                                      │          │
│  │  • Facebook MCP (NEW)                                     │          │
│  │  • Odoo MCP (Accounting, Invoices, Payments) (NEW)        │          │
│  │  • Browser MCP (Playwright)                               │          │
│  │  • LinkedIn MCP                                           │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  External Integrations:                                   │          │
│  │  • Odoo ERP (Docker)                                      │          │
│  │  • Facebook/Meta Graph API                                │          │
│  │  • Instagram Graph API                                    │          │
│  │  • Twitter API v2                                         │          │
│  │  • Gmail API                                              │          │
│  │  • WhatsApp Web                                           │          │
│  │  • LinkedIn API                                           │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
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

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13+ | Watchers and orchestration |
| Node.js | 18+ | MCP servers |
| Docker Desktop | Latest | Odoo ERP container |
| Obsidian | v1.10.6+ | Knowledge vault |
| Claude Code | Active | AI reasoning engine |
| Git | Latest | Version control |

### Setup Steps

#### 1. Clone or Download Project

#### 2. Install Python Dependencies

```bash
cd gold-tier

# Install core dependencies
pip install -r requirements.txt

# Install Playwright
playwright install chromium
```

#### 3. Start Odoo ERP (Docker)

```bash
# Start Odoo container
docker-compose up -d

# Wait for Odoo to initialize (2-3 minutes)
# Access at: http://localhost:8069
# Default credentials: admin / admin
```

#### 4. Configure API Credentials

Create `.env` file in `src/config/`:

```bash
# Facebook/Meta
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_ig_account_id

# Twitter/X
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=hackathon_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# Gmail (from Silver Tier)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
```

#### 5. Open Vault in Obsidian

- Open Obsidian
- Click "Open folder as vault"
- Select `gold-tier/ai_employee_vault` folder

#### 6. Configure Claude Code Skills

```bash
# Copy skills to Claude Code
cp src/skills/*.md ~/.claude/skills/
```

---

## Quick Start

### 1. Start Odoo ERP

```bash
docker-compose up -d
```

### 2. Start All Watchers

```bash
# Start orchestrator with all watchers
python -m src.orchestrator ai_employee_vault --watchers filesystem,gmail,facebook,twitter,odoo --daemon --interval 60
```

### 3. Start MCP Servers

```bash
# Start Facebook MCP Server
python src/mcp/facebook_mcp_server.py

# Start Odoo MCP Server
python src/mcp/odoo_mcp_server.py

# Start Email MCP Server (Silver Tier)
python src/mcp/email_mcp_server.py
```

### 4. Process Tasks with Claude Code

```bash
# Open vault in Claude Code
claude
cd ai_employee_vault

# Use Agent Skills
"Process all pending tasks using gold-tier skills"
"Generate weekly CEO briefing"
"Sync with Odoo accounting"
```

### 5. Check Dashboard

Open `ai_employee_vault/Dashboard.md` in Obsidian

---

## Odoo ERP Integration

### Docker Configuration

Odoo Community runs in Docker with PostgreSQL:

```yaml
# docker-compose.yml
services:
  odoo:
    image: odoo:19.0
    ports:
      - "8069:8069"
    environment:
      - ODOO_DB=postgres
      - ODOO_DB_USER=postgres
      - ODOO_DB_PASSWORD=postgres
      - ODOO_ADMIN_PASSWORD=admin
    volumes:
      - odoo-data:/var/lib/odoo
      - ./docker/odoo-config:/etc/odoo

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  postgres-data:
```

### Odoo MCP Server

The Odoo MCP server provides these capabilities:

| Tool | Description |
|------|-------------|
| `odoo_connect` | Test connection to Odoo |
| `odoo_list_apps` | List installed Odoo apps |
| `odoo_search_records` | Search records in any model |
| `odoo_read_record` | Read a specific record |
| `odoo_create_record` | Create new record |
| `odoo_write_record` | Update existing record |
| `odoo_unlink_record` | Delete record |
| `odoo_get_invoices` | Get customer invoices |
| `odoo_create_invoice` | Create customer invoice |
| `odoo_validate_invoice` | Validate posted invoice |
| `odoo_get_payments` | Get payment records |
| `odoo_register_payment` | Register payment for invoice |
| `odoo_get_account_moves` | Get journal entries |
| `odoo_create_account_move` | Create journal entry |
| `odoo_get_partners` | Search business partners |
| `odoo_create_partner` | Create new partner |
| `odoo_get_products` | Get products/services |
| `odoo_get_financial_reports` | Get P&L, Balance Sheet |

### Odoo Accounting Watcher

Monitors Odoo for financial events:

- New invoices created
- Payments received
- Overdue payments
- Budget alerts

Creates action files in `/Needs_Action/` for:
- Invoice follow-up required
- Payment reconciliation needed
- Financial review needed

---

## Facebook & Instagram Integration

### Facebook MCP Server

Provides capabilities for Facebook/Instagram:

| Tool | Description |
|------|-------------|
| `facebook_post` | Create post on Facebook Page |
| `facebook_get_posts` | Get recent posts |
| `facebook_get_insights` | Get page insights |
| `facebook_get_messages` | Get page messages |
| `facebook_reply_message` | Reply to message |
| `instagram_post` | Create post on Instagram |
| `instagram_get_posts` | Get Instagram posts |
| `instagram_get_insights` | Get Instagram insights |
| `instagram_get_comments` | Get post comments |

### Facebook Watcher

Monitors for:
- New page messages (urgent keywords)
- New comments on posts
- Negative sentiment posts
- Mention alerts

Creates action files for:
- Customer service response needed
- Engagement opportunity
- Crisis management

### Automated Posting Workflow

1. **Content Generation**: AI generates post content based on business goals
2. **Approval Request**: Creates file in `/Pending_Approval/`
3. **Human Review**: User approves or rejects
4. **Scheduled Posting**: Posts to Facebook/Instagram/LinkedIn
5. **Performance Tracking**: Monitors engagement metrics

---

## Twitter (X) Integration

### Twitter MCP Server

| Tool | Description |
|------|-------------|
| `twitter_post_tweet` | Create new tweet |
| `twitter_get_timeline` | Get home timeline |
| `twitter_get_mentions` | Get mentions |
| `twitter_reply_tweet` | Reply to tweet |
| `twitter_retweet` | Retweet a tweet |
| `twitter_like_tweet` | Like a tweet |
| `twitter_get_insights` | Get tweet analytics |
| `twitter_search` | Search tweets |

### Twitter Watcher

Monitors for:
- Brand mentions
- Keyword alerts
- Competitor activity
- Industry trends

---

## Usage

### Running Watchers

#### File System Watcher

```bash
python src/run_watcher.py ai_employee_vault filesystem --daemon --interval 30
```

#### Facebook Watcher

```bash
python src/run_watcher.py ai_employee_vault facebook --daemon --interval 120
```

#### Twitter Watcher

```bash
python src/run_watcher.py ai_employee_vault twitter --daemon --interval 120
```

#### Odoo Accounting Watcher

```bash
python src/run_watcher.py ai_employee_vault odoo --daemon --interval 300
```

### Running the Orchestrator

```bash
# Show status
python -m src.orchestrator ai_employee_vault --status

# Run one cycle
python -m src.orchestrator ai_employee_vault

# Run continuously with all watchers
python -m src.orchestrator ai_employee_vault \
  --watchers filesystem,gmail,facebook,twitter,odoo \
  --daemon \
  --interval 60
```

### Using with Qwen Code

1. **Open your vault:**
   ```bash
   qwen
   cd ai_employee_vault
   ```

2. **Use Agent Skills:**
   ```
   @skills/gold-tier-tasks
   @skills/gold-tier-dashboard
   @skills/gold-tier-odoo
   @skills/gold-tier-social-media
   ```

3. **Common prompts:**
   ```
   Generate weekly CEO briefing
   Sync accounting data from Odoo
   Post to all social media platforms
   What invoices need follow-up?
   Show me this week's revenue
   ```

4. **Run skill scripts directly:**
   ```bash
   # Task management
   python .qwen/skills/gold-tier-tasks/scripts/task_manager.py list
   
   # Odoo integration
   python .qwen/skills/gold-tier-odoo/scripts/odoo_connector.py get-invoices
   
   # Social media posting
   python .qwen/skills/gold-tier-social/scripts/social_poster.py post --platform all --message "Hello"
   ```

---

## Folder Structure

### Project Structure

```
gold-tier/
├── ai_employee_vault/       # Obsidian vault
│   ├── Inbox/
│   │   └── Drop/           # Drop files here
│   ├── Needs_Action/       # Tasks awaiting processing
│   ├── Plans/              # Generated action plans
│   ├── Pending_Approval/   # Awaiting approval
│   ├── Approved/           # Approved for execution
│   ├── Rejected/           # Rejected tasks
│   ├── Done/               # Completed tasks
│   ├── Logs/               # Activity logs
│   ├── Accounting/         # Financial records
│   │   ├── Invoices/
│   │   ├── Payments/
│   │   └── Reports/
│   ├── Briefings/          # CEO briefings
│   │   └── Weekly/
│   ├── Social_Media/       # Social media content
│   │   ├── Facebook/
│   │   ├── Instagram/
│   │   ├── Twitter/
│   │   └── LinkedIn/
│   ├── Integrations/       # Integration configs
│   │   ├── Odoo/
│   │   ├── Facebook/
│   │   └── Twitter/
│   ├── Dashboard.md        # Main dashboard
│   ├── Company_Handbook.md # Rules
│   ├── Business_Goals.md   # Objectives
│   └── Odoo_Config.md      # Odoo settings
├── src/
│   ├── watchers/
│   │   ├── base_watcher.py
│   │   ├── filesystem_watcher.py
│   │   ├── gmail_watcher.py
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
│   │   ├── odoo_mcp_server.py
│   │   └── email_mcp_server.py
│   ├── integrations/
│   │   ├── odoo_client.py
│   │   ├── facebook_client.py
│   │   ├── twitter_client.py
│   │   └── error_handler.py
│   ├── skills/
│   │   ├── gold-tier-tasks.md
│   │   ├── gold-tier-dashboard.md
│   │   ├── gold-tier-odoo.md
│   │   └── gold-tier-social-media.md
│   ├── orchestrator.py
│   ├── run_watcher.py
│   └── __init__.py
├── docker/
│   ├── docker-compose.yml
│   └── odoo-config/
├── .env.example
├── requirements.txt
├── README.md
└── QWEN.md
```

---

## Agent Skills

### Qwen Code Skills Architecture

Gold Tier skills are designed for **Qwen Code** and located in `.qwen/skills/`:

| Skill | Location | Purpose |
|-------|----------|---------|
| `gold-tier-tasks` | `.qwen/skills/gold-tier-tasks/` | Task management |
| `gold-tier-dashboard` | `.qwen/skills/gold-tier-dashboard/` | Dashboard & briefings |
| `gold-tier-odoo` | `.qwen/skills/gold-tier-odoo/` | Odoo ERP integration |
| `gold-tier-social` | `.qwen/skills/gold-tier-social/` | Social media management |

Each skill includes:
- `config.json` - Skill configuration
- `scripts/` - Executable Python scripts
- `SKILL.md` - Usage documentation

### Task Management Skills

**Location:** `.qwen/skills/gold-tier-tasks/`

**Script:** `task_manager.py`

```bash
# List pending tasks
python .qwen/skills/gold-tier-tasks/scripts/task_manager.py list

# Read specific task
python .qwen/skills/gold-tier-tasks/scripts/task_manager.py read FILE_invoice.md

# Process all tasks
python .qwen/skills/gold-tier-tasks/scripts/task_manager.py process

# Complete task
python .qwen/skills/gold-tier-tasks/scripts/task_manager.py complete FILE_invoice.md
```

### Dashboard Skills

**Location:** `.qwen/skills/gold-tier-dashboard/`

**Scripts:** `dashboard_reader.py`, `briefing_gen.py`

- Read dashboard
- Update statistics
- Generate daily summaries
- Generate weekly CEO briefings

### Odoo Skills

**Location:** `.qwen/skills/gold-tier-odoo/`

**Script:** `odoo_connector.py`

```bash
# Test connection
python .qwen/skills/gold-tier-odoo/scripts/odoo_connector.py connect

# Get invoices
python .qwen/skills/gold-tier-odoo/scripts/odoo_connector.py get-invoices

# Create invoice
python .qwen/skills/gold-tier-odoo/scripts/odoo_connector.py create-invoice --partner "Client A" --amount 1000

# Get financial reports
python .qwen/skills/gold-tier-odoo/scripts/odoo_connector.py get-reports --type profit_loss
```

### Social Media Skills

**Location:** `.qwen/skills/gold-tier-social/`

**Script:** `social_poster.py`

```bash
# Post to all platforms
python .qwen/skills/gold-tier-social/scripts/social_poster.py post --platform all --message "Hello World"

# Post to Facebook only
python .qwen/skills/gold-tier-social/scripts/social_poster.py post --platform facebook --message "FB Post"

# Get insights
python .qwen/skills/gold-tier-social/scripts/social_poster.py get-insights --platform facebook
```
- Schedule posts

---

## Development

### Adding a New MCP Server

1. Create server file in `src/mcp/`:

```python
#!/usr/bin/env python3
from mcp.server import Server
import mcp.server.stdio

server = Server("my-mcp-server")

@server.list_tools()
async def list_tools():
    return [...]

@server.call_tool()
async def call_tool(name, arguments):
    ...

async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

2. Configure in Claude Code MCP settings

### Error Recovery Pattern

```python
from integrations.error_handler import ErrorHandler

error_handler = ErrorHandler(
    max_retries=3,
    retry_delay=5,
    fallback_action="log_and_notify"
)

@error_handler.handle
def risky_operation():
    ...
```

### Audit Logging

All actions are logged to:
- `/Logs/` directory (markdown files)
- Console output
- Odoo audit log (if integrated)

---

## Troubleshooting

### Odoo Not Starting

```bash
# Check container logs
docker-compose logs odoo

# Restart containers
docker-compose restart

# Reset database
docker-compose down -v
docker-compose up -d
```

### Facebook API Errors

1. Verify access token is valid (expires every 60 days)
2. Check page permissions
3. Ensure app is not in development mode

### Twitter API Rate Limits

- Check rate limit status in logs
- Increase check interval if hitting limits
- Use bearer token for higher limits

### Watcher Not Creating Files

1. Check Logs folder for errors
2. Verify API credentials
3. Ensure folder permissions allow writing

---

## Gold Tier Completion Checklist

- [ ] All Silver Tier requirements complete
- [ ] Odoo ERP running via Docker
- [ ] Odoo MCP server functional
- [ ] Facebook/Instagram integration working
- [ ] Twitter integration working
- [ ] Weekly CEO briefing generates correctly
- [ ] Error recovery tested
- [ ] Audit logging comprehensive
- [ ] Ralph Wiggum loop implemented
- [ ] Documentation complete

---

## Resources

- [Hackathon Main Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://docs.anthropic.com/claude-code/)
- [Odoo Documentation](https://www.odoo.com/documentation/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Qwen MCP Skills](https://github.com/anthropics/qwen-code)

---

*Digital FTE Gold Tier - Building Autonomous FTEs in 2026*
*Powered by Qwen Code*
