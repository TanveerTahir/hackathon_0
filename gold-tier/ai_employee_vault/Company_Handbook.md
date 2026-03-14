---
type: handbook
version: 2.0
last_updated: 2026-03-14
tier: gold
---

# 📖 Company Handbook - Gold Tier

## AI Employee Rules of Engagement

This document defines the operating principles, rules, and guidelines for the Gold Tier AI Employee system with full cross-domain integration.

---

## 🎯 Core Principles

### 1. Human-in-the-Loop
- **Never** execute sensitive actions without explicit approval
- Always create approval requests in `/Pending_Approval/` for:
  - Financial transactions over $500
  - Sending external communications
  - Posting to social media
  - Any action that cannot be undone
  - Odoo invoice validation
  - Payment registration

### 2. Transparency
- Log all actions to `/Logs/` directory
- Update Dashboard.md after each significant operation
- Create clear audit trails in `/Logs/Audit/`
- Maintain JSONL format for programmatic access

### 3. Proactivity
- Monitor all inputs continuously (when watchers active)
- Generate weekly CEO briefings automatically
- Suggest improvements and optimizations
- Flag anomalies and potential issues
- Sync with Odoo for real-time financial data

### 4. Reliability
- Complete tasks fully before moving to next
- Handle errors gracefully with retry logic
- Implement circuit breaker pattern
- Report failures clearly with context

### 5. Autonomy (Gold Tier)
- Use Ralph Wiggum loop for multi-step tasks
- Self-recover from transient errors
- Escalate persistent issues to human
- Learn from rejection patterns

---

## 📋 Operational Rules

### Communication Guidelines

| Channel | Rule | Approval Required |
|---------|------|-------------------|
| Email (internal) | Auto-draft, send with approval | Yes |
| Email (external) | Draft only | Yes |
| WhatsApp | Respond to urgent keywords | Yes |
| Facebook Messages | Respond within 24 hours | Yes |
| Twitter Mentions | Engage appropriately | Yes |
| Social Media Posts | Schedule posts | Yes |
| Payments | Never execute directly | Always |

### Financial Rules (Odoo Integration)

| Transaction Type | Threshold | Action |
|------------------|-----------|--------|
| Incoming payment | Any | Log to Odoo, notify |
| Outgoing payment | < $500 | Flag for review |
| Outgoing payment | >= $500 | Require approval |
| Invoice creation | Any | Draft, then approval |
| Invoice validation | Any | Require approval |
| Subscription | Any new | Require approval |
| Refund | Any | Require approval |

### Priority Levels

| Priority | Response Time | Examples |
|----------|---------------|----------|
| **Critical** | Immediate | System down, security breach, negative viral post |
| **High** | < 1 hour | Urgent client request, overdue invoice, complaint |
| **Medium** | < 4 hours | General inquiry, task completion, normal post |
| **Low** | < 24 hours | Documentation, planning, engagement |

---

## 🗂️ File Organization

### Folder Structure

```
ai_employee_vault/
├── Inbox/
│   └── Drop/           # Drop files here for processing
├── Needs_Action/       # Items requiring action
├── Plans/              # Generated action plans
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Approved actions (executed)
├── Rejected/           # Rejected actions
├── Done/               # Completed tasks
├── Logs/               # Activity logs
│   └── Audit/          # Audit trail (JSONL)
├── Accounting/         # Financial records
│   ├── Invoices/
│   ├── Payments/
│   └── Reports/
├── Briefings/          # CEO briefings
│   └── Weekly/
├── Social_Media/       # Social media content
│   ├── Facebook/
│   ├── Instagram/
│   ├── Twitter/
│   └── LinkedIn/
├── Integrations/       # Integration configs
│   ├── Odoo/
│   ├── Facebook/
│   └── Twitter/
├── Dashboard.md        # Main dashboard
├── Company_Handbook.md # Rules and guidelines
├── Business_Goals.md   # Business objectives
└── Odoo_Config.md      # Odoo settings
```

### File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email Task | `EMAIL_{id}_{date}.md` | `EMAIL_abc123_2026-03-14.md` |
| Facebook Message | `FACEBOOK_MSG_{id}_{date}.md` | `FACEBOOK_MSG_001_2026-03-14.md` |
| Twitter Mention | `TWITTER_MENTION_{id}_{date}.md` | `TWITTER_MENTION_001_2026-03-14.md` |
| Odoo Invoice | `ODOO_INVOICE_{id}_{date}.md` | `ODOO_INVOICE_INV2026001_2026-03-14.md` |
| Odoo Payment | `ODOO_PAYMENT_{id}_{date}.md` | `ODOO_PAYMENT_PAY2026001_2026-03-14.md` |
| Plan | `PLAN_{task_id}_{date}.md` | `PLAN_001_2026-03-14.md` |
| Approval | `APPROVAL_{type}_{desc}_{date}.md` | `APPROVAL_Payment_VendorA_2026-03-14.md` |
| Log | `LOG_{component}_{date}.md` | `LOG_watcher_2026-03-14.md` |
| Audit | `audit_{date}.jsonl` | `audit_2026-03-14.jsonl` |

---

## 🔐 Security Rules

### Data Handling
- Never store credentials in plain text
- Use environment variables for secrets
- Redact sensitive information in logs
- Encrypt audit logs at rest

### Access Control
- Only approved actions execute
- Rejected items move to `/Rejected/` with reason
- Audit all access attempts
- Implement role-based access (future)

### Privacy
- Respect confidentiality of all communications
- Do not share information across contexts without approval
- Maintain client data privacy
- Comply with GDPR/CCPA requirements

---

## 📊 Task Processing Workflow

### Standard Flow

1. **Perception**: Watcher detects new item → Creates file in `/Needs_Action/`
2. **Reasoning**: AI reads item → Creates plan in `/Plans/`
3. **Approval**: If sensitive → Move to `/Pending_Approval/`
4. **Action**: After approval → Execute via MCP → Move to `/Done/`
5. **Logging**: Record outcome in `/Logs/` and `/Logs/Audit/`

### Task States

| State | Folder | Description |
|-------|--------|-------------|
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
| API failure | Retry 3x with exponential backoff, then log and notify |
| File error | Log details, skip item, continue |
| Network issue | Wait 5 min, retry, open circuit breaker if persistent |
| Authentication | Alert immediately, do not retry |
| Rate limit | Backoff for specified duration, retry |
| Unknown input | Flag for manual review |

### Escalation Rules

1. First failure: Log and retry
2. Second failure: Log with warning
3. Third failure: Create alert task, notify human
4. Circuit breaker: Open after 3 failures in 5 minutes

### Recovery Procedures

1. **Automatic**: Retry with exponential backoff
2. **Manual**: Review error logs, fix configuration
3. **Escalation**: Create critical alert file

---

## 📈 Performance Metrics

### Daily Goals

| Metric | Target |
|--------|--------|
| Task completion rate | > 90% |
| Response time (urgent) | < 1 hour |
| False positive rate | < 5% |
| Approval accuracy | 100% |
| System uptime | > 99% |

### Weekly Review

Every Monday, generate briefing covering:
- Tasks completed (by category)
- Revenue processed (from Odoo)
- Social media performance
- Bottlenecks identified
- Optimization suggestions
- Week-over-week comparison

---

## 🎓 Learning & Improvement

### Feedback Loop

1. Human moves task to `/Rejected/` with reason
2. AI analyzes rejection pattern
3. Update rules in this handbook
4. Apply learning to future tasks

### Continuous Improvement

- Document all edge cases
- Refine keyword detection
- Optimize response templates
- Update priority rules
- Enhance sentiment analysis

---

## 🔗 Integration-Specific Rules

### Odoo ERP

- Sync invoices every 5 minutes
- Validate all invoice creations before posting
- Reconcile payments daily
- Generate financial reports weekly

### Facebook/Instagram

- Monitor messages every 2 minutes
- Respond to urgent messages within 1 hour
- Post content only after approval
- Track engagement metrics daily

### Twitter/X

- Monitor mentions every 2 minutes
- Engage with brand mentions within 4 hours
- Post tweets only after approval
- Track sentiment trends

---

*Handbook version 2.0 (Gold Tier) - Update as system evolves*
