#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Watcher - Monitors Twitter/X for mentions and engagement.

This watcher monitors:
- Brand mentions
- Keyword alerts
- Competitor activity
- Industry trends

Creates action files for:
- Response to mentions needed
- Engagement opportunities
- Trending topics to leverage

Usage:
    python twitter_watcher.py /path/to/vault
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
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')

# Keywords to monitor (customize for your business)
MONITOR_KEYWORDS = [
    'your_brand',
    'your_product',
    'your_service',
    # Add your brand/product names
]

# Competitor keywords
COMPETITOR_KEYWORDS = [
    'competitor1',
    'competitor2',
    # Add competitor names
]

# Industry keywords
INDUSTRY_KEYWORDS = [
    'your_industry',
    'your_niche',
    # Add industry terms
]


class TwitterWatcher(BaseWatcher):
    """
    Watcher that monitors Twitter/X for mentions and activity.
    """

    def __init__(self, vault_path: str, check_interval: int = 120):
        """
        Initialize the Twitter watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)

        # Track processed items
        self.processed_tweet_ids: set = set()

        # Keywords to monitor
        self.monitor_keywords = MONITOR_KEYWORDS
        self.competitor_keywords = COMPETITOR_KEYWORDS
        self.industry_keywords = INDUSTRY_KEYWORDS

        # Check if configured
        self.is_configured = bool(TWITTER_BEARER_TOKEN)
        if not self.is_configured:
            self.logger.warning("Twitter credentials not configured - watcher will run in mock mode")

    def _categorize_tweet(self, text: str) -> str:
        """
        Categorize tweet based on content.

        Args:
            text: Tweet text

        Returns:
            Category string: 'mention', 'competitor', 'industry', 'other'
        """
        text_lower = text.lower()

        for keyword in self.monitor_keywords:
            if keyword.lower() in text_lower:
                return 'mention'

        for keyword in self.competitor_keywords:
            if keyword.lower() in text_lower:
                return 'competitor'

        for keyword in self.industry_keywords:
            if keyword.lower() in text_lower:
                return 'industry'

        return 'other'

    def _detect_priority(self, text: str, category: str) -> str:
        """
        Detect priority level based on content.

        Args:
            text: Tweet text
            category: Tweet category

        Returns:
            Priority level string
        """
        text_lower = text.lower()

        # Urgent keywords
        urgent_keywords = ['complaint', 'problem', 'issue', 'angry', 'refund', 'scam']
        for keyword in urgent_keywords:
            if keyword in text_lower:
                return "high"

        # Category-based priority
        if category == 'mention':
            return "normal"
        elif category == 'competitor':
            return "low"
        elif category == 'industry':
            return "low"

        return "low"

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Twitter for new mentions and relevant tweets.

        Returns:
            List of new items to process
        """
        if not self.is_configured:
            return []

        new_items = []

        try:
            # Get mentions
            mentions = self._get_mentions()
            for mention in mentions:
                if mention['id'] not in self.processed_tweet_ids:
                    mention['category'] = 'mention'
                    new_items.append({
                        'type': 'mention',
                        'source': 'twitter',
                        **mention
                    })
                    self.processed_tweet_ids.add(mention['id'])

            # Search for brand keywords
            brand_tweets = self._search_tweets(self.monitor_keywords)
            for tweet in brand_tweets:
                if tweet['id'] not in self.processed_tweet_ids:
                    tweet['category'] = 'mention'
                    new_items.append({
                        'type': 'mention',
                        'source': 'twitter',
                        **tweet
                    })
                    self.processed_tweet_ids.add(tweet['id'])

            # Search for competitor tweets (competitive intelligence)
            competitor_tweets = self._search_tweets(self.competitor_keywords)
            for tweet in competitor_tweets:
                if tweet['id'] not in self.processed_tweet_ids:
                    tweet['category'] = 'competitor'
                    new_items.append({
                        'type': 'intelligence',
                        'source': 'twitter',
                        **tweet
                    })
                    self.processed_tweet_ids.add(tweet['id'])

        except Exception as e:
            self.logger.error(f"Error checking Twitter updates: {e}")
            self.handle_error(e, "Twitter API check failed")

        return new_items

    def _get_mentions(self) -> List[Dict[str, Any]]:
        """Get recent mentions (simplified - would use actual API)"""
        # In production, this would call the Twitter MCP server
        return []

    def _search_tweets(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search tweets by keywords"""
        # In production, this would call the Twitter MCP server
        return []

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for Twitter activity.

        Args:
            item: Activity information dictionary

        Returns:
            Path to the created action file
        """
        # Generate unique ID
        unique_id = item.get('id', hashlib.md5(str(item).encode()).hexdigest()[:8])

        # Determine prefix
        source = item.get('source', 'twitter')
        item_type = item.get('type', 'activity')
        category = item.get('category', 'other')

        prefix = f"{source.upper()}_{category.upper()}"

        action_filename = self._generate_filename(prefix, unique_id)
        action_path = self.needs_action / action_filename

        # Detect priority
        text = item.get('text', '')
        priority = self._detect_priority(text, category)

        # Get suggested actions
        suggested_actions = self._get_suggested_actions(item_type, category)

        # Build action file content
        content = self._build_action_content(
            item=item,
            priority=priority,
            suggested_actions=suggested_actions
        )

        # Write action file
        action_path.write_text(content, encoding='utf-8')

        return action_path

    def _get_suggested_actions(self, item_type: str, category: str) -> List[str]:
        """
        Get suggested actions based on item type and category.

        Args:
            item_type: Type of item
            category: Tweet category

        Returns:
            List of suggested action strings
        """
        actions = []

        if category == 'mention':
            actions.append("Review mention context")
            actions.append("Determine if response needed")
            actions.append("Draft appropriate response")
            actions.append("Consider engagement opportunity")
        elif category == 'competitor':
            actions.append("Analyze competitive intelligence")
            actions.append("Document insights")
            actions.append("Consider strategic response")
        elif category == 'industry':
            actions.append("Review industry trend")
            actions.append("Consider content opportunity")
            actions.append("Share with team if relevant")
        else:
            actions.append("Review tweet")
            actions.append("Determine action needed")

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
        source = item.get('source', 'twitter').upper()
        item_type = item.get('type', 'activity')
        category = item.get('category', 'other')
        text = item.get('text', 'No content')
        author = item.get('author', {})
        author_name = author.get('username', author.get('name', 'Unknown'))
        created_time = item.get('created_at', datetime.now().isoformat())
        metrics = item.get('metrics', {})

        # Build frontmatter
        frontmatter = self._create_frontmatter(
            item_type=f"{source.lower()}_{item_type}",
            source=f'"{source}"',
            category=f'"{category}"',
            author=f'"{author_name}"',
            priority=f'"{priority}"',
            created_time=f'"{created_time}"'
        )

        # Build suggested actions markdown
        actions_md = "\n".join([f"- [ ] {action}" for action in suggested_actions])

        # Build content
        content = f"""{frontmatter}

# {source} {item_type.title()}: {category.title()}

## Tweet Information

| Property | Value |
|----------|-------|
| **Source** | {source} |
| **Type** | {item_type.title()} |
| **Category** | {category.title()} |
| **From** | @{author_name} |
| **Received** | {created_time} |
| **Priority** | {priority} |

## Tweet Content

{text}

## Engagement Metrics

| Metric | Value |
|--------|-------|
| **Likes** | {metrics.get('like_count', 0)} |
| **Retweets** | {metrics.get('retweet_count', 0)} |
| **Replies** | {metrics.get('reply_count', 0)} |
| **Impressions** | {metrics.get('impression_count', 0)} |

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
        print("Usage: python twitter_watcher.py <vault_path>")
        print("  vault_path: Path to Obsidian vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    watcher = TwitterWatcher(vault_path)

    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()


if __name__ == "__main__":
    main()
