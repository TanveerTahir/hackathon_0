"""
Watcher Skills - Perception Layer for AI Employee

This module contains skills for monitoring external sources and detecting
new tasks, messages, and events that require AI attention.

Silver Tier Implementation - Personal AI Employee Hackathon 0
"""

from typing import Any, Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime, timedelta
import re
import json
import logging
import time

from ..core.base_skill import BaseSkill, SkillExecutionError


class GoogleWatcherSkill(BaseSkill):
    """
    Skill: google_watcher_skill
    
    Monitors Google Alerts, Search results, and Gmail for new tasks or triggers.
    
    Input:
        - watch_type: str - Type of Google service to watch (alerts, search, gmail)
        - keywords: list - Keywords to monitor
        - since: str - ISO timestamp to check since
        - credentials_path: str - Path to Google credentials
    
    Output:
        - success: bool
        - data: dict containing:
            - new_items: list of detected items
            - watch_type: str
            - keywords_matched: list
            - last_check: str (ISO format)
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="google_watcher_skill",
            description="Monitor Google services (Alerts, Search, Gmail) for new tasks",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.credentials_path = self.config.get("credentials_path")
        self.check_interval = self.config.get("check_interval", 300)  # 5 minutes
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "watch_type": {
                    "type": "string",
                    "description": "Google service to watch",
                    "enum": ["alerts", "search", "gmail"]
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to monitor"
                },
                "since": {
                    "type": "string",
                    "description": "ISO timestamp to check since"
                },
                "credentials_path": {
                    "type": "string",
                    "description": "Path to Google credentials file"
                }
            },
            "required": ["watch_type", "keywords"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "new_items": {"type": "array"},
                        "watch_type": {"type": "string"},
                        "keywords_matched": {"type": "array"},
                        "last_check": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the Google watcher skill"""
        try:
            watch_type = kwargs.get("watch_type", "alerts")
            keywords = kwargs.get("keywords", [])
            since = kwargs.get("since")
            credentials_path = kwargs.get("credentials_path", self.credentials_path)
            
            if not keywords:
                raise SkillExecutionError("keywords are required")
            
            # Simulate watching (actual implementation would use Google APIs)
            new_items = self._check_google_service(watch_type, keywords, since)
            
            # Find matched keywords
            matched_keywords = self._find_matched_keywords(new_items, keywords)
            
            result = {
                "new_items": new_items,
                "watch_type": watch_type,
                "keywords_matched": matched_keywords,
                "last_check": datetime.now().isoformat(),
                "items_count": len(new_items)
            }
            
            # Create action files for new items
            if new_items:
                self._create_action_files(new_items, watch_type)
            
            self._write_log({
                "action": "google_watch",
                "watch_type": watch_type,
                "keywords": keywords,
                "items_found": len(new_items),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error in Google watcher: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _check_google_service(self, watch_type: str, keywords: List[str], since: str) -> List[Dict]:
        """Check Google service for new items"""
        # This is a simulation - actual implementation would use Google APIs
        # For Gmail: google-api-python-client
        # For Alerts: google-alerts-api (unofficial)
        # For Search: google-custom-search-api
        
        self.logger.info(f"Checking Google {watch_type} for keywords: {keywords}")
        
        # Simulated results
        items = []
        
        # In production, this would call actual Google APIs
        # Example for Gmail:
        # service = build('gmail', 'v1', credentials=creds)
        # results = service.users().messages().list(userId='me', q=query).execute()
        
        return items
    
    def _find_matched_keywords(self, items: List[Dict], keywords: List[str]) -> List[str]:
        """Find which keywords were matched"""
        matched = set()
        for item in items:
            text = f"{item.get('title', '')} {item.get('content', '')}".lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    matched.add(keyword)
        return list(matched)
    
    def _create_action_files(self, items: List[Dict], watch_type: str) -> None:
        """Create action files in Needs_Action folder"""
        if not self.vault_path:
            return
        
        needs_action = self.vault_path / "Needs_Action"
        needs_action.mkdir(exist_ok=True)
        
        for item in items:
            filename = f"GOOGLE_{watch_type.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{item.get('id', 'unknown')}.md"
            filepath = needs_action / filename
            
            content = f"""---
type: google_{watch_type}
source: Google {watch_type.title()}
detected: {datetime.now().isoformat()}
priority: normal
status: pending
keywords: {', '.join(item.get('matched_keywords', []))}
---

# Google {watch_type.title()} Alert

## Title
{item.get('title', 'No title')}

## Content
{item.get('content', 'No content')}

## Source
{item.get('source_url', 'No URL')}

## Suggested Actions
- [ ] Review content
- [ ] Take necessary action
- [ ] Archive after processing
"""
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created action file: {filepath}")


class LinkedInWatcherSkill(BaseSkill):
    """
    Skill: linkedin_watcher_skill

    Monitors LinkedIn for updates, opportunities, messages, and engagement.
    Uses Playwright for browser automation with persistent session.
    Credentials loaded from .qwen/.env file.

    Input:
        - watch_types: list - Types to watch (messages, posts, jobs, connections)
        - keywords: list - Keywords to monitor in posts/jobs
        - check_engagement: bool - Whether to check post engagement
        - session_cookie: str - LinkedIn session cookie (for automation)

    Output:
        - success: bool
        - data: dict containing:
            - new_messages: list
            - relevant_posts: list
            - job_opportunities: list
            - connection_requests: list
            - engagement_summary: dict
        - error: str (if failed)
    """

    # LinkedIn selectors (may need updates as LinkedIn changes UI)
    SELECTORS = {
        "messaging": {
            "button": '[aria-label*="Messaging"]',
            "list": '[data-id="conversations-list"]',
            "conversation": '.conversation-card',
            "message_text": '.msg-text',
            "sender_name": '.msg-sender__name',
            "unread_indicator": '[aria-label*="unread"]'
        },
        "feed": {
            "container": 'div[id="feed"]',
            "post": '.feed-shared-update-v2',
            "content": '.update-v2__commentary',
            "author": '.update-v2__actor'
        },
        "jobs": {
            "container": '#jobs-featured-results-list',
            "job_card": '.job-card-list',
            "title": '.job-card-list__title',
            "company": '.artdeco-entity-lockup__subtitle'
        },
        "network": {
            "button": '[aria-label*="My Network"]',
            "invitation": '.invitation-card',
            "name": '.invitation-card__actor-name'
        }
    }

    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="linkedin_watcher_skill",
            description="Monitor LinkedIn for updates, opportunities, and engagement using browser automation",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )

        # Note: LinkedIn Watcher uses browser automation (Playwright), not API credentials
        # Authentication is handled through browser session stored in session_path
        self.session_cookie = self.config.get("session_cookie")
        self.check_interval = self.config.get("check_interval", 600)  # 10 minutes
        self.keywords = self.config.get("keywords", ["hiring", "opportunity", "project"])
        
        # Setup session path
        if vault_path:
            self.vault_path_obj = Path(vault_path)
            self.session_path = self.vault_path_obj / ".linkedin_session"
            self.needs_action = self.vault_path_obj / "Needs_Action"
            self.state_dir = self.vault_path_obj / ".state"
            
            # Ensure directories exist
            for folder in [self.session_path, self.needs_action, self.state_dir]:
                folder.mkdir(parents=True, exist_ok=True)
            
            # Load processed items
            self.processed_items = self._load_processed_items()
        else:
            self.processed_items = set()

    def _load_processed_items(self) -> Set[str]:
        """Load set of processed item IDs from state file."""
        state_file = self.state_dir / "linkedin_processed.json"
        
        if not state_file.exists():
            return set()
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Clean old entries (older than 7 days)
                cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
                cleaned = {k: v for k, v in data.items() if v > cutoff}
                
                # Save cleaned data
                with open(state_file, 'w', encoding='utf-8') as f2:
                    json.dump(cleaned, f2, indent=2)
                
                return set(cleaned.keys())
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return set()
    
    def _save_processed_items(self):
        """Save processed item IDs to state file."""
        state_file = self.state_dir / "linkedin_processed.json"
        
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_items), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
    
    def _is_new_item(self, item_type: str, identifier: str) -> bool:
        """Check if item is new (not processed before)."""
        item_id = f"{item_type}_{identifier}"
        is_new = item_id not in self.processed_items
        
        if is_new:
            self.processed_items.add(item_id)
            self._save_processed_items()
        
        return is_new
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "watch_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["messages", "posts", "jobs", "connections"]
                    },
                    "description": "Types of LinkedIn content to watch"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to monitor"
                },
                "check_engagement": {
                    "type": "boolean",
                    "description": "Check post engagement metrics"
                },
                "session_cookie": {
                    "type": "string",
                    "description": "LinkedIn session cookie for automation"
                }
            },
            "required": ["watch_types"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "new_messages": {"type": "array"},
                        "relevant_posts": {"type": "array"},
                        "job_opportunities": {"type": "array"},
                        "connection_requests": {"type": "array"},
                        "engagement_summary": {"type": "object"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the LinkedIn watcher skill"""
        try:
            watch_types = kwargs.get("watch_types", ["messages", "posts"])
            keywords = kwargs.get("keywords", self.keywords)
            check_engagement = kwargs.get("check_engagement", False)
            session_cookie = kwargs.get("session_cookie", self.session_cookie)

            results = {
                "new_messages": [],
                "relevant_posts": [],
                "job_opportunities": [],
                "connection_requests": [],
                "engagement_summary": {}
            }

            # Use Playwright for browser automation
            try:
                from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

                with sync_playwright() as p:
                    # Launch browser with persistent session and anti-detection settings
                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=str(self.session_path),
                        headless=True,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-web-security',
                            '--disable-features=IsolateOrigins,site-per-process',
                            '--disable-extensions',
                            '--disable-background-networking',
                            '--disable-default-apps',
                            '--disable-sync'
                        ],
                        ignore_default_args=['--enable-automation']
                    )
                    
                    if len(browser.pages) > 0:
                        page = browser.pages[0]
                    else:
                        page = browser.new_page()
                    
                    # Navigate to LinkedIn
                    page.goto('https://www.linkedin.com', timeout=60000)
                    time.sleep(3)
                    
                    # Check if logged in
                    try:
                        page.wait_for_selector('[data-control-name="topbar_post"]', timeout=10000)
                        self.logger.info("Session valid - logged in")
                    except PlaywrightTimeout:
                        self.logger.warning("Session may have expired - manual login required")
                        # Give time for login in interactive mode
                        try:
                            page.wait_for_selector('[data-control-name="topbar_post"]', timeout=120000)
                            self.logger.info("Login successful")
                        except PlaywrightTimeout:
                            self.logger.error("Login timeout - please login manually")
                            browser.close()
                            return {"success": False, "data": None, "error": "LinkedIn login required"}
                    
                    # Check each watch type
                    if "messages" in watch_types:
                        results["new_messages"] = self._check_messages(page)

                    if "posts" in watch_types:
                        results["relevant_posts"] = self._check_posts(keywords, page)

                    if "jobs" in watch_types:
                        results["job_opportunities"] = self._check_jobs(keywords, page)

                    if "connections" in watch_types:
                        results["connection_requests"] = self._check_connections(page)

                    browser.close()
                    
            except ImportError:
                return {"success": False, "data": None, "error": "Playwright not installed"}

            # Create action files for important items
            self._create_action_files(results)

            self._write_log({
                "action": "linkedin_watch",
                "watch_types": watch_types,
                "messages_found": len(results["new_messages"]),
                "posts_found": len(results["relevant_posts"]),
                "jobs_found": len(results["job_opportunities"]),
                "success": True
            })

            return {"success": True, "data": results, "error": None}

        except Exception as e:
            error_msg = f"Error in LinkedIn watcher: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}

    def _check_messages(self, page) -> List[Dict]:
        """Check for new LinkedIn messages using Playwright"""
        self.logger.info("Checking LinkedIn messages...")
        messages = []

        try:
            # Navigate to messaging
            page.goto('https://www.linkedin.com/messaging/', timeout=30000)
            time.sleep(3)

            # Wait for conversation list
            try:
                page.wait_for_selector(self.SELECTORS["messaging"]["list"], timeout=10000)
            except:
                self.logger.warning("Could not find messaging interface")
                return messages

            # Get conversations
            conversations = page.query_selector_all(self.SELECTORS["messaging"]["conversation"])

            for conv in conversations[:10]:
                try:
                    # Check if unread
                    unread = conv.query_selector(self.SELECTORS["messaging"]["unread_indicator"])
                    if not unread:
                        continue

                    # Get sender name
                    sender_elem = conv.query_selector(self.SELECTORS["messaging"]["sender_name"])
                    sender = sender_elem.inner_text() if sender_elem else "Unknown"

                    # Get message preview
                    message_elem = conv.query_selector(self.SELECTORS["messaging"]["message_text"])
                    content = message_elem.inner_text() if message_elem else ""

                    # Check if new
                    if not self._is_new_item("message", sender + content[:50]):
                        continue

                    # Check for keywords
                    matched_keywords = self._find_matched_keywords(content)

                    if matched_keywords:
                        messages.append({
                            "sender": sender,
                            "content": content,
                            "url": "https://www.linkedin.com/messaging/",
                            "matched_keywords": matched_keywords
                        })

                except Exception as e:
                    self.logger.debug(f"Error processing conversation: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error checking messages: {e}")

        return messages

    def _check_posts(self, keywords: List[str], page) -> List[Dict]:
        """Check for relevant posts using Playwright"""
        self.logger.info(f"Checking LinkedIn posts for keywords: {keywords}")
        posts = []

        try:
            # Navigate to feed
            page.goto('https://www.linkedin.com/feed/', timeout=30000)
            time.sleep(3)

            # Wait for feed container
            try:
                page.wait_for_selector(self.SELECTORS["feed"]["container"], timeout=10000)
            except:
                self.logger.warning("Could not find feed")
                return posts

            # Get posts
            post_elements = page.query_selector_all(self.SELECTORS["feed"]["post"])

            for post_elem in post_elements[:20]:
                try:
                    # Get content
                    content_elem = post_elem.query_selector(self.SELECTORS["feed"]["content"])
                    content = content_elem.inner_text() if content_elem else ""

                    # Get author
                    author_elem = post_elem.query_selector(self.SELECTORS["feed"]["author"])
                    author = author_elem.inner_text() if author_elem else "Unknown"

                    # Check if new
                    if not self._is_new_item("post", content[:100]):
                        continue

                    # Check for keywords
                    matched_keywords = self._find_matched_keywords(content)

                    if matched_keywords:
                        posts.append({
                            "author": author,
                            "content": content[:500],
                            "url": "https://www.linkedin.com/feed/",
                            "matched_keywords": matched_keywords,
                            "posted_time": "Recent"
                        })

                except Exception as e:
                    self.logger.debug(f"Error processing post: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error checking posts: {e}")

        return posts

    def _check_jobs(self, keywords: List[str], page) -> List[Dict]:
        """Check for job opportunities using Playwright"""
        self.logger.info(f"Checking LinkedIn jobs for keywords: {keywords}")
        jobs = []

        try:
            # Navigate to jobs
            page.goto('https://www.linkedin.com/jobs/', timeout=30000)
            time.sleep(3)

            # Search for jobs with keywords
            search_box = page.query_selector('input[aria-label="Search by title, skill, or company"]')
            if search_box:
                search_box.fill(" ".join(keywords[:3]))
                page.keyboard.press("Enter")
                time.sleep(3)

            # Get job listings
            job_elements = page.query_selector_all(self.SELECTORS["jobs"]["job_card"])

            for job_elem in job_elements[:10]:
                try:
                    # Get title
                    title_elem = job_elem.query_selector(self.SELECTORS["jobs"]["title"])
                    title = title_elem.inner_text() if title_elem else "Unknown"

                    # Get company
                    company_elem = job_elem.query_selector(self.SELECTORS["jobs"]["company"])
                    company = company_elem.inner_text() if company_elem else "Unknown"

                    # Check if new
                    if not self._is_new_item("job", title + company):
                        continue

                    # Check for keywords
                    job_text = f"{title} {company}".lower()
                    matched_keywords = [kw for kw in keywords if kw.lower() in job_text]

                    if matched_keywords:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": "Not specified",
                            "description": "See job posting for details",
                            "url": "https://www.linkedin.com/jobs/",
                            "matched_keywords": matched_keywords
                        })

                except Exception as e:
                    self.logger.debug(f"Error processing job: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error checking jobs: {e}")

        return jobs

    def _check_connections(self, page) -> List[Dict]:
        """Check for connection requests using Playwright"""
        self.logger.info("Checking LinkedIn connection requests...")
        connections = []

        try:
            # Navigate to network
            page.goto('https://www.linkedin.com/mynetwork/', timeout=30000)
            time.sleep(3)

            # Get invitations
            invitation_elements = page.query_selector_all(self.SELECTORS["network"]["invitation"])

            for inv_elem in invitation_elements[:10]:
                try:
                    # Get name
                    name_elem = inv_elem.query_selector(self.SELECTORS["network"]["name"])
                    name = name_elem.inner_text() if name_elem else "Unknown"

                    # Check if new
                    if not self._is_new_item("connection", name):
                        continue

                    connections.append({
                        "name": name,
                        "title": "See profile",
                        "company": "See profile",
                        "note": "See invitation"
                    })

                except Exception as e:
                    self.logger.debug(f"Error processing invitation: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error checking connections: {e}")

        return connections

    def _check_engagement(self, session_cookie: str) -> Dict:
        """Check post engagement metrics (placeholder)"""
        self.logger.info("Checking LinkedIn engagement metrics")
        return {
            "total_impressions": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0
        }

    def _find_matched_keywords(self, text: str) -> List[str]:
        """Find which keywords were matched in text"""
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw.lower() in text_lower]

    def _create_action_files(self, results: Dict) -> None:
        """Create action files for important LinkedIn items"""
        if not self.vault_path:
            return

        needs_action = self.vault_path / "Needs_Action"
        needs_action.mkdir(exist_ok=True)

        # Create files for new messages
        for message in results.get("new_messages", []):
            filename = f"LINKEDIN_MESSAGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = needs_action / filename

            content = f"""---
type: linkedin_message
from: {message.get('sender', 'Unknown')}
received: {datetime.now().isoformat()}
priority: normal
status: pending
conversation_url: {message.get('url', 'N/A')}
---

# LinkedIn Message

## From
**{message.get('sender', 'Unknown')}**

## Content
{message.get('content', 'No content')}

## Matched Keywords
{', '.join(message.get('matched_keywords', []))}

## Suggested Actions
- [ ] Review message
- [ ] Draft response
- [ ] Archive after processing

---
*Detected by LinkedIn Watcher v1.0*
"""
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created message action file: {filename}")

        # Create files for job opportunities
        for job in results.get("job_opportunities", []):
            filename = f"LINKEDIN_JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = needs_action / filename

            content = f"""---
type: linkedin_job
company: {job.get('company', 'Unknown')}
title: {job.get('title', 'Unknown')}
detected: {datetime.now().isoformat()}
priority: normal
status: pending
job_url: {job.get('url', 'N/A')}
---

# LinkedIn Job Opportunity

## Position
**{job.get('title', 'Unknown')}** at **{job.get('company', 'Unknown')}**

## Matched Keywords
{', '.join(job.get('matched_keywords', []))}

## Suggested Actions
- [ ] Review opportunity
- [ ] Check requirements match
- [ ] Consider applying
- [ ] Archive if not relevant

---
*Detected by LinkedIn Watcher v1.0*
"""
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created job action file: {filename}")

        # Create files for relevant posts
        for post in results.get("relevant_posts", []):
            filename = f"LINKEDIN_POST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = needs_action / filename

            content = f"""---
type: linkedin_post
author: {post.get('author', 'Unknown')}
posted: {post.get('posted_time', 'Unknown')}
detected: {datetime.now().isoformat()}
priority: normal
status: pending
post_url: {post.get('url', 'N/A')}
---

# LinkedIn Post

## Author
**{post.get('author', 'Unknown')}**

## Content
{post.get('content', 'No content')}

## Matched Keywords
{', '.join(post.get('matched_keywords', []))}

## Suggested Actions
- [ ] Review post
- [ ] Engage if relevant (like/comment)
- [ ] Archive after processing

---
*Detected by LinkedIn Watcher v1.0*
"""
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created post action file: {filename}")

        # Create files for connection requests
        for connection in results.get("connection_requests", []):
            filename = f"LINKEDIN_CONNECTION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = needs_action / filename

            content = f"""---
type: linkedin_connection
from: {connection.get('name', 'Unknown')}
title: {connection.get('title', 'Not specified')}
company: {connection.get('company', 'Not specified')}
detected: {datetime.now().isoformat()}
priority: normal
status: pending
---

# LinkedIn Connection Request

## From
**{connection.get('name', 'Unknown')}**

## Title
{connection.get('title', 'Not specified')}

## Company
{connection.get('company', 'Not specified')}

## Suggested Actions
- [ ] Review profile
- [ ] Accept or decline
- [ ] Archive after processing

---
*Detected by LinkedIn Watcher v1.0*
"""
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created connection action file: {filename}")


class WhatsAppWatcherSkill(BaseSkill):
    """
    Skill: whatsapp_watcher_skill
    
    Monitors WhatsApp Web for new messages containing task triggers.
    
    Input:
        - keywords: list - Keywords that indicate tasks (urgent, invoice, payment, etc.)
        - contacts: list - Specific contacts to monitor (optional)
        - session_path: str - Path to browser session data
        - check_interval: int - Seconds between checks
    
    Output:
        - success: bool
        - data: dict containing:
            - new_messages: list of detected messages
            - keywords_matched: list
            - urgent_count: int
            - last_check: str (ISO format)
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="whatsapp_watcher_skill",
            description="Monitor WhatsApp Web for new messages containing task triggers",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.keywords = self.config.get(
            "keywords",
            ["urgent", "asap", "invoice", "payment", "help", "need", "call", "meeting"]
        )
        self.session_path = self.config.get("session_path")
        self.check_interval = self.config.get("check_interval", 30)  # 30 seconds
        self.processed_messages = set()
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords indicating tasks"
                },
                "contacts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific contacts to monitor"
                },
                "session_path": {
                    "type": "string",
                    "description": "Path to browser session data"
                },
                "check_interval": {
                    "type": "integer",
                    "description": "Seconds between checks"
                }
            },
            "required": []
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "new_messages": {"type": "array"},
                        "keywords_matched": {"type": "array"},
                        "urgent_count": {"type": "integer"},
                        "last_check": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the WhatsApp watcher skill"""
        try:
            keywords = kwargs.get("keywords", self.keywords)
            contacts = kwargs.get("contacts", [])
            session_path = kwargs.get("session_path", self.session_path)
            check_interval = kwargs.get("check_interval", self.check_interval)
            
            # Check for new messages
            new_messages = self._check_whatsapp_messages(keywords, contacts, session_path)
            
            # Find matched keywords
            matched_keywords = self._find_matched_keywords(new_messages, keywords)
            
            # Count urgent messages
            urgent_keywords = ["urgent", "asap", "emergency", "help"]
            urgent_count = sum(
                1 for msg in new_messages
                if any(ukw in msg.get("text", "").lower() for ukw in urgent_keywords)
            )
            
            result = {
                "new_messages": new_messages,
                "keywords_matched": matched_keywords,
                "urgent_count": urgent_count,
                "last_check": datetime.now().isoformat(),
                "total_messages": len(new_messages)
            }
            
            # Create action files for new messages
            if new_messages:
                self._create_action_files(new_messages)
            
            self._write_log({
                "action": "whatsapp_watch",
                "keywords": keywords,
                "messages_found": len(new_messages),
                "urgent_count": urgent_count,
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error in WhatsApp watcher: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _check_whatsapp_messages(
        self,
        keywords: List[str],
        contacts: List[str],
        session_path: str
    ) -> List[Dict]:
        """Check WhatsApp Web for new messages"""
        self.logger.info(f"Checking WhatsApp for keywords: {keywords}")
        
        # In production, this would use Playwright to automate WhatsApp Web
        # Example implementation:
        # from playwright.sync_api import sync_playwright
        # with sync_playwright() as p:
        #     browser = p.chromium.launch_persistent_context(session_path, headless=True)
        #     page = browser.pages[0]
        #     page.goto('https://web.whatsapp.com')
        #     ... scrape messages ...
        
        # Simulated results
        messages = []
        
        return messages
    
    def _find_matched_keywords(self, messages: List[Dict], keywords: List[str]) -> List[str]:
        """Find which keywords were matched"""
        matched = set()
        for msg in messages:
            text = msg.get("text", "").lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    matched.add(keyword)
        return list(matched)
    
    def _create_action_files(self, messages: List[Dict]) -> None:
        """Create action files in Needs_Action folder"""
        if not self.vault_path:
            return
        
        needs_action = self.vault_path / "Needs_Action"
        needs_action.mkdir(exist_ok=True)
        
        for msg in messages:
            # Sanitize contact name for filename
            contact = msg.get("contact", "unknown").replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"WHATSAPP_{contact}_{timestamp}.md"
            filepath = needs_action / filename
            
            content = f"""---
type: whatsapp_message
from: {msg.get('contact', 'Unknown')}
received: {msg.get('timestamp', datetime.now().isoformat())}
priority: {msg.get('priority', 'normal')}
status: pending
keywords: {', '.join(msg.get('matched_keywords', []))}
---

# WhatsApp Message

## From
{msg.get('contact', 'Unknown')}

## Message
{msg.get('text', 'No content')}

## Received
{msg.get('timestamp', datetime.now().isoformat())}

## Suggested Actions
- [ ] Review message
- [ ] Respond if needed
- [ ] Archive after processing
"""
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Created WhatsApp action file: {filepath}")
    
    def start_continuous_monitoring(self, callback=None) -> None:
        """Start continuous monitoring (daemon mode)"""
        import time
        
        self.logger.info(f"Starting continuous WhatsApp monitoring (interval: {self.check_interval}s)")
        
        try:
            while True:
                result = self.execute()
                if result["success"] and callback:
                    callback(result["data"])
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("WhatsApp monitoring stopped by user")


# Export all watcher skills
__all__ = [
    "GoogleWatcherSkill",
    "LinkedInWatcherSkill",
    "WhatsAppWatcherSkill"
]
