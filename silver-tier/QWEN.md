# QWEN.md - Project Context

## Directory Overview

This is the **Bronze Tier** project directory for the **Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026**. It contains documentation, skill configurations, and resources for building a "Digital FTE" (Full-Time Equivalent) - an AI agent that autonomously manages personal and business affairs using Qwen Code as the reasoning engine and Obsidian as the knowledge dashboard.

**Purpose:** This directory serves as a workspace for developing the foundational layer (Bronze Tier) of an autonomous AI employee system. The architecture follows a "local-first, agent-driven, human-in-the-loop" approach.

---

## Key Files

| File/Directory | Purpose |
|----------------|---------|
| `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md` | Comprehensive hackathon blueprint covering architecture, tiers, watchers, MCP servers, and the "Orchestrator" persistence loop pattern |
| `skills-lock.json` | Skill dependency lockfile tracking installed Qwen skills (currently: `browsing-with-playwright`) |
| `.qwen/skills/` | Installed skill packages with scripts, documentation, and references |
| `QWEN.md` | This context file for AI assistant interactions |

---

## Project Structure

```
bronz-tier/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main documentation
├── skills-lock.json          # Skill dependencies
├── QWEN.md                   # This file
└── .qwen/
    └── skills/
        └── browsing-with-playwright/  # Browser automation skill
            ├── SKILL.md               # Skill usage guide
            ├── references/
            │   └── playwright-tools.md # Complete MCP tool reference
            └── scripts/
                ├── mcp-client.py      # Universal MCP client (HTTP + stdio)
                ├── start-server.sh    # Start Playwright MCP server
                ├── stop-server.sh     # Stop Playwright MCP server
                └── verify.py          # Server health check
```

---

## Usage

### Hackathon Tiers

This directory targets **Bronze Tier** completion (8-12 hours estimated):

- [ ] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [ ] One working Watcher script (Gmail OR file system monitoring)
- [ ] Qwen Code reading/writing to the vault
- [ ] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [ ] All AI functionality implemented as [Agent Skills](https://platform.qwen.com/docs/en/agents-and-tools/agent-skills/overview)

### Core Architecture Components

1. **The Brain:** Qwen Code (reasoning engine)
2. **The Memory/GUI:** Obsidian (local Markdown dashboard)
3. **The Senses (Watchers):** Python scripts monitoring Gmail, WhatsApp, filesystems
4. **The Hands (MCP):** Model Context Protocol servers for external actions

### Browser Automation Skill

The installed `browsing-with-playwright` skill enables web automation:

```bash
# Start the Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

**Server runs on:** `http://localhost:8808`

**Key tools available:**
- `browser_navigate` - Navigate to URLs
- `browser_snapshot` - Capture accessibility snapshot (element refs)
- `browser_click` - Click elements
- `browser_type` - Type text into inputs
- `browser_fill_form` - Fill multiple form fields
- `browser_take_screenshot` - Capture screenshots
- `browser_evaluate` - Execute JavaScript
- `browser_run_code` - Run multi-step Playwright code

See `.qwen/skills/browsing-with-playwright/SKILL.md` for detailed usage examples.

---

## Development Workflow

### 1. Start Browser Automation (if needed)

```bash
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

### 2. Use Qwen Code with Agent Skills

When using Qwen Code, skills are automatically loaded from `.qwen/skills/`. Prompt Qwen Code to:
- Read/write Markdown files in your Obsidian vault
- Execute browser automation via Playwright MCP
- Create `Plan.md` files for multi-step tasks

### 3. Human-in-the-Loop Pattern

For sensitive actions, Qwen Code should:
1. Create approval request file in `/Pending_Approval/`
2. Wait for user to move file to `/Approved/`
3. Execute action via MCP only after approval

### 4. Orchestrator Persistence Loop

Use the Orchestrator pattern to keep Qwen Code working autonomously until tasks complete. See the main documentation for implementation details.

---

## External Resources

- **Hackathon Zoom:** Wednesdays 10:00 PM PKT - [Join Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube Recordings:** [@panaversity](https://www.youtube.com/@panaversity)
- **Qwen Code Docs:** [Agent Skills](https://platform.qwen.com/docs/en/agents-and-tools/agent-skills/overview)
- **Orchestrator Pattern:** [GitHub Reference](https://github.com/anthropics/qwen-code/tree/main/.qwen/plugins/orchestrator)

---

## Notes for AI Assistants

- This is a **documentation/hackathon workspace**, not a traditional code project
- No build commands or package managers to run
- Focus on helping implement Agent Skills for Qwen Code
- Browser automation requires the Playwright MCP server running on port 8808
- All tool schemas are cached in `.qwen/skills/browsing-with-playwright/references/`
- Use `mcp-client.py` for direct MCP tool calls when needed
