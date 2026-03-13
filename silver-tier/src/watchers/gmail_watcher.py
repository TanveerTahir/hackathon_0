#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important/unread messages.

This watcher uses the Gmail API to check for new emails and creates
markdown action files for messages that require attention.

Setup Requirements:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json to the config folder
4. First run will prompt for authorization

Usage:
    python gmail_watcher.py /path/to/vault
"""

import base64
import os
import sys
from datetime import datetime
from email import message_from_bytes
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add watchers directory to path for base_watcher import
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Try to import Google API libraries
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class GmailWatcher(BaseWatcher):
    """
    Watcher that monitors Gmail for new messages.
    
    When a new email is detected, it:
    1. Fetches the email content
    2. Creates a markdown action file in Needs_Action
    3. Tracks processed message IDs to avoid duplicates
    """

    # OAuth scopes for Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Keywords that indicate high priority
    PRIORITY_KEYWORDS = [
        'urgent', 'asap', 'invoice', 'payment', 'receipt',
        'contract', 'agreement', 'deadline', 'review',
        'action required', 'response needed', 'important'
    ]
    
    # Keywords that indicate financial content
    FINANCIAL_KEYWORDS = [
        'invoice', 'payment', 'receipt', 'bill', 'quote',
        'estimate', 'pricing', 'cost', 'budget', 'transfer'
    ]

    def __init__(
        self,
        vault_path: str,
        credentials_path: str = None,
        check_interval: int = 120
    ):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to Gmail credentials JSON (default: config/gmail_credentials.json)
            check_interval: Seconds between checks (default: 120)
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail watcher requires Google API libraries. "
                "Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
        
        super().__init__(vault_path, check_interval)
        
        # Setup credentials path
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            self.credentials_path = Path(__file__).parent.parent / 'config' / 'gmail_credentials.json'
        
        self.token_path = Path(__file__).parent.parent / 'config' / 'gmail_token.json'
        self.service = None
        self._authenticated = False

    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful
        """
        try:
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path.exists():
                        self.logger.error(
                            f"Credentials file not found: {self.credentials_path}. "
                            "Please set up Gmail API credentials."
                        )
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save token
                self.token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            self._authenticated = True
            self.logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False

    def _decode_message(self, message: Dict[str, Any]) -> Dict[str, str]:
        """
        Decode a Gmail message.

        Args:
            message: Gmail message resource (format='full')

        Returns:
            Dictionary with decoded message fields
        """
        try:
            # Extract headers from payload
            headers = {h['name'].lower(): h['value'] for h in message['payload']['headers']}

            # Extract body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body'].get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                            break
            elif 'body' in message['payload']:
                body_data = message['payload']['body'].get('data', '')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')

            # If still no body, try snippet
            if not body:
                body = message.get('snippet', '')

            return {
                'id': message['id'],
                'thread_id': message.get('threadId', ''),
                'from': headers.get('from', 'Unknown'),
                'to': headers.get('to', ''),
                'subject': headers.get('subject', 'No Subject'),
                'date': headers.get('date', ''),
                'snippet': message.get('snippet', ''),
                'body': body,
                'attachments': len(message['payload'].get('parts', [])) > 0
            }

        except Exception as e:
            self.logger.error(f"Error decoding message: {e}")
            return {
                'id': message.get('id', 'unknown'),
                'from': 'Unknown',
                'subject': 'Error decoding message',
                'snippet': str(e),
                'body': '',
                'attachments': False
            }

    def _detect_priority(self, email_data: Dict[str, str]) -> str:
        """
        Detect priority level based on email content.
        
        Args:
            email_data: Decoded email data
            
        Returns:
            Priority level string
        """
        text_to_check = (
            f"{email_data.get('subject', '')} "
            f"{email_data.get('snippet', '')} "
            f"{email_data.get('from', '')}"
        ).lower()
        
        for keyword in self.PRIORITY_KEYWORDS:
            if keyword in text_to_check:
                return "high"
        
        return "normal"

    def _detect_category(self, email_data: Dict[str, str]) -> str:
        """
        Detect category based on email content.
        
        Args:
            email_data: Decoded email data
            
        Returns:
            Category string
        """
        text_to_check = (
            f"{email_data.get('subject', '')} "
            f"{email_data.get('snippet', '')}"
        ).lower()
        
        for keyword in self.FINANCIAL_KEYWORDS:
            if keyword in text_to_check:
                return "financial"
        
        if 'invoice' in text_to_check or 'receipt' in text_to_check:
            return "financial"
        elif 'contract' in text_to_check or 'agreement' in text_to_check:
            return "legal"
        elif 'meeting' in text_to_check or 'schedule' in text_to_check:
            return "schedule"
        else:
            return "general"

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new messages.
        
        Returns:
            List of new email dictionaries
        """
        new_emails = []
        
        # Authenticate if needed
        if not self._authenticated:
            if not self._authenticate():
                return new_emails
        
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    # Fetch full message with full format to get payload
                    full_message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    # Decode message
                    email_data = self._decode_message(full_message)
                    email_data['priority'] = self._detect_priority(email_data)
                    email_data['category'] = self._detect_category(email_data)
                    
                    new_emails.append(email_data)
                    self.processed_ids.add(msg['id'])
            
        except HttpError as error:
            self.logger.error(f"Gmail API error: {error}")
            self.log_activity(f"Gmail API error: {error}", "error")
        
        return new_emails

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for the email.
        
        Args:
            item: Email data dictionary
            
        Returns:
            Path to the created action file
        """
        # Generate unique ID (first 8 chars of message ID)
        unique_id = item['id'][:8]
        action_filename = self._generate_filename('EMAIL', unique_id)
        action_path = self.needs_action / action_filename
        
        # Build suggested actions based on category
        suggested_actions = self._get_suggested_actions(item['category'], item['priority'])
        
        # Build content
        content = self._build_action_content(item, suggested_actions)
        
        # Write action file
        action_path.write_text(content, encoding='utf-8')
        
        return action_path

    def _get_suggested_actions(self, category: str, priority: str) -> List[str]:
        """
        Get suggested actions based on category and priority.
        
        Args:
            category: Email category
            priority: Priority level
            
        Returns:
            List of suggested action strings
        """
        actions = []
        
        if category == "financial":
            actions = [
                "Review financial details",
                "Verify amounts and dates",
                "Record in accounting system",
                "Reply with confirmation if needed"
            ]
        elif category == "legal":
            actions = [
                "Review legal terms carefully",
                "Check for required actions",
                "Forward to legal review if needed",
                "Archive for records"
            ]
        elif category == "schedule":
            actions = [
                "Check calendar availability",
                "Respond with availability",
                "Add to calendar if confirmed",
                "Send calendar invite if needed"
            ]
        else:
            actions = [
                "Read and understand request",
                "Determine required response",
                "Draft and send reply",
                "Archive after processing"
            ]
        
        if priority == "high":
            actions.insert(0, "⚠️ URGENT: Process immediately")
        
        return actions

    def _build_action_content(self, item: Dict[str, Any], suggested_actions: List[str]) -> str:
        """
        Build the markdown content for the action file.
        
        Args:
            item: Email data dictionary
            suggested_actions: List of suggested actions
            
        Returns:
            Markdown content string
        """
        # Build frontmatter
        frontmatter = self._create_frontmatter(
            item_type="email",
            message_id=f'"{item["id"]}"',
            thread_id=f'"{item.get("thread_id", "")}"',
            sender=f'"{item["from"]}"',
            subject=f'"{item["subject"]}"',
            received=f'"{datetime.now().isoformat()}"',
            category=f'"{item["category"]}"',
            priority=f'"{item["priority"]}"',
            has_attachments=str(item.get("attachments", False)).lower()
        )
        
        # Build suggested actions markdown
        actions_md = "\n".join([f"- [ ] {action}" for action in suggested_actions])
        
        # Truncate body if too long
        body = item.get('body', '')
        if len(body) > 2000:
            body = body[:2000] + "\n\n... [truncated]"
        
        # Build content
        content = f"""{frontmatter}

# 📧 Email: {item['subject']}

## Email Information

| Property | Value |
|----------|-------|
| **From** | {item['from']} |
| **Subject** | {item['subject']} |
| **Received** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |
| **Category** | {item['category']} |
| **Priority** | {item['priority']} |
| **Has Attachments** | {'Yes' if item.get('attachments') else 'No'} |

## Email Content

{body if body else item.get('snippet', 'No content available')}

## Suggested Actions

{actions_md}

## Draft Reply

*Draft your reply here*

---
*Auto-generated by Gmail Watcher*
"""
        return content


def main():
    """Main entry point for running the watcher standalone."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path> [credentials_path]")
        print("  vault_path: Path to Obsidian vault")
        print("  credentials_path: Path to Gmail credentials JSON (optional)")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        watcher = GmailWatcher(vault_path, credentials_path)
        watcher.run()
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        if 'watcher' in locals():
            watcher.stop()


if __name__ == "__main__":
    main()
