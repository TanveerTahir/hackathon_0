"""
Watchers package - Perception layer for AI Employee system.

Watchers monitor various data sources and create actionable markdown files
for the AI to process.
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FilesystemWatcher

__all__ = ['BaseWatcher', 'FilesystemWatcher']

# Optional imports
try:
    from .gmail_watcher import GmailWatcher
    __all__.append('GmailWatcher')
except ImportError:
    pass
