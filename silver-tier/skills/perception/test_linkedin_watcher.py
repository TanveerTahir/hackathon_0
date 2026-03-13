#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for LinkedIn Watcher

This script tests the LinkedInWatcherSkill to ensure it's working properly.
"""

import sys
from pathlib import Path

# Add parent directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.perception.watcher_skills import LinkedInWatcherSkill


def test_linkedin_watcher():
    """Test the LinkedIn watcher"""
    
    # Vault path
    vault_path = Path(__file__).parent.parent / "ai_employee_vault"
    
    print("=" * 60)
    print("LinkedIn Watcher Test")
    print("=" * 60)
    print()
    
    # Check if vault exists
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        print("Creating vault folder...")
        vault_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[OK] Vault path: {vault_path}")
    print()
    
    # Initialize the watcher
    print("Initializing LinkedIn Watcher...")
    try:
        watcher = LinkedInWatcherSkill(
            vault_path=str(vault_path),
            config={
                "keywords": ["hiring", "opportunity", "AI", "automation", "consulting"],
                "check_interval": 600
            }
        )
        print("[OK] LinkedIn Watcher initialized successfully")
        print()
    except Exception as e:
        print(f"[X] Error initializing watcher: {e}")
        return False

    # Check session path
    print("Checking session path...")
    print(f"[OK] Session path: {watcher.session_path}")
    if watcher.session_path.exists():
        print("  Session folder exists (previous session may be saved)")
    else:
        print("  Session folder will be created on first run")
    print()
    
    # Check Playwright installation
    print("Checking Playwright installation...")
    try:
        from playwright.sync_api import sync_playwright
        print("[OK] Playwright is installed")
    except ImportError:
        print("[X] Playwright is NOT installed")
        print()
        print("To install Playwright:")
        print("  1. pip install playwright")
        print("  2. playwright install chromium")
        return False
    print()
    
    # Run the watcher
    print("=" * 60)
    print("Running LinkedIn Watcher Test")
    print("=" * 60)
    print()
    print("[INFO] Browser will open if session needs login.")
    print("       If login is required, you'll see a message.")
    print()
    print("Starting watcher...")
    print()
    
    try:
        # Execute the watcher
        result = watcher.execute(
            watch_types=["messages", "posts", "jobs"],
            keywords=["hiring", "opportunity", "AI", "automation"]
        )
        
        # Display results
        print()
        print("=" * 60)
        print("Test Results")
        print("=" * 60)
        print()
        
        if result.get("success"):
            print("[OK] Watcher executed successfully!")
            print()
            
            data = result.get("data", {})
            
            print(f"Messages found: {len(data.get('new_messages', []))}")
            print(f"Posts found: {len(data.get('relevant_posts', []))}")
            print(f"Jobs found: {len(data.get('job_opportunities', []))}")
            print(f"Connections found: {len(data.get('connection_requests', []))}")
            print()
            
            total = (len(data.get('new_messages', [])) + 
                    len(data.get('relevant_posts', [])) + 
                    len(data.get('job_opportunities', [])) + 
                    len(data.get('connection_requests', [])))
            
            if total > 0:
                print(f"[OK] Total: {total} new items detected")
                print(f"[OK] Action files created in: {watcher.needs_action}")
            else:
                print("[INFO] No new items detected (this is normal if nothing new)")
            
            print()
            print("[OK] Test completed successfully!")
            return True
            
        else:
            error = result.get("error", "Unknown error")
            print(f"[X] Watcher failed: {error}")
            
            if "login" in error.lower():
                print()
                print("[INFO] LinkedIn login required:")
                print("  1. Run the watcher again")
                print("  2. Wait for browser to open")
                print("  3. Login to LinkedIn manually")
                print("  4. Session will be saved")
            
            return False
            
    except Exception as e:
        print(f"[X] Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_linkedin_watcher()
    sys.exit(0 if success else 1)
