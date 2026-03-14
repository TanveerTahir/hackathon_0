#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Accounting Watcher - Monitors Odoo ERP for financial events.

This watcher monitors:
- New invoices created
- Payments received
- Overdue payments
- Budget alerts

Creates action files in /Needs_Action/ for:
- Invoice follow-up required
- Payment reconciliation needed
- Financial review needed

Usage:
    python odoo_watcher.py /path/to/vault
"""

import hashlib
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from watchers.base_watcher import BaseWatcher

# Load environment variables
load_dotenv()

# Configuration
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'hackathon_db')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')


class OdooWatcher(BaseWatcher):
    """
    Watcher that monitors Odoo ERP for accounting events.
    """

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize the Odoo watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300 - 5 minutes)
        """
        super().__init__(vault_path, check_interval)

        # Track processed items
        self.processed_invoice_ids: set = set()
        self.processed_payment_ids: set = set()
        self.last_invoice_check: datetime = datetime.now()
        self.last_payment_check: datetime = datetime.now()

        # Thresholds for alerts
        self.overdue_threshold_days = 7
        self.large_payment_threshold = 1000.0

        # Check if configured
        self.is_configured = all([ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD])
        if not self.is_configured:
            self.logger.warning("Odoo credentials not configured - watcher will run in mock mode")

    def _detect_invoice_priority(self, invoice: Dict[str, Any]) -> str:
        """
        Detect priority level for invoice.

        Args:
            invoice: Invoice data

        Returns:
            Priority level string
        """
        amount = abs(invoice.get('amount_residual', 0))
        state = invoice.get('state', 'draft')
        payment_state = invoice.get('payment_state', 'not_paid')

        # Overdue invoices are high priority
        if payment_state == 'not_paid':
            due_date = invoice.get('invoice_date_due')
            if due_date:
                try:
                    due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    days_overdue = (datetime.now() - due).days
                    if days_overdue > self.overdue_threshold_days:
                        return "high"
                except:
                    pass

        # Large amounts are high priority
        if amount > self.large_payment_threshold:
            return "high"

        # Posted invoices need attention
        if state == 'posted':
            return "normal"

        return "low"

    def _detect_payment_priority(self, payment: Dict[str, Any]) -> str:
        """
        Detect priority level for payment.

        Args:
            payment: Payment data

        Returns:
            Priority level string
        """
        amount = abs(payment.get('amount', 0))

        # Large payments are high priority
        if amount > self.large_payment_threshold:
            return "high"

        return "normal"

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Odoo for new accounting events.

        Returns:
            List of new items to process
        """
        if not self.is_configured:
            return []

        new_items = []

        try:
            # Check for new invoices
            invoices = self._get_new_invoices()
            for invoice in invoices:
                if invoice['id'] not in self.processed_invoice_ids:
                    new_items.append({
                        'type': 'invoice',
                        'source': 'odoo',
                        **invoice
                    })
                    self.processed_invoice_ids.add(invoice['id'])

            # Check for new payments
            payments = self._get_new_payments()
            for payment in payments:
                if payment['id'] not in self.processed_payment_ids:
                    new_items.append({
                        'type': 'payment',
                        'source': 'odoo',
                        **payment
                    })
                    self.processed_payment_ids.add(payment['id'])

            # Check for overdue invoices
            overdue = self._get_overdue_invoices()
            for invoice in overdue:
                if invoice['id'] not in self.processed_invoice_ids:
                    invoice['alert_type'] = 'overdue'
                    new_items.append({
                        'type': 'alert',
                        'source': 'odoo',
                        **invoice
                    })
                    self.processed_invoice_ids.add(invoice['id'])

        except Exception as e:
            self.logger.error(f"Error checking Odoo updates: {e}")
            self.handle_error(e, "Odoo API check failed")

        return new_items

    def _get_new_invoices(self) -> List[Dict[str, Any]]:
        """Get new invoices from Odoo (simplified - would use actual API)"""
        # In production, this would call the Odoo MCP server
        # Example: client.get_invoices(state='posted', days=1)
        return []

    def _get_new_payments(self) -> List[Dict[str, Any]]:
        """Get new payments from Odoo"""
        # In production, this would call the Odoo MCP server
        # Example: client.get_payments(state='posted', days=1)
        return []

    def _get_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Get overdue invoices"""
        # In production, this would call the Odoo MCP server
        return []

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for Odoo accounting event.

        Args:
            item: Activity information dictionary

        Returns:
            Path to the created action file
        """
        # Generate unique ID
        unique_id = str(item.get('id', hashlib.md5(str(item).encode()).hexdigest()[:8]))

        # Determine prefix
        source = item.get('source', 'odoo')
        item_type = item.get('type', 'event')
        alert_type = item.get('alert_type', '')

        if alert_type:
            prefix = f"{source.upper()}_ALERT"
        elif item_type == 'invoice':
            prefix = f"{source.upper()}_INVOICE"
        elif item_type == 'payment':
            prefix = f"{source.upper()}_PAYMENT"
        else:
            prefix = f"{source.upper()}_ACCOUNTING"

        action_filename = self._generate_filename(prefix, unique_id)
        action_path = self.needs_action / action_filename

        # Detect priority
        if item_type == 'invoice':
            priority = self._detect_invoice_priority(item)
        elif item_type == 'payment':
            priority = self._detect_payment_priority(item)
        else:
            priority = "high" if alert_type == 'overdue' else "normal"

        # Get suggested actions
        suggested_actions = self._get_suggested_actions(item_type, alert_type)

        # Build action file content
        content = self._build_action_content(
            item=item,
            priority=priority,
            suggested_actions=suggested_actions
        )

        # Write action file
        action_path.write_text(content, encoding='utf-8')

        return action_path

    def _get_suggested_actions(self, item_type: str, alert_type: str) -> List[str]:
        """
        Get suggested actions based on item type.

        Args:
            item_type: Type of item
            alert_type: Alert type if any

        Returns:
            List of suggested action strings
        """
        actions = []

        if alert_type == 'overdue':
            actions.append("⚠️ URGENT: Invoice is overdue")
            actions.append("Send payment reminder to customer")
            actions.append("Consider follow-up call")
            actions.append("Review credit terms")
        elif item_type == 'invoice':
            actions.append("Review invoice details")
            actions.append("Verify goods/services delivered")
            actions.append("Send invoice to customer")
            actions.append("Track payment status")
        elif item_type == 'payment':
            actions.append("Reconcile payment with invoice")
            actions.append("Update accounting records")
            actions.append("Send payment confirmation")
            actions.append("File payment documentation")
        else:
            actions.append("Review accounting event")
            actions.append("Take appropriate action")

        return actions

    def _build_action_content(
        self,
        item: Dict[str, Any],
        priority: str,
        suggested_actions: List[str]
    ) -> str:
        """
        Build the markdown content for the action file.

        Args:
            item: Activity item
            priority: Priority level
            suggested_actions: List of suggested actions

        Returns:
            Markdown content string
        """
        source = item.get('source', 'odoo').upper()
        item_type = item.get('type', 'event')
        alert_type = item.get('alert_type', '')

        # Invoice/Payment details
        name = item.get('name', 'N/A')
        partner = item.get('partner_id', 'Unknown')
        if isinstance(partner, (list, tuple)) and len(partner) > 1:
            partner = partner[1]  # Odoo returns [id, name]

        amount = item.get('amount_total', item.get('amount', 0))
        amount_residual = item.get('amount_residual', 0)
        state = item.get('state', 'draft')
        payment_state = item.get('payment_state', '')
        invoice_date = item.get('invoice_date', item.get('date', ''))
        due_date = item.get('invoice_date_due', '')

        # Build frontmatter
        frontmatter = self._create_frontmatter(
            item_type=f"{source.lower()}_{item_type}",
            source=f'"{source}"',
            name=f'"{name}"',
            partner=f'"{partner}"',
            amount=f'"{amount}"',
            priority=f'"{priority}"',
            state=f'"{state}"'
        )

        # Build suggested actions markdown
        actions_md = "\n".join([f"- [ ] {action}" for action in suggested_actions])

        # Calculate days overdue if applicable
        days_overdue = ""
        if due_date and payment_state == 'not_paid':
            try:
                due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                days = (datetime.now() - due).days
                if days > 0:
                    days_overdue = f"\n**Days Overdue:** {days}"
            except:
                pass

        # Build content
        content = f"""{frontmatter}

# {source} {item_type.title()}: {name}

## {'⚠️ OVERDUE ALERT' if alert_type == 'overdue' else 'Accounting Event'}

| Property | Value |
|----------|-------|
| **Source** | {source} |
| **Type** | {item_type.title()} |
| **Name/Reference** | {name} |
| **Partner/Customer** | {partner} |
| **Total Amount** | ${amount:,.2f} |
| **Amount Due** | ${amount_residual:,.2f} |
| **State** | {state} |
| **Payment Status** | {payment_state} |
| **Date** | {invoice_date} |
| **Due Date** | {due_date} |
| **Priority** | {priority} |
{days_overdue}

## Suggested Actions

{actions_md}

## Notes

*Add any notes or context here*

## Communication Log

| Date | Action | Notes |
|------|--------|-------|
| | | |

---
*Auto-generated by {source} Watcher*
"""
        return content


def main():
    """Main entry point for running the watcher standalone."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python odoo_watcher.py <vault_path>")
        print("  vault_path: Path to Obsidian vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    watcher = OdooWatcher(vault_path)

    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()


if __name__ == "__main__":
    main()
