#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Watcher - Launch individual watchers.

Usage:
    python run_watcher.py /path/to/vault filesystem [--daemon] [--interval 30]
    python run_watcher.py /path/to/vault facebook [--daemon] [--interval 120]
    python run_watcher.py /path/to/vault twitter [--daemon] [--interval 120]
    python run_watcher.py /path/to/vault odoo [--daemon] [--interval 300]
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point for running watchers."""
    parser = argparse.ArgumentParser(
        description="Run individual watchers for AI Employee System"
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        'watcher',
        choices=['filesystem', 'gmail', 'facebook', 'twitter', 'odoo'],
        help='Watcher to run'
    )
    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='Run continuously in daemon mode'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=None,
        help='Check interval in seconds (default varies by watcher)'
    )

    args = parser.parse_args()

    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)

    # Import and run watcher
    if args.watcher == 'filesystem':
        from watchers import FilesystemWatcher
        watcher = FilesystemWatcher(str(vault_path))
    elif args.watcher == 'gmail':
        from watchers import GmailWatcher
        watcher = GmailWatcher(str(vault_path))
    elif args.watcher == 'facebook':
        from watchers import FacebookWatcher
        watcher = FacebookWatcher(str(vault_path))
    elif args.watcher == 'twitter':
        from watchers import TwitterWatcher
        watcher = TwitterWatcher(str(vault_path))
    elif args.watcher == 'odoo':
        from watchers import OdooWatcher
        watcher = OdooWatcher(str(vault_path))
    else:
        print(f"Unknown watcher: {args.watcher}")
        sys.exit(1)

    # Override interval if specified
    if args.interval:
        watcher.check_interval = args.interval

    # Run watcher
    try:
        if args.daemon:
            print(f"Starting {watcher.__class__.__name__} in daemon mode...")
            watcher.run()
        else:
            print(f"Running {watcher.__class__.__name__} (single check)...")
            items = watcher.check_for_updates()
            print(f"Found {len(items)} new items")
            for item in items:
                filepath = watcher.create_action_file(item)
                print(f"  Created: {filepath.name}")
    except KeyboardInterrupt:
        print("\nWatcher stopped by user")
        watcher.stop()


if __name__ == "__main__":
    main()
