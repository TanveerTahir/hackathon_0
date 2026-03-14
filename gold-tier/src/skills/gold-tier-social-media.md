# Gold Tier Social Media Skill

**Purpose:** Manage social media posting and engagement across Facebook, Instagram, Twitter, and LinkedIn.

## Available Actions

### Post to Facebook

Create posts on Facebook Page:

```
Post to Facebook: "Exciting news about our new product!"
Share this update on Facebook with link
Schedule Facebook post for tomorrow at 10 AM
```

### Post to Instagram

Create posts on Instagram:

```
Post to Instagram with this image
Share to Instagram: "Beautiful day at the office"
```

### Post to Twitter

Create tweets:

```
Tweet: "Just launched our new feature! #innovation"
Post to Twitter about the product launch
```

### Post to LinkedIn

Share professional updates:

```
Post to LinkedIn: "Proud to announce our partnership with..."
Share business update on LinkedIn
```

### Get Social Media Insights

Retrieve analytics:

```
Show Facebook insights for this week
Get Instagram engagement metrics
Display Twitter analytics
```

### Get Messages

Retrieve messages from platforms:

```
Get Facebook messages
Show Instagram comments
List Twitter mentions
```

### Reply to Messages

Respond to engagement:

```
Reply to Facebook message from John
Respond to this Instagram comment
Reply to this Twitter mention
```

### Search Social Media

Search for content:

```
Search Twitter for our brand name
Find mentions of our product
```

## Social Media MCP Tools

### Facebook Tools

| Tool | Description |
|------|-------------|
| `facebook_post` | Create post |
| `facebook_get_posts` | Get posts |
| `facebook_get_insights` | Get analytics |
| `facebook_get_messages` | Get messages |
| `facebook_reply_message` | Reply to message |

### Instagram Tools

| Tool | Description |
|------|-------------|
| `instagram_post` | Create post |
| `instagram_get_posts` | Get posts |
| `instagram_get_insights` | Get analytics |
| `instagram_get_comments` | Get comments |

### Twitter Tools

| Tool | Description |
|------|-------------|
| `twitter_post_tweet` | Create tweet |
| `twitter_get_timeline` | Get timeline |
| `twitter_get_mentions` | Get mentions |
| `twitter_reply_tweet` | Reply to tweet |
| `twitter_retweet` | Retweet |
| `twitter_like_tweet` | Like tweet |
| `twitter_get_insights` | Get analytics |
| `twitter_search` | Search tweets |

## Configuration

Set these environment variables:

```bash
# Facebook/Meta
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_ig_account

# Twitter
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret
```

## Usage with Claude Code

1. **Reference the skill:**
   ```
   @skills/gold-tier-social-media
   ```

2. **Give commands:**
   ```
   Using the gold-tier-social-media skill, post to all platforms
   Get insights from Facebook and Twitter
   ```

3. **Review output:**
   - Post confirmation
   - Engagement metrics
   - Response drafts

## Content Guidelines

### Facebook
- Optimal length: 40-80 characters
- Include images for 2.3x more engagement
- Post 1-2 times per day

### Instagram
- Use high-quality images
- Include 5-10 relevant hashtags
- Post consistently

### Twitter
- Keep under 280 characters
- Use 1-2 hashtags
- Engage with replies

### LinkedIn
- Professional tone
- 1300-1500 characters optimal
- Include industry insights

## Approval Workflow

For sensitive posts:

1. **Draft created** in `/Social_Media/Drafts/`
2. **Approval request** in `/Pending_Approval/`
3. **Human review** and approval
4. **Scheduled/posted** to platforms

## Best Practices

1. **Review before posting** - Always check content
2. **Engage promptly** - Respond to comments/messages
3. **Monitor sentiment** - Watch for negative feedback
4. **Track metrics** - Review insights weekly
5. **Maintain consistency** - Regular posting schedule
6. **Use hashtags wisely** - Relevant and适度

## Error Handling

If posting fails:
1. Check API credentials
2. Verify content meets platform guidelines
3. Check rate limits
4. Review error logs

---

*Gold Tier Social Media Skill v1.0*
