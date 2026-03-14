#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watchers package - Perception layer for AI Employee System.

Watchers monitor various data sources and create actionable files.
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FilesystemWatcher
from .facebook_watcher import FacebookWatcher
from .twitter_watcher import TwitterWatcher
from .odoo_watcher import OdooWatcher

# Gmail watcher may not exist in gold-tier, import from bronze/silver if needed
try:
    from .gmail_watcher import GmailWatcher
except ImportError:
    GmailWatcher = None

__all__ = [
    'BaseWatcher',
    'FilesystemWatcher',
    'FacebookWatcher',
    'TwitterWatcher',
    'OdooWatcher',
    'GmailWatcher',
]
