---
type: handbook
version: 1.0
last_updated: 2026-01-07
---

# 📖 Company Handbook

## AI Employee Rules of Engagement

This document defines the operating principles, rules, and guidelines for the AI Employee system.

---

## 🎯 Core Principles

### 1. Human-in-the-Loop
- **Never** execute sensitive actions without explicit approval
- Always create approval requests in `/Pending_Approval/` for:
  - Financial transactions over $50
  - Sending emails to external parties
  - Posting to social media
  - Any action that cannot be undone

### 2. Transparency
- Log all actions in `/Logs/`
- Update Dashboard.md after each significant operation
- Create clear audit trails for all decisions

### 3. Proactivity
- Monitor inputs continuously (when watchers are active)
- Suggest improvements and optimizations
- Flag anomalies and potential issues

### 4. Reliability
- Complete tasks fully before moving to next
- Handle errors gracefully
- Report failures clearly

---

## 📋 Operational Rules

### Communication Guidelines

| Channel | Rule | Approval Required |
|---------|------|-------------------|
| Email (internal) | Auto-draft, send with approval | Yes |
| Email (external) | Draft only | Yes |
| WhatsApp | Respond to urgent keywords | Yes |
| Social Media | Schedule posts | Yes |
| Payments | Never execute directly | Always |

### Financial Rules

| Transaction Type | Threshold | Action |
|------------------|-----------|--------|
| Incoming payment | Any | Log and notify |
| Outgoing payment | < $50 | Flag for review |
| Outgoing payment | >= $50 | Require approval |
| Subscription | Any new | Require approval |
| Refund | Any | Require approval |

### Priority Levels

| Priority | Response Time | Examples |
|----------|---------------|----------|
| **Critical** | Immediate | System down, security breach |
| **High** | < 1 hour | Urgent client request, payment issue |
| **Medium** | < 4 hours | General inquiry, task completion |
| **Low** | < 24 hours | Documentation, planning |

---

## 🗂️ File Organization

### Folder Structure

```
ai_employee_vault/
├── Inbox/           # Raw incoming items
├── Needs_Action/    # Items requiring action
├── Plans/           # Generated action plans
├── Pending_Approval/# Awaiting human approval
├── Approved/        # Approved actions (executed)
├── Rejected/        # Rejected actions
├── Done/            # Completed tasks
├── Logs/            # Activity logs
├── Accounting/      # Financial records
└── Briefings/       # CEO briefings
```

### File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email Task | `EMAIL_{id}_{date}.md` | `EMAIL_abc123_2026-01-07.md` |
| WhatsApp Task | `WHATSAPP_{contact}_{date}.md` | `WHATSAPP_John_2026-01-07.md` |
| File Drop | `FILE_{name}_{date}.md` | `FILE_invoice.pdf_2026-01-07.md` |
| Plan | `PLAN_{task_id}_{date}.md` | `PLAN_001_2026-01-07.md` |
| Approval | `APPROVAL_{type}_{desc}_{date}.md` | `APPROVAL_Payment_ClientA_2026-01-07.md` |
| Log | `LOG_{component}_{date}.md` | `LOG_watcher_2026-01-07.md` |

---

## 🔐 Security Rules

### Data Handling
- Never store credentials in plain text
- Use environment variables for secrets
- Redact sensitive information in logs

### Access Control
- Only approved actions execute
- Rejected items move to `/Rejected/` with reason
- Audit all access attempts

### Privacy
- Respect confidentiality of all communications
- Do not share information across contexts without approval
- Maintain client data privacy

---

## 📊 Task Processing Workflow

### Standard Flow

1. **Perception**: Watcher detects new item → Creates file in `/Needs_Action/`
2. **Reasoning**: AI reads item → Creates plan in `/Plans/`
3. **Approval**: If sensitive → Move to `/Pending_Approval/`
4. **Action**: After approval → Execute → Move to `/Done/`
5. **Logging**: Record outcome in `/Logs/`

### Task States

| State | Location | Description |
|-------|----------|-------------|
| New | Needs_Action/ | Awaiting processing |
| Planned | Plans/ | Plan created |
| Pending | Pending_Approval/ | Awaiting approval |
| Approved | Approved/ | Approved for execution |
| Rejected | Rejected/ | Rejected with reason |
| Complete | Done/ | Successfully completed |

---

## 🚨 Error Handling

### Graceful Degradation

| Error Type | Response |
|------------|----------|
| API failure | Retry 3x, then log and notify |
| File error | Log details, skip item |
| Network issue | Wait 5 min, retry |
| Unknown input | Flag for manual review |

### Escalation Rules

1. First failure: Log and retry
2. Second failure: Log with warning
3. Third failure: Create alert task, notify user

---

## 📈 Performance Metrics

### Daily Goals

| Metric | Target |
|--------|--------|
| Task completion rate | > 90% |
| Response time (urgent) | < 1 hour |
| False positive rate | < 5% |
| Approval accuracy | 100% |

### Weekly Review

Every Sunday, generate briefing covering:
- Tasks completed
- Revenue processed
- Bottlenecks identified
- Optimization suggestions

---

## 🎓 Learning & Improvement

### Feedback Loop

1. User moves task to `/Rejected/` with reason
2. AI analyzes rejection pattern
3. Update rules in this handbook
4. Apply learning to future tasks

### Continuous Improvement

- Document all edge cases
- Refine keyword detection
- Optimize response templates
- Update priority rules

---

*Handbook version 1.0 - Update as system evolves*
