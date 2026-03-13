# LinkedIn Watcher - Usage Guide

## Overview

The LinkedIn Watcher is now integrated into the existing `watcher_skills.py` file. It uses Playwright for browser automation and stores credentials in the `.qwen/.env` file.

## Credentials Setup

Your LinkedIn credentials are already configured in `.qwen/.env`:

**Note:** The LinkedIn Watcher uses **browser automation (Playwright)** rather than the LinkedIn API, so these credentials are for reference. The actual authentication happens through your browser session.

## How It Works

1. **First Run**: Browser opens → You manually login to LinkedIn → Session saved
2. **Subsequent Runs**: Reuses saved session automatically
3. **Monitoring**: Checks messages, posts, jobs, and connections
4. **Output**: Creates action files in `/Needs_Action/` folder

## Usage via Qwen Code

### Basic Usage

```bash
# Ask Qwen Code to run the LinkedIn watcher
"Run the LinkedIn watcher to check for new messages and job opportunities"
```

### Using the Skill Directly

```python
from skills.perception.watcher_skills import LinkedInWatcherSkill

# Initialize the watcher
watcher = LinkedInWatcherSkill(
    vault_path="D:/Quarter 4/qwen-e-commerce/hackathon_0/silver-tier/ai_employee_vault",
    config={
        "keywords": ["hiring", "AI", "consulting", "opportunity"],
        "check_interval": 600
    }
)

# Execute the watcher
result = watcher.execute(
    watch_types=["messages", "posts", "jobs"],
    keywords=["AI", "automation"]
)

print(result)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `vault_path` | string | required | Path to Obsidian vault |
| `keywords` | list | ["hiring", "opportunity", "project"] | Keywords to monitor |
| `watch_types` | list | ["messages", "posts"] | What to watch |
| `check_interval` | int | 600 | Seconds between checks |

### Watch Types

- `"messages"` - LinkedIn messages
- `"posts"` - Feed posts
- `"jobs"` - Job opportunities
- `"connections"` - Connection requests

## Output Example

When the watcher finds new items, it creates files like:

```
ai_employee_vault/
└── Needs_Action/
    ├── LINKEDIN_MESSAGE_20260108_143000.md
    ├── LINKEDIN_JOB_20260108_143015.md
    └── LINKEDIN_POST_20260108_143030.md
```

### Action File Format

```markdown
---
type: linkedin_message
from: John Doe
received: 2026-01-08T14:30:00Z
priority: normal
status: pending
conversation_url: https://www.linkedin.com/messaging/
---

# LinkedIn Message

## From
**John Doe**

## Content
Hi, I'm interested in your AI consulting services...

## Matched Keywords
AI, consulting

## Suggested Actions
- [ ] Review message
- [ ] Draft response
- [ ] Archive after processing
```

## First Run - Login Required

On the **first run**, you need to login manually:

1. Run the watcher
2. Browser will open to LinkedIn
3. **Manually login** with your credentials
4. Session is saved for future runs

**Session expires after ~30 days** - you'll need to login again.

## Troubleshooting

### "LinkedIn login required" error

**Solution:**
- Run watcher in interactive mode
- Wait for browser to open
- Login to LinkedIn
- Session will be saved

### "Could not find messaging interface"

**Solution:**
- LinkedIn updates their UI frequently
- Check if you're logged in
- May need to update selectors in code

### No items detected

**Possible causes:**
- No new activity on LinkedIn
- Keywords too specific
- Items already processed (duplicate prevention)

**Solution:**
- Check `/Logs/` folder for details
- Try broader keywords
- Clear state: delete `.state/linkedin_processed.json`

## Integration with Other Skills

### With Scheduler

```python
# Schedule LinkedIn watcher to run every hour
# Scheduler triggers watcher_skill.execute()
```

### With Qwen Code

```bash
# After watcher creates action files
"Check the Needs_Action folder and draft responses to new LinkedIn messages"
```

## Architecture

```
┌─────────────────────────────────────┐
│  LinkedIn Watcher (watcher_skills)  │
│  - Loads credentials from .env      │
│  - Uses Playwright for automation   │
│  - Persistent session storage       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Creates Action Files:              │
│  /Needs_Action/LINKEDIN_*.md        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Qwen Code Processes:               │
│  - Reads action files               │
│  - Creates Plan.md                  │
│  - Takes action via MCP             │
│  - Moves to /Done                   │
└─────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `skills/perception/watcher_skills.py` | Main implementation (includes LinkedInWatcherSkill) |
| `.qwen/.env` | Credentials storage |
| `ai_employee_vault/.linkedin_session/` | Browser session data |
| `ai_employee_vault/.state/linkedin_processed.json` | Processed items tracking |

## Best Practices

1. **Run Interval**: Check every 10-15 minutes (not too frequent)
2. **Keywords**: Start with 5-10 relevant keywords
3. **Review Daily**: Process `/Needs_Action/` files daily
4. **Monitor Logs**: Check logs for errors weekly

## Logs

Daily logs are created in:
```
ai_employee_vault/Logs/linkedin_watcher_YYYY-MM-DD.log
```

Example:
```
[2026-01-08T14:30:00] [INFO] Session valid - logged in
[2026-01-08T14:30:05] [INFO] Checking LinkedIn messages...
[2026-01-08T14:30:10] [INFO] Created message action file: LINKEDIN_MESSAGE_20260108_143010.md
[2026-01-08T14:30:15] [INFO] Check complete - 3 new items detected
```

---

*Part of the Personal AI Employee Hackathon 0 - Silver Tier*
