# LinkedIn Watcher - Testing Guide

## Quick Start

### Step 1: Login to LinkedIn (First Time Only)

The LinkedIn session has expired. You need to login manually:

```bash
cd D:\Quarter 4\qwen-e-commerce\hackathon_0\silver-tier
python skills/perception/linkedin_login_helper.py
```

**What happens:**
1. Browser opens to LinkedIn
2. You login with your credentials
3. Session is saved automatically
4. Browser closes

### Step 2: Test the Watcher

After logging in:

```bash
python skills/perception/test_linkedin_watcher.py
```

**Expected output:**
```
[OK] LinkedIn Watcher initialized successfully
[OK] Playwright is installed
[OK] Watcher executed successfully!
Messages found: 0
Posts found: 0
Jobs found: 0
[OK] Test completed successfully!
```

## Test Results Explanation

### Success Indicators

| Message | Meaning |
|---------|---------|
| `[OK] LinkedIn Watcher initialized successfully` | Skill loaded correctly |
| `[OK] LinkedIn Client ID loaded` | Credentials found in .env |
| `[OK] Session path exists` | Session folder ready |
| `[OK] Playwright is installed` | Browser automation ready |
| `[OK] Watcher executed successfully` | LinkedIn check completed |

### Common Issues

#### "LinkedIn login required"

**Cause:** Session expired or not logged in

**Fix:**
```bash
python skills/perception/linkedin_login_helper.py
```

#### "Playwright is NOT installed"

**Fix:**
```bash
pip install playwright
playwright install chromium
```

#### "Could not find messaging interface"

**Cause:** LinkedIn UI changed or not logged in

**Fix:**
1. Run login helper again
2. Make sure you're logged in to LinkedIn

## What the Watcher Does

### 1. Checks LinkedIn For:

- **Messages** - New LinkedIn messages containing your keywords
- **Posts** - Feed posts matching your keywords
- **Jobs** - Job opportunities with your keywords
- **Connections** - New connection requests

### 2. Creates Action Files:

Files are created in:
```
ai_employee_vault/Needs_Action/
├── LINKEDIN_MESSAGE_YYYYMMDD_HHMMSS.md
├── LINKEDIN_POST_YYYYMMDD_HHMMSS.md
├── LINKEDIN_JOB_YYYYMMDD_HHMMSS.md
└── LINKEDIN_CONNECTION_YYYYMMDD_HHMMSS.md
```

### 3. Example Action File:

```markdown
---
type: linkedin_message
from: John Doe
received: 2026-03-08T14:30:00Z
priority: normal
status: pending
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

## Keywords Monitored

Default keywords:
- `hiring`
- `opportunity`
- `AI`
- `automation`
- `consulting`

You can customize these in the test script or when calling via Qwen Code.

## Running via Qwen Code

Instead of the test script, use Qwen Code:

```bash
# Check LinkedIn
"Run the LinkedIn watcher to check for new messages and job opportunities"

# Process results
"Check the Needs_Action folder and draft responses to new LinkedIn messages"
```

## Session Management

### Where Session is Stored

```
ai_employee_vault/.linkedin_session/
```

### Session Expires

- **Duration:** ~30 days
- **Signs of expiry:** "Login required" error
- **Fix:** Run `linkedin_login_helper.py` again

### Clear Session (if needed)

```bash
# Delete session folder
rmdir /s ai_employee_vault\.linkedin_session

# Run login helper to create new session
python skills/perception/linkedin_login_helper.py
```

## Logs

Daily logs are created in:
```
ai_employee_vault/Logs/linkedin_watcher_YYYY-MM-DD.log
```

Example log content:
```
[2026-03-08T04:10:17] [INFO] Session valid - logged in
[2026-03-08T04:10:20] [INFO] Checking LinkedIn messages...
[2026-03-08T04:10:25] [INFO] Check complete - 2 new items detected
```

## Troubleshooting

### Test Shows 0 Items Found

**This is normal if:**
- No new activity on LinkedIn
- Keywords don't match recent content
- Already processed recent items (duplicate prevention)

**To verify watcher is working:**
1. Check logs in `ai_employee_vault/Logs/`
2. Look for "Session valid - logged in"
3. Check for "Check complete" messages

### Browser Opens But Nothing Happens

**Possible causes:**
- LinkedIn still loading
- Need to scroll/feed refresh
- Session expired

**Fix:**
1. Watch the browser during test
2. If stuck, close and run login helper
3. Try test again

### Windows Console Encoding Errors

If you see encoding errors with Unicode characters:

**Fix:** Set console to UTF-8
```cmd
chcp 65001
```

Or the test script already uses ASCII-safe characters `[OK]`, `[X]`, etc.

## Next Steps After Testing

Once the test passes:

1. **Integrate with Scheduler** - Run watcher automatically every hour
2. **Connect with Qwen Code** - Process action files automatically
3. **Customize Keywords** - Add your specific industry terms
4. **Set Up Notifications** - Get alerts for high-priority items

## Files Reference

| File | Purpose |
|------|---------|
| `skills/perception/watcher_skills.py` | Main LinkedIn watcher implementation |
| `skills/perception/linkedin_login_helper.py` | Login helper script |
| `skills/perception/test_linkedin_watcher.py` | Test script |
| `.qwen/.env` | LinkedIn credentials |
| `ai_employee_vault/.linkedin_session/` | Browser session storage |

---

*Part of Personal AI Employee Hackathon 0 - Silver Tier*
