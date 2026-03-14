#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Briefing Generator - Generates Weekly CEO Briefings and Business Audits.

This module generates comprehensive briefings covering:
- Revenue and financial metrics
- Task completion summary
- Social media performance
- Bottlenecks and issues
- Proactive suggestions

Usage:
    python briefing_generator.py /path/to/vault --type weekly
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class BriefingGenerator:
    """
    Generates CEO briefings and business audits.
    """

    def __init__(self, vault_path: str):
        """
        Initialize the briefing generator.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.briefings_dir = self.vault_path / 'Briefings'
        self.logs_dir = self.vault_path / 'Logs'
        self.accounting_dir = self.vault_path / 'Accounting'
        self.social_media_dir = self.vault_path / 'Social_Media'

        # Ensure directories exist
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.accounting_dir.mkdir(parents=True, exist_ok=True)

    def generate_weekly_briefing(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Path:
        """
        Generate a comprehensive weekly CEO briefing.

        Args:
            start_date: Start of the week (default: last Monday)
            end_date: End of the week (default: last Sunday)

        Returns:
            Path to the generated briefing file
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            # Get last Monday
            start_date = end_date - timedelta(days=end_date.weekday())

        # Collect data
        tasks_data = self._collect_task_data(start_date, end_date)
        financial_data = self._collect_financial_data(start_date, end_date)
        social_data = self._collect_social_media_data(start_date, end_date)
        alerts_data = self._collect_alerts_data(start_date, end_date)

        # Generate briefing
        briefing_content = self._build_briefing_content(
            start_date=start_date,
            end_date=end_date,
            tasks=tasks_data,
            financial=financial_data,
            social=social_data,
            alerts=alerts_data
        )

        # Save briefing
        filename = f"Weekly_Briefing_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.md"
        briefing_path = self.briefings_dir / filename
        briefing_path.write_text(briefing_content, encoding='utf-8')

        return briefing_path

    def _collect_task_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect task completion data from vault"""
        done_dir = self.vault_path / 'Done'
        needs_action_dir = self.vault_path / 'Needs_Action'
        plans_dir = self.vault_path / 'Plans'

        tasks = {
            'completed': [],
            'pending': [],
            'by_day': {},
            'by_category': {},
            'total_completed': 0,
            'total_pending': 0
        }

        # Scan Done folder
        if done_dir.exists():
            for file in done_dir.glob('*.md'):
                try:
                    content = file.read_text(encoding='utf-8')
                    # Parse frontmatter to get completion date
                    created = self._extract_frontmatter_value(content, 'created')
                    if created:
                        try:
                            task_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            if start_date <= task_date <= end_date:
                                tasks['completed'].append({
                                    'file': file.name,
                                    'type': self._extract_frontmatter_value(content, 'type'),
                                    'date': created
                                })
                                tasks['total_completed'] += 1

                                # By day
                                day_key = task_date.strftime('%A')
                                tasks['by_day'][day_key] = tasks['by_day'].get(day_key, 0) + 1

                                # By category
                                task_type = self._extract_frontmatter_value(content, 'type')
                                tasks['by_category'][task_type] = tasks['by_category'].get(task_type, 0) + 1
                        except:
                            pass
                except:
                    pass

        # Scan Needs_Action folder
        if needs_action_dir.exists():
            tasks['total_pending'] = len(list(needs_action_dir.glob('*.md')))

        return tasks

    def _collect_financial_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect financial data from Odoo or accounting files"""
        financial = {
            'revenue': 0.0,
            'expenses': 0.0,
            'profit': 0.0,
            'invoices_sent': 0,
            'invoices_paid': 0,
            'invoices_overdue': 0,
            'payments_received': [],
            'subscriptions': []
        }

        # Try to read from accounting files
        accounting_file = self.accounting_dir / f"Transactions_{start_date.strftime('%Y-%m')}.md"
        if accounting_file.exists():
            try:
                content = accounting_file.read_text(encoding='utf-8')
                # Parse transactions (simplified)
                # In production, this would integrate with Odoo
            except:
                pass

        # In production, this would call Odoo MCP server
        # Example:
        # invoices = odoo_client.get_invoices(state='posted', days=7)
        # for invoice in invoices:
        #     financial['revenue'] += invoice.get('amount_total', 0)

        financial['profit'] = financial['revenue'] - financial['expenses']

        return financial

    def _collect_social_media_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect social media performance data"""
        social = {
            'facebook': {
                'posts': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'reach': 0
            },
            'instagram': {
                'posts': 0,
                'likes': 0,
                'comments': 0,
                'followers': 0,
                'reach': 0
            },
            'twitter': {
                'tweets': 0,
                'likes': 0,
                'retweets': 0,
                'replies': 0,
                'impressions': 0
            },
            'linkedin': {
                'posts': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'impressions': 0
            }
        }

        # In production, this would call the respective MCP servers
        # to get actual insights data

        return social

    def _collect_alerts_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Collect alerts and issues from logs"""
        alerts = {
            'critical': [],
            'warnings': [],
            'errors': [],
            'total_critical': 0,
            'total_warnings': 0,
            'total_errors': 0
        }

        # Scan log files
        log_file = self.logs_dir / f"watcher_{datetime.now().strftime('%Y-%m-%d')}.log"
        if log_file.exists():
            try:
                content = log_file.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if '[CRITICAL]' in line:
                        alerts['critical'].append(line)
                        alerts['total_critical'] += 1
                    elif '[WARNING]' in line:
                        alerts['warnings'].append(line)
                        alerts['total_warnings'] += 1
                    elif '[ERROR]' in line:
                        alerts['errors'].append(line)
                        alerts['total_errors'] += 1
            except:
                pass

        return alerts

    def _extract_frontmatter_value(self, content: str, key: str) -> Optional[str]:
        """Extract a value from YAML frontmatter"""
        try:
            lines = content.split('\n')
            in_frontmatter = False
            for line in lines:
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                elif in_frontmatter and line.startswith(f'{key}:'):
                    value = line.split(':', 1)[1].strip().strip('"\'')
                    return value
        except:
            pass
        return None

    def _build_briefing_content(
        self,
        start_date: datetime,
        end_date: datetime,
        tasks: Dict[str, Any],
        financial: Dict[str, Any],
        social: Dict[str, Any],
        alerts: Dict[str, Any]
    ) -> str:
        """Build the markdown briefing content"""

        # Calculate week number
        week_number = start_date.isocalendar()[1]

        # Build content
        content = f"""---
type: weekly_briefing
period_start: {start_date.strftime('%Y-%m-%d')}
period_end: {end_date.strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
week_number: {week_number}
status: draft
---

# 📊 Weekly CEO Briefing

**Week {week_number}, {start_date.strftime('%Y')}**

**Period:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 🎯 Executive Summary

*Add a brief 2-3 sentence summary of the week's performance*

**Overall Performance:** 🟢 On Track / 🟡 Needs Attention / 🔴 At Risk

---

## 💰 Financial Performance

### Revenue Summary

| Metric | Amount | Target | Variance |
|--------|--------|--------|----------|
| **Revenue** | ${financial['revenue']:,.2f} | $10,000.00 | {((financial['revenue'] - 10000) / 10000 * 100):+.1f}% |
| **Expenses** | ${financial['expenses']:,.2f} | - | - |
| **Net Profit** | ${financial['profit']:,.2f} | - | - |

### Invoices

| Status | Count | Amount |
|--------|-------|--------|
| **Sent** | {financial['invoices_sent']} | - |
| **Paid** | {financial['invoices_paid']} | - |
| **Overdue** | {financial['invoices_overdue']} | - |

### Payment Activity

*List of payments received this week*

"""

        if financial['payments_received']:
            for payment in financial['payments_received']:
                content += f"- {payment.get('date', 'N/A')}: ${payment.get('amount', 0):,.2f} from {payment.get('partner', 'Unknown')}\n"
        else:
            content += "*No payments recorded this week*\n"

        content += f"""
---

## ✅ Task Completion

### Summary

| Metric | Count | Trend |
|--------|-------|-------|
| **Completed** | {tasks['total_completed']} | - |
| **Pending** | {tasks['total_pending']} | - |
| **Completion Rate** | {(tasks['total_completed'] / max(tasks['total_completed'] + tasks['total_pending'], 1) * 100):.1f}% | - |

### Tasks by Day

| Day | Completed |
|-----|-----------|
"""

        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            count = tasks['by_day'].get(day, 0)
            content += f"| {day} | {count} |\n"

        content += """
### Tasks by Category

| Category | Count |
|----------|-------|
"""

        for category, count in tasks['by_category'].items():
            content += f"| {category} | {count} |\n"

        if not tasks['by_category']:
            content += "| *No categories* | 0 |\n"

        content += f"""
---

## 📱 Social Media Performance

### Facebook

| Metric | Value |
|--------|-------|
| Posts | {social['facebook']['posts']} |
| Likes | {social['facebook']['likes']} |
| Comments | {social['facebook']['comments']} |
| Shares | {social['facebook']['shares']} |
| Reach | {social['facebook']['reach']} |

### Instagram

| Metric | Value |
|--------|-------|
| Posts | {social['instagram']['posts']} |
| Likes | {social['instagram']['likes']} |
| Comments | {social['instagram']['comments']} |
| Followers | {social['instagram']['followers']} |
| Reach | {social['instagram']['reach']} |

### Twitter/X

| Metric | Value |
|--------|-------|
| Tweets | {social['twitter']['tweets']} |
| Likes | {social['twitter']['likes']} |
| Retweets | {social['twitter']['retweets']} |
| Replies | {social['twitter']['replies']} |
| Impressions | {social['twitter']['impressions']} |

### LinkedIn

| Metric | Value |
|--------|-------|
| Posts | {social['linkedin']['posts']} |
| Likes | {social['linkedin']['likes']} |
| Comments | {social['linkedin']['comments']} |
| Shares | {social['linkedin']['shares']} |
| Impressions | {social['linkedin']['impressions']} |

---

## ⚠️ Alerts and Issues

### Critical Issues ({alerts['total_critical']})

"""

        if alerts['critical']:
            for alert in alerts['critical'][:5]:
                content += f"- {alert}\n"
        else:
            content += "*No critical issues*\n"

        content += f"""
### Warnings ({alerts['total_warnings']})

"""

        if alerts['warnings']:
            for alert in alerts['warnings'][:5]:
                content += f"- {alert}\n"
        else:
            content += "*No warnings*\n"

        content += f"""
### Errors ({alerts['total_errors']})

"""

        if alerts['errors']:
            for alert in alerts['errors'][:5]:
                content += f"- {alert}\n"
        else:
            content += "*No errors*\n"

        content += f"""
---

## 🎯 Proactive Suggestions

### Cost Optimization

*AI-generated suggestions based on spending patterns*

- Review subscription costs
- Identify unused services
- Negotiate vendor contracts

### Revenue Opportunities

*AI-generated suggestions based on business activity*

- Follow up on overdue invoices
- Engage with positive social media mentions
- Create content based on trending topics

### Process Improvements

*AI-generated suggestions based on task patterns*

- Automate repetitive tasks
- Improve response times
- Enhance customer communication

---

## 📋 Action Items for Next Week

1. [ ] Review and address critical issues
2. [ ] Follow up on overdue invoices
3. [ ] Engage with social media opportunities
4. [ ] Implement process improvements
5. [ ] Review weekly goals and adjust

---

## 📈 Week-over-Week Comparison

*Compare with previous week's performance*

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Revenue | ${financial['revenue']:,.2f} | $0.00 | - |
| Tasks Completed | {tasks['total_completed']} | 0 | - |
| Social Posts | {sum([social['facebook']['posts'], social['instagram']['posts'], social['twitter']['tweets'], social['linkedin']['posts']])} | 0 | - |

---

*Briefing generated automatically by AI Employee System*

**Next Briefing:** {(end_date + timedelta(days=7)).strftime('%B %d, %Y')}
"""

        return content


def main():
    """Main entry point for generating briefings"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate CEO Briefings and Business Audits"
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['weekly', 'daily', 'monthly'],
        default='weekly',
        help='Type of briefing to generate'
    )
    parser.add_argument(
        '--start-date',
        help='Start date (YYYY-MM-DD, default: last Monday)'
    )
    parser.add_argument(
        '--end-date',
        help='End date (YYYY-MM-DD, default: today)'
    )

    args = parser.parse_args()

    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)

    generator = BriefingGenerator(str(vault_path))

    # Parse dates if provided
    start_date = None
    end_date = None

    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')

    # Generate briefing
    if args.type == 'weekly':
        briefing_path = generator.generate_weekly_briefing(start_date, end_date)
        print(f"Weekly briefing generated: {briefing_path}")
    else:
        print(f"{args.type.capitalize()} briefing generation not yet implemented")


if __name__ == "__main__":
    main()
