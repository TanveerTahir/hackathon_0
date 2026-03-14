#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Watcher - Monitors Facebook Page for messages and engagement.

This watcher monitors:
- New page messages (especially urgent ones)
- New comments on posts
- Negative sentiment posts
- Mention alerts

Creates action files in /Needs_Action/ for:
- Customer service response needed
- Engagement opportunity
- Crisis management

Usage:
    python facebook_watcher.py /path/to/vault
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
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID', '')

# Keywords that indicate urgency
URGENT_KEYWORDS = [
    'urgent', 'asap', 'emergency', 'complaint', 'problem',
    'issue', 'broken', 'not working', 'refund', 'angry',
    'disappointed', 'terrible', 'worst', 'scam', 'fraud'
]

# Keywords for engagement opportunities
ENGAGEMENT_KEYWORDS = [
    'love', 'great', 'awesome', 'excellent', 'amazing',
    'thank', 'helpful', 'recommend', 'best', 'happy'
]


class FacebookWatcher(BaseWatcher):
    """
    Watcher that monitors Facebook Page and Instagram for activity.
    """

    def __init__(self, vault_path: str, check_interval: int = 120):
        """
        Initialize the Facebook watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)

        # Track processed items
        self.processed_message_ids: set = set()
        self.processed_comment_ids: set = set()
        self.processed_post_ids: set = set()

        # Priority keywords
        self.urgent_keywords = URGENT_KEYWORDS
        self.engagement_keywords = ENGAGEMENT_KEYWORDS

        # Check if configured
        self.is_configured = bool(FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID)
        if not self.is_configured:
            self.logger.warning("Facebook credentials not configured - watcher will run in mock mode")

    def _detect_sentiment(self, text: str) -> str:
        """
        Detect sentiment of text based on keywords.

        Args:
            text: Text to analyze

        Returns:
            Sentiment string: 'negative', 'positive', or 'neutral'
        """
        text_lower = text.lower()

        urgent_count = sum(1 for kw in self.urgent_keywords if kw in text_lower)
        engagement_count = sum(1 for kw in self.engagement_keywords if kw in text_lower)

        if urgent_count >= 2:
            return 'negative'
        elif engagement_count >= 1:
            return 'positive'
        else:
            return 'neutral'

    def _detect_priority(self, text: str, sentiment: str) -> str:
        """
        Detect priority level based on content.

        Args:
            text: Text to analyze
            sentiment: Detected sentiment

        Returns:
            Priority level string
        """
        text_lower = text.lower()

        # Check for urgent keywords
        for keyword in self.urgent_keywords:
            if keyword in text_lower:
                return "high"

        # Check sentiment
        if sentiment == 'negative':
            return "high"
        elif sentiment == 'positive':
            return "normal"

        return "low"

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Facebook for new messages, comments, and mentions.

        Returns:
            List of new items to process
        """
        if not self.is_configured:
            # Return mock data for testing
            return self._check_mock_updates()

        new_items = []

        try:
            # Check for new messages
            messages = self._get_facebook_messages()
            for msg in messages:
                if msg['id'] not in self.processed_message_ids:
                    new_items.append({
                        'type': 'message',
                        'source': 'facebook',
                        **msg
                    })
                    self.processed_message_ids.add(msg['id'])

            # Check for new comments on posts
            comments = self._get_post_comments()
            for comment in comments:
                if comment['id'] not in self.processed_comment_ids:
                    new_items.append({
                        'type': 'comment',
                        'source': 'facebook',
                        **comment
                    })
                    self.processed_comment_ids.add(comment['id'])

            # Check Instagram comments if configured
            if INSTAGRAM_ACCOUNT_ID:
                ig_comments = self._get_instagram_comments()
                for comment in ig_comments:
                    if comment['id'] not in self.processed_comment_ids:
                        new_items.append({
                            'type': 'comment',
                            'source': 'instagram',
                            **comment
                        })
                        self.processed_comment_ids.add(comment['id'])

        except Exception as e:
            self.logger.error(f"Error checking Facebook updates: {e}")
            self.handle_error(e, "Facebook API check failed")

        return new_items

    def _get_facebook_messages(self) -> List[Dict[str, Any]]:
        """Get recent Facebook messages (simplified - would use actual API)"""
        # In production, this would call the Facebook MCP server or Graph API
        # For now, return empty list
        return []

    def _get_post_comments(self) -> List[Dict[str, Any]]:
        """Get recent comments on Facebook posts"""
        # In production, this would call the Facebook MCP server
        return []

    def _get_instagram_comments(self) -> List[Dict[str, Any]]:
        """Get recent Instagram comments"""
        # In production, this would call the Instagram API
        return []

    def _check_mock_updates(self) -> List[Dict[str, Any]]:
        """Generate mock updates for testing (when not configured)"""
        # This allows testing the watcher without actual API credentials
        return []

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for the Facebook/Instagram activity.

        Args:
            item: Activity information dictionary

        Returns:
            Path to the created action file
        """
        # Generate unique ID
        unique_id = item.get('id', hashlib.md5(str(item).encode()).hexdigest()[:8])

        # Determine prefix based on type and source
        source = item.get('source', 'facebook')
        item_type = item.get('type', 'message')

        if item_type == 'message':
            prefix = f"{source.upper()}_MSG"
        elif item_type == 'comment':
            prefix = f"{source.upper()}_COMMENT"
        else:
            prefix = f"{source.upper()}_ACTIVITY"

        action_filename = self._generate_filename(prefix, unique_id)
        action_path = self.needs_action / action_filename

        # Detect sentiment and priority
        text = item.get('text', item.get('message', ''))
        sentiment = self._detect_sentiment(text)
        priority = self._detect_priority(text, sentiment)

        # Get suggested actions based on sentiment and type
        suggested_actions = self._get_suggested_actions(item_type, sentiment, priority)

        # Build action file content
        content = self._build_action_content(
            item=item,
            sentiment=sentiment,
            priority=priority,
            suggested_actions=suggested_actions
        )

        # Write action file
        action_path.write_text(content, encoding='utf-8')

        return action_path

    def _get_suggested_actions(self, item_type: str, sentiment: str, priority: str) -> List[str]:
        """
        Get suggested actions based on item type and sentiment.

        Args:
            item_type: Type of item (message, comment)
            sentiment: Detected sentiment
            priority: Priority level

        Returns:
            List of suggested action strings
        """
        actions = []

        if sentiment == 'negative' or priority == 'high':
            actions.append("⚠️ URGENT: Respond immediately")
            actions.append("Assess situation and escalate if needed")
            actions.append("Draft empathetic response")
            actions.append("Consider moving conversation to private channel")
        elif sentiment == 'positive':
            actions.append("Engage with positive feedback")
            actions.append("Thank the user")
            actions.append("Consider sharing as testimonial")
        else:
            actions.append("Review and respond appropriately")
            actions.append("Provide helpful information")

        if item_type == 'message':
            actions.append("Check conversation history")
            actions.append("Determine if requires immediate response")
        elif item_type == 'comment':
            actions.append("Check post context")
            actions.append("Determine if public response needed")

        return actions

    def _build_action_content(
        self,
        item: Dict[str, Any],
        sentiment: str,
        priority: str,
        suggested_actions: List[str]
    ) -> str:
        """
        Build the markdown content for the action file.

        Args:
            item: Activity item
            sentiment: Detected sentiment
            priority: Priority level
            suggested_actions: List of suggested actions

        Returns:
            Markdown content string
        """
        source = item.get('source', 'facebook').upper()
        item_type = item.get('type', 'activity')
        text = item.get('text', item.get('message', 'No content'))
        author = item.get('author', item.get('from', 'Unknown'))
        created_time = item.get('created_time', datetime.now().isoformat())

        # Build frontmatter
        frontmatter = self._create_frontmatter(
            item_type=f"{source.lower()}_{item_type}",
            source=f'"{source}"',
            author=f'"{author}"',
            sentiment=f'"{sentiment}"',
            priority=f'"{priority}"',
            created_time=f'"{created_time}"'
        )

        # Build suggested actions markdown
        actions_md = "\n".join([f"- [ ] {action}" for action in suggested_actions])

        # Build content
        content = f"""{frontmatter}

# {source} {item_type.title()}: Response Required

## Activity Information

| Property | Value |
|----------|-------|
| **Source** | {source} |
| **Type** | {item_type.title()} |
| **From** | {author} |
| **Received** | {created_time} |
| **Sentiment** | {sentiment} |
| **Priority** | {priority} |

## Content

{text}

## Suggested Actions

{actions_md}

## Response Draft

*Draft your response here*

---
## Notes

*Add any additional context or notes here*

---
*Auto-generated by {source} Watcher*
"""
        return content


def main():
    """Main entry point for running the watcher standalone."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python facebook_watcher.py <vault_path>")
        print("  vault_path: Path to Obsidian vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    watcher = FacebookWatcher(vault_path)

    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()


if __name__ == "__main__":
    main()
