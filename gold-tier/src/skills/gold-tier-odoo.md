# Gold Tier Odoo Integration Skill

**Purpose:** Interact with Odoo ERP for accounting, invoices, payments, partners, and financial reports.

## Available Actions

### Connect to Odoo

Test connection to Odoo server:

```
Connect to Odoo and test connection
Check Odoo status
```

### Get Invoices

Retrieve customer invoices:

```
Get recent invoices from Odoo
Show invoices from last 7 days
List unpaid invoices
```

### Create Invoice

Create a new customer invoice:

```
Create invoice for Partner A with 3 line items
Generate invoice for consulting services
```

### Validate Invoice

Post/validate a draft invoice:

```
Validate invoice INV/2026/001
Post this draft invoice
```

### Get Payments

Retrieve payment records:

```
Get recent payments
Show payments from this week
List posted payments
```

### Register Payment

Record payment for an invoice:

```
Register payment of $1000 for invoice INV/2026/001
Record payment received from Customer A
```

### Get Partners

Search business partners:

```
Find partner by name "Acme Corp"
List all customers
Search partners by email
```

### Create Partner

Create new business partner:

```
Create new customer: John Doe, john@example.com
Add vendor: ABC Supplies, abc@supplies.com
```

### Get Products

Search products/services:

```
List available products
Search for "consulting" services
```

### Get Financial Reports

Generate financial reports:

```
Get profit and loss report for Q1
Show balance sheet as of today
```

### Search Records

Search any Odoo model:

```
Search sale.order for recent orders
Find purchase orders from last month
```

## Odoo MCP Tools

The Odoo MCP server provides these tools:

| Tool | Description |
|------|-------------|
| `odoo_connect` | Test connection |
| `odoo_get_invoices` | Get invoices |
| `odoo_create_invoice` | Create invoice |
| `odoo_validate_invoice` | Validate invoice |
| `odoo_get_payments` | Get payments |
| `odoo_register_payment` | Register payment |
| `odoo_get_partners` | Search partners |
| `odoo_create_partner` | Create partner |
| `odoo_get_products` | Search products |
| `odoo_get_financial_reports` | Get reports |
| `odoo_search_records` | Search any model |
| `odoo_read_record` | Read specific record |
| `odoo_create_record` | Create record |
| `odoo_write_record` | Update record |
| `odoo_unlink_record` | Delete record |

## Configuration

Set these environment variables:

```bash
ODOO_URL=http://localhost:8069
ODOO_DB=hackathon_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

## Usage with Claude Code

1. **Reference the skill:**
   ```
   @skills/gold-tier-odoo
   ```

2. **Give commands:**
   ```
   Using the gold-tier-odoo skill, get unpaid invoices
   Create an invoice for the consulting work
   ```

3. **Review output:**
   - Invoice details
   - Payment status
   - Partner information

## Common Workflows

### Invoice Creation Workflow

1. Check if partner exists
2. Create partner if needed
3. Create invoice with line items
4. Validate invoice
5. Send to customer

### Payment Recording Workflow

1. Get unpaid invoices
2. Match payment to invoice
3. Register payment
4. Reconcile accounts

### Financial Review Workflow

1. Get P&L report
2. Get Balance Sheet
3. Review key metrics
4. Generate briefing

## Best Practices

1. **Always validate invoices** before sending
2. **Record payments promptly**
3. **Review financial reports weekly**
4. **Keep partner data updated**
5. **Reconcile accounts regularly**

## Error Handling

If Odoo connection fails:
1. Check Odoo server status
2. Verify credentials
3. Check network connectivity
4. Review error logs

---

*Gold Tier Odoo Integration Skill v1.0*
