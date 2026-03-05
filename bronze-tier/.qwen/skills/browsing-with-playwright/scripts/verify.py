#!/usr/bin/env python3
"""Verify Playwright MCP server is running and accessible."""
import subprocess
import sys
import os

def main():
    # Check if server process is running using Windows-compatible commands
    # First try with pgrep (for Unix-like environments), then fall back to PowerShell
    
    # Try pgrep first (for WSL or Git Bash)
    try:
        result = subprocess.run(
            ["pgrep", "-f", "@playwright/mcp"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ Playwright MCP server running")
            sys.exit(0)
    except FileNotFoundError:
        pass
    
    # Try PowerShell for Windows
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*@playwright/mcp*' }"],
            capture_output=True, text=True
        )
        if result.returncode == 0 and "node" in result.stdout.lower():
            print("✓ Playwright MCP server running")
            sys.exit(0)
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Try netstat for checking port 8808
    try:
        result = subprocess.run(
            ["powershell", "-Command", "netstat -ano | Select-String ':8808.*LISTENING'"],
            capture_output=True, text=True
        )
        if result.returncode == 0 and "8808" in result.stdout:
            print("✓ Playwright MCP server running on port 8808")
            sys.exit(0)
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    
    print("✗ Server not running. Run: bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh")
    sys.exit(1)

if __name__ == "__main__":
    main()
