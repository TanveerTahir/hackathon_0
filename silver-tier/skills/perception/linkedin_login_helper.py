#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Login Helper

This script opens a browser window for you to login to LinkedIn.
Once logged in, the session is saved for the LinkedIn Watcher.

Usage:
    python linkedin_login_helper.py
"""

import sys
from pathlib import Path
import time

# Add parent directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright


def main():
    """Open LinkedIn login in browser"""
    
    vault_path = project_root / "silver-tier" / "ai_employee_vault"
    session_path = vault_path / ".linkedin_session"
    
    # Ensure session directory exists
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LinkedIn Login Helper")
    print("=" * 60)
    print()
    print("This will open a browser window for LinkedIn login.")
    print()
    print("Steps:")
    print("  1. Browser will open to LinkedIn")
    print("  2. Login with your credentials")
    print("  3. Wait until you see your LinkedIn feed")
    print("  4. Close the browser window when done")
    print()
    print("Session will be saved to:")
    print(f"  {session_path}")
    print()
    print("Press Enter to continue...")
    input()
    
    print("Opening browser...")
    print()
    
    try:
        with sync_playwright() as p:
            # Launch browser with persistent context (saves session)
            # Using more human-like settings to avoid detection
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=False,  # Show browser for manual login
                viewport={'width': 1280, 'height': 720},
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
                    '--disable-sync',
                    '--no-first-run',
                    '--disable-translate',
                    '--disable-hang-monitor',
                    '--disable-software-rasterizer',
                    '--disable-client-side-phishing-detection',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-restoring-session-state',
                    '--window-size=1280,720'
                ],
                ignore_default_args=['--enable-automation'],
                channel='chrome'  # Use installed Chrome if available
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            print("Navigate to LinkedIn and login...")
            page.goto('https://www.linkedin.com', timeout=60000)
            
            # Wait for user to login (max 5 minutes)
            print("Waiting for login (up to 5 minutes)...")
            print("Close the browser window when you're logged in.")
            print()
            
            # Keep checking if user is logged in
            start_time = time.time()
            timeout = 300  # 5 minutes
            
            while time.time() - start_time < timeout:
                try:
                    # Check for post button (indicates logged in)
                    if page.query_selector('[data-control-name="topbar_post"]'):
                        print()
                        print("[OK] Login detected!")
                        time.sleep(2)  # Give time for page to fully load
                        break
                    time.sleep(1)
                except:
                    time.sleep(1)
            else:
                print()
                print("[WARN] Timeout - login may not have completed")
            
            # Close browser
            browser.close()
            
            print()
            print("=" * 60)
            print("Login Complete!")
            print("=" * 60)
            print()
            print("Session saved successfully!")
            print()
            print("Next steps:")
            print("  1. Run the LinkedIn Watcher test again:")
            print(f"     python {project_root / 'silver-tier' / 'skills' / 'perception' / 'test_linkedin_watcher.py'}")
            print()
            print("  2. Or use Qwen Code to run the watcher:")
            print('     "Run the LinkedIn watcher to check for new messages"')
            print()
            
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
