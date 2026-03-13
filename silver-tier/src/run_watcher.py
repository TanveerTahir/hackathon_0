#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watcher Runner - Simple script to run watchers from command line.

This script provides a simple way to run individual watchers
without the full orchestrator.

Usage:
    python run_watcher.py /path/to/vault filesystem
    python run_watcher.py /path/to/vault gmail
    python run_watcher.py /path/to/vault filesystem --daemon
"""

import argparse
import signal
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run a specific watcher for the AI Employee system"
    )
    
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        'watcher',
        choices=['filesystem', 'gmail'],
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
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)
    
    # Import and run the requested watcher
    running = True
    
    def signal_handler(signum, frame):
        nonlocal running
        print("\nStopping watcher...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.watcher == 'filesystem':
            from watchers import FilesystemWatcher
            watcher = FilesystemWatcher(str(vault_path), check_interval=args.interval)
            
            print(f"Starting FilesystemWatcher...")
            print(f"Drop folder: {watcher.drop_folder}")
            print(f"Check interval: {args.interval}s")
            
            if args.daemon:
                watcher.run()
            else:
                # Single check
                items = watcher.check_for_updates()
                print(f"Found {len(items)} new file(s)")
                for item in items:
                    filepath = watcher.create_action_file(item)
                    print(f"  Created: {filepath.name}")
                    
        elif args.watcher == 'gmail':
            from watchers import GmailWatcher
            watcher = GmailWatcher(str(vault_path), check_interval=args.interval)
            
            print(f"Starting GmailWatcher...")
            print(f"Check interval: {args.interval}s")
            
            if args.daemon:
                watcher.run()
            else:
                # Single check
                items = watcher.check_for_updates()
                print(f"Found {len(items)} new email(s)")
                for item in items:
                    filepath = watcher.create_action_file(item)
                    print(f"  Created: {filepath.name}")
                    
    except ImportError as e:
        print(f"Error: {e}")
        if args.watcher == 'gmail':
            print("Note: Gmail watcher requires Google API libraries.")
            print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
