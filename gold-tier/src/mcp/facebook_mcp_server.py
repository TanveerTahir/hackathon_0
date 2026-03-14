#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook/Meta MCP Server

Provides MCP tools for Facebook and Instagram integration:
- Post to Facebook Page
- Post to Instagram
- Get messages
- Get insights
- Reply to messages
- Get comments

Usage:
    python facebook_mcp_server.py
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp.server import Server
import mcp.server.stdio

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('facebook-mcp-server')

# Configuration
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID', '')
GRAPH_API_VERSION = 'v21.0'
GRAPH_API_BASE = f'https://graph.facebook.com/{GRAPH_API_VERSION}'

# Create server
server = Server('facebook-mcp-server')


class FacebookClient:
    """Client for Facebook/Meta Graph API"""

    def __init__(self, access_token: str, page_id: str, instagram_account_id: str = None):
        self.access_token = access_token
        self.page_id = page_id
        self.instagram_account_id = instagram_account_id
        self.base_url = GRAPH_API_BASE
        self.timeout = httpx.Timeout(30.0)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        files: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Graph API"""
        url = f'{self.base_url}/{endpoint}'

        if params is None:
            params = {}
        params['access_token'] = self.access_token

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method == 'GET':
                    response = await client.get(url, params=params)
                elif method == 'POST':
                    if files:
                        # Multipart form data for file uploads
                        response = await client.post(url, params=params, files=files, data=data)
                    else:
                        response = await client.post(url, params=params, json=data)
                elif method == 'DELETE':
                    response = await client.delete(url, params=params)
                else:
                    raise ValueError(f'Unsupported HTTP method: {method}')

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f'HTTP error: {e.response.status_code} - {e.response.text}')
                raise Exception(f'Facebook API error: {e.response.status_code}')
            except httpx.RequestError as e:
                logger.error(f'Request error: {str(e)}')
                raise Exception(f'Network error: {str(e)}')

    async def post_to_facebook(
        self,
        message: str,
        link: str = None,
        photo_url: str = None,
        scheduled_time: str = None
    ) -> Dict[str, Any]:
        """Create a post on Facebook Page"""
        data = {'message': message}

        if link:
            data['link'] = link
        if photo_url:
            data['photo_url'] = photo_url
        if scheduled_time:
            data['scheduled_publish_time'] = scheduled_time
            data['published'] = False

        result = await self._request('POST', f'{self.page_id}/feed', data=data)

        return {
            'success': True,
            'post_id': result.get('id'),
            'post_url': f'https://www.facebook.com/{result.get("id")}',
            'message': 'Post created successfully'
        }

    async def get_facebook_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts from Facebook Page"""
        params = {
            'fields': 'id,message,created_time,updated_time,permalink_url,likes.summary(true),comments.summary(true),shares',
            'limit': limit
        }

        result = await self._request('GET', f'{self.page_id}/posts', params=params)

        posts = []
        for post in result.get('data', []):
            posts.append({
                'id': post.get('id'),
                'message': post.get('message', ''),
                'created_time': post.get('created_time'),
                'permalink_url': post.get('permalink_url'),
                'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                'shares': post.get('shares', {}).get('count', 0)
            })

        return posts

    async def get_facebook_insights(self, metric_names: List[str] = None) -> Dict[str, Any]:
        """Get Facebook Page insights"""
        if metric_names is None:
            metric_names = [
                'page_impressions_unique',
                'page_engaged_users',
                'page_post_engagements',
                'page_likes',
                'page_follows',
                'page_posts_impressions_unique'
            ]

        params = {
            'metric': ','.join(metric_names),
            'period': 'day'
        }

        result = await self._request('GET', f'{self.page_id}/insights', params=params)

        insights = {}
        for metric in result.get('data', []):
            insights[metric['name']] = {
                'values': metric.get('values', []),
                'period': metric.get('period', 'day')
            }

        return insights

    async def get_facebook_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get messages from Facebook Page inbox"""
        params = {
            'fields': 'messages{from,message,created_time,id},updated_time',
            'limit': limit
        }

        result = await self._request('GET', f'{self.page_id}/conversations', params=params)

        messages = []
        for conversation in result.get('data', []):
            for msg in conversation.get('messages', {}).get('data', []):
                messages.append({
                    'id': msg.get('id'),
                    'from': msg.get('from', {}).get('name', 'Unknown'),
                    'message': msg.get('message', ''),
                    'created_time': msg.get('created_time'),
                    'conversation_id': conversation.get('id')
                })

        return messages

    async def reply_to_facebook_message(
        self,
        recipient_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Reply to a Facebook message"""
        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message}
        }

        result = await self._request('POST', 'me/messages', data=data)

        return {
            'success': True,
            'message_id': result.get('message_id'),
            'message': 'Reply sent successfully'
        }

    async def post_to_instagram(
        self,
        caption: str,
        image_url: str = None,
        video_url: str = None
    ) -> Dict[str, Any]:
        """Create a post on Instagram"""
        if not self.instagram_account_id:
            return {
                'success': False,
                'error': 'Instagram account ID not configured'
            }

        # Step 1: Create media container
        container_data = {
            'caption': caption,
            'image_source': image_url
        }

        if video_url:
            container_data = {
                'caption': caption,
                'video_url': video_url,
                'media_type': 'REELS'
            }

        container_result = await self._request(
            'POST',
            f'{self.instagram_account_id}/media',
            data=container_data
        )

        creation_id = container_result.get('id')

        # Step 2: Publish the container
        publish_data = {'creation_id': creation_id}
        publish_result = await self._request(
            'POST',
            f'{self.instagram_account_id}/media_publish',
            data=publish_data
        )

        return {
            'success': True,
            'post_id': publish_result.get('id'),
            'message': 'Instagram post published successfully'
        }

    async def get_instagram_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts from Instagram"""
        if not self.instagram_account_id:
            return []

        params = {
            'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
            'limit': limit
        }

        result = await self._request(
            'GET',
            f'{self.instagram_account_id}/media',
            params=params
        )

        posts = []
        for post in result.get('data', []):
            posts.append({
                'id': post.get('id'),
                'caption': post.get('caption', ''),
                'media_type': post.get('media_type'),
                'media_url': post.get('media_url'),
                'permalink': post.get('permalink'),
                'timestamp': post.get('timestamp'),
                'like_count': post.get('like_count', 0),
                'comments_count': post.get('comments_count', 0)
            })

        return posts

    async def get_instagram_insights(self, metric_names: List[str] = None) -> Dict[str, Any]:
        """Get Instagram account insights"""
        if not self.instagram_account_id:
            return {}

        if metric_names is None:
            metric_names = [
                'follower_count',
                'impressions',
                'reach',
                'profile_views',
                'website_clicks',
                'email_contacts'
            ]

        params = {
            'metric': ','.join(metric_names)
        }

        result = await self._request(
            'GET',
            f'{self.instagram_account_id}/insights',
            params=params
        )

        insights = {}
        for metric in result.get('data', []):
            insights[metric['name']] = {
                'value': metric.get('values', [{}])[0].get('value', 0),
                'period': metric.get('period', 'lifetime')
            }

        return insights

    async def get_instagram_comments(self, media_id: str) -> List[Dict[str, Any]]:
        """Get comments on an Instagram post"""
        if not self.instagram_account_id:
            return []

        params = {
            'fields': 'from,text,created_time,like_count',
        }

        result = await self._request(
            'GET',
            f'{media_id}/comments',
            params=params
        )

        comments = []
        for comment in result.get('data', []):
            comments.append({
                'id': comment.get('id'),
                'from': comment.get('from', {}).get('username', 'Unknown'),
                'text': comment.get('text', ''),
                'created_time': comment.get('created_time'),
                'like_count': comment.get('like_count', 0)
            })

        return comments


# Global client instance
client: Optional[FacebookClient] = None


def get_client() -> FacebookClient:
    """Get or create Facebook client instance"""
    global client
    if client is None:
        if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            raise Exception(
                'Facebook credentials not configured. '
                'Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID environment variables.'
            )
        client = FacebookClient(
            access_token=FACEBOOK_ACCESS_TOKEN,
            page_id=FACEBOOK_PAGE_ID,
            instagram_account_id=INSTAGRAM_ACCOUNT_ID
        )
    return client


@server.list_tools()
async def list_tools() -> List[Dict[str, Any]]:
    """List available Facebook/Instagram tools"""
    return [
        {
            'name': 'facebook_post',
            'description': 'Create a post on Facebook Page. Can include text, links, photos, and scheduling.',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'The post message/content'
                    },
                    'link': {
                        'type': 'string',
                        'description': 'Optional link to share'
                    },
                    'photo_url': {
                        'type': 'string',
                        'description': 'Optional photo URL to share'
                    },
                    'scheduled_time': {
                        'type': 'string',
                        'description': 'Optional ISO 8601 datetime for scheduled posting'
                    }
                },
                'required': ['message']
            }
        },
        {
            'name': 'facebook_get_posts',
            'description': 'Get recent posts from Facebook Page with engagement metrics',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of posts to retrieve (default: 10)',
                        'default': 10
                    }
                }
            }
        },
        {
            'name': 'facebook_get_insights',
            'description': 'Get Facebook Page insights and analytics',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'metrics': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'List of metric names to retrieve'
                    }
                }
            }
        },
        {
            'name': 'facebook_get_messages',
            'description': 'Get recent messages from Facebook Page inbox',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of messages to retrieve (default: 20)',
                        'default': 20
                    }
                }
            }
        },
        {
            'name': 'facebook_reply_message',
            'description': 'Reply to a Facebook message',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'recipient_id': {
                        'type': 'string',
                        'description': 'ID of the message recipient'
                    },
                    'message': {
                        'type': 'string',
                        'description': 'Reply message content'
                    }
                },
                'required': ['recipient_id', 'message']
            }
        },
        {
            'name': 'instagram_post',
            'description': 'Create a post on Instagram (supports images and reels)',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'caption': {
                        'type': 'string',
                        'description': 'The post caption'
                    },
                    'image_url': {
                        'type': 'string',
                        'description': 'URL of the image to post'
                    },
                    'video_url': {
                        'type': 'string',
                        'description': 'URL of the video for reels'
                    }
                },
                'required': ['caption']
            }
        },
        {
            'name': 'instagram_get_posts',
            'description': 'Get recent posts from Instagram',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of posts to retrieve (default: 10)',
                        'default': 10
                    }
                }
            }
        },
        {
            'name': 'instagram_get_insights',
            'description': 'Get Instagram account insights and analytics',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'metrics': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'List of metric names to retrieve'
                    }
                }
            }
        },
        {
            'name': 'instagram_get_comments',
            'description': 'Get comments on an Instagram post',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'media_id': {
                        'type': 'string',
                        'description': 'ID of the Instagram media'
                    }
                },
                'required': ['media_id']
            }
        }
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute a Facebook/Instagram tool"""
    try:
        fb_client = get_client()

        if name == 'facebook_post':
            result = await fb_client.post_to_facebook(
                message=arguments.get('message', ''),
                link=arguments.get('link'),
                photo_url=arguments.get('photo_url'),
                scheduled_time=arguments.get('scheduled_time')
            )
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'facebook_get_posts':
            limit = arguments.get('limit', 10)
            posts = await fb_client.get_facebook_posts(limit=limit)
            return [{'type': 'text', 'text': json.dumps(posts, indent=2, default=str)}]

        elif name == 'facebook_get_insights':
            metrics = arguments.get('metrics')
            insights = await fb_client.get_facebook_insights(metric_names=metrics)
            return [{'type': 'text', 'text': json.dumps(insights, indent=2, default=str)}]

        elif name == 'facebook_get_messages':
            limit = arguments.get('limit', 20)
            messages = await fb_client.get_facebook_messages(limit=limit)
            return [{'type': 'text', 'text': json.dumps(messages, indent=2, default=str)}]

        elif name == 'facebook_reply_message':
            recipient_id = arguments.get('recipient_id', '')
            message = arguments.get('message', '')
            result = await fb_client.reply_to_facebook_message(recipient_id, message)
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'instagram_post':
            caption = arguments.get('caption', '')
            image_url = arguments.get('image_url')
            video_url = arguments.get('video_url')
            result = await fb_client.post_to_instagram(caption, image_url, video_url)
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'instagram_get_posts':
            limit = arguments.get('limit', 10)
            posts = await fb_client.get_instagram_posts(limit=limit)
            return [{'type': 'text', 'text': json.dumps(posts, indent=2, default=str)}]

        elif name == 'instagram_get_insights':
            metrics = arguments.get('metrics')
            insights = await fb_client.get_instagram_insights(metric_names=metrics)
            return [{'type': 'text', 'text': json.dumps(insights, indent=2, default=str)}]

        elif name == 'instagram_get_comments':
            media_id = arguments.get('media_id', '')
            comments = await fb_client.get_instagram_comments(media_id)
            return [{'type': 'text', 'text': json.dumps(comments, indent=2, default=str)}]

        else:
            return [{'type': 'text', 'text': f'Unknown tool: {name}'}]

    except Exception as e:
        logger.error(f'Tool execution error: {str(e)}')
        return [{'type': 'text', 'text': f'Error: {str(e)}'}]


async def main():
    """Run the Facebook MCP server"""
    logger.info('Starting Facebook MCP Server...')

    # Verify configuration
    if not FACEBOOK_ACCESS_TOKEN:
        logger.warning('FACEBOOK_ACCESS_TOKEN not set - server will run in limited mode')
    else:
        logger.info(f'Facebook Page ID: {FACEBOOK_PAGE_ID}')
        logger.info(f'Instagram Account ID: {INSTAGRAM_ACCOUNT_ID or "Not configured"}')

    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == '__main__':
    asyncio.run(main())
