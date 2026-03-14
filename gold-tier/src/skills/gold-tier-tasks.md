# Gold Tier Task Management Skill

**Purpose:** Manage tasks in the AI Employee System vault - read, create, process, and move tasks through the workflow.

## Available Actions

### List Pending Tasks

List all tasks in Needs_Action folder:

```
List all pending tasks in Needs_Action
Show me tasks that need action
What tasks are pending?
```

### Read Task File

Read a specific task file:

```
Read the task file FILE_invoice_2026-03-14.md
Show me the details of TASK_001
```

### Create Action Plan

Create an execution plan for a task:

```
Create an action plan for processing this invoice
Generate execution plan for email response
```

### Create Approval Request

Create approval request for sensitive actions:

```
Create approval request for payment to Vendor A
Request approval for social media post
```

### Move Task to Done

Mark a task as complete:

```
Move TASK_001 to Done folder
Mark this task as complete
```

### Move Task to Approved

Approve a pending task:

```
Move APPROVAL_001 to Approved folder
Approve this payment request
```

### Move Task to Rejected

Reject a task with reason:

```
Move TASK_001 to Rejected with reason "Duplicate invoice"
Reject this request because budget exceeded
```

## Task File Format

Task files follow this structure:

```markdown
---
type: email | invoice | payment | file_drop | facebook_message | twitter_mention | odoo_invoice
source: gmail | facebook | twitter | odoo | filesystem
priority: low | normal | high
status: pending | in_progress | completed
created: ISO 8601 timestamp
---

# Task Title

## Content

Task content here...

## Suggested Actions

- [ ] Action 1
- [ ] Action 2
```

## Workflow States

| State | Folder | Description |
|-------|--------|-------------|
| New | Needs_Action/ | Awaiting processing |
| Planned | Plans/ | Plan created |
| Pending | Pending_Approval/ | Awaiting approval |
| Approved | Approved/ | Approved for execution |
| Rejected | Rejected/ | Rejected with reason |
| Complete | Done/ | Successfully completed |

## Usage with Claude Code

When using this skill with Claude Code:

1. **Reference the skill:**
   ```
   @skills/gold-tier-tasks
   ```

2. **Give commands:**
   ```
   Using the gold-tier-tasks skill, process all pending tasks
   ```

3. **Review output:**
   - Tasks created
   - Plans generated
   - Approvals requested
   - Tasks completed

## Best Practices

1. **Always review approval requests** before approving
2. **Add notes** to task files for context
3. **Move rejected tasks** with clear reasons
4. **Check the Dashboard** for overall status
5. **Review logs** for any errors

## Error Handling

If a task fails processing:
1. Check the Logs folder for error details
2. Review the task file for issues
3. Manually process if needed
4. Document the resolution

---

*Gold Tier Task Management Skill v1.0*
