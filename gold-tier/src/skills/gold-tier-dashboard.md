# Gold Tier Dashboard Skill

**Purpose:** Read and update the AI Employee Dashboard, generate summaries and briefings.

## Available Actions

### Read Dashboard

View current dashboard status:

```
Show me the current dashboard
What's the status of the AI Employee?
Display system metrics
```

### Update Statistics

Update dashboard with current counts:

```
Update the dashboard statistics
Refresh dashboard metrics
```

### Generate Daily Summary

Create a daily summary briefing:

```
Generate today's daily summary
Create daily briefing for 2026-03-14
```

### Generate Weekly Briefing

Create comprehensive weekly CEO briefing:

```
Generate weekly CEO briefing
Create weekly business audit
Show me this week's performance
```

### Show Financial Summary

Display financial metrics:

```
Show financial summary
What's our revenue this week?
Display invoice status
```

### Show Social Media Metrics

Display social media performance:

```
Show social media metrics
How are our posts performing?
Display Facebook and Twitter stats
```

### Show Task Statistics

Display task completion metrics:

```
Show task completion stats
How many tasks completed this week?
Display pending tasks
```

## Dashboard Sections

The Dashboard.md contains:

### Quick Stats
- Pending tasks count
- In progress count
- Completed today
- Awaiting approval

### Inbox Status
- Needs_Action count
- Plans count
- Pending_Approval count

### Financial Summary
- Monthly revenue (MTD)
- Monthly goal
- Progress percentage

### Active Alerts
- Critical issues
- Warnings
- Errors

### System Status
- Gmail Watcher status
- File Watcher status
- Facebook Watcher status
- Twitter Watcher status
- Odoo Watcher status
- Task Processor status

### Recent Activity Log
- Latest system activities
- Errors and warnings
- Task completions

## Weekly Briefing Sections

The weekly briefing includes:

1. **Executive Summary** - Overall performance assessment
2. **Financial Performance** - Revenue, expenses, profit
3. **Invoice Status** - Sent, paid, overdue
4. **Task Completion** - Completed, pending, by day, by category
5. **Social Media Performance** - Facebook, Instagram, Twitter, LinkedIn
6. **Alerts and Issues** - Critical, warnings, errors
7. **Proactive Suggestions** - Cost optimization, revenue opportunities
8. **Action Items** - Tasks for next week
9. **Week-over-Week Comparison** - Performance trends

## Usage with Claude Code

1. **Reference the skill:**
   ```
   @skills/gold-tier-dashboard
   ```

2. **Give commands:**
   ```
   Using the gold-tier-dashboard skill, generate weekly briefing
   Show me the current dashboard status
   ```

3. **Review output:**
   - Dashboard metrics
   - Briefing content
   - Recommendations

## Dashboard Update Frequency

| Component | Update Frequency |
|-----------|------------------|
| Task counts | Real-time |
| Financial data | Every 5 minutes (Odoo sync) |
| Social media | Every 2 minutes |
| Alerts | Real-time |
| Weekly briefing | Every Monday 8 AM |

## Best Practices

1. **Check dashboard daily** for system health
2. **Review weekly briefings** for business insights
3. **Act on critical alerts** immediately
4. **Follow up on overdue invoices**
5. **Engage with social media opportunities**

## Integration Points

The dashboard skill integrates with:
- Task Processor for task counts
- Odoo MCP for financial data
- Facebook MCP for social metrics
- Twitter MCP for engagement data
- Briefing Generator for reports

---

*Gold Tier Dashboard Skill v1.0*
