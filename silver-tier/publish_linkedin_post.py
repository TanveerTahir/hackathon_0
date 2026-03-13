#!/usr/bin/env python3
# Publish approved LinkedIn post
import sys
sys.path.insert(0, '.qwen/skills/linkedin-poster/scripts')

from linkedin_poster import LinkedInPoster

# Initialize with require_approval=False for direct posting
poster = LinkedInPoster(
    vault_path="ai_employee_vault",
    require_approval=False  # Direct posting
)

# Post content
content = "Silver Tier Test - AI Employee is operational! #Hackathon #SilverTier"

print("Publishing to LinkedIn...")
print(f"Content: {content}")
print()

result = poster.create_post(
    content=content,
    auto_post=True
)

if result["success"] and result["status"] == "published":
    print("[OK] Post published successfully!")
    print(f"URL: {result.get('post_url', 'N/A')}")
else:
    print(f"[WARN] Status: {result['status']}")
    print(f"Message: {result.get('message', result.get('error', 'Unknown'))}")
