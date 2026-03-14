#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter (X) MCP Server

Provides MCP tools for Twitter/X integration:
- Post tweets
- Get timeline
- Get mentions
- Reply to tweets
- Retweet/Like
- Get insights/analytics
- Search tweets

Usage:
    python twitter_mcp_server.py
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
logger = logging.getLogger('twitter-mcp-server')

# Configuration
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')

TWITTER_API_BASE = 'https://api.twitter.com/2'
TWITTER_API_V1 = 'https://api.twitter.com/1.1'

# Create server
server = Server('twitter-mcp-server')


class TwitterClient:
    """Client for Twitter API v2"""

    def __init__(self, bearer_token: str, api_key: str = None, api_secret: str = None,
                 access_token: str = None, access_secret: str = None):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.timeout = httpx.Timeout(30.0)
        self.user_id = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        use_v1: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request to Twitter API"""
        base_url = TWITTER_API_V1 if use_v1 else TWITTER_API_BASE
        url = f'{base_url}/{endpoint}'

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        # Use OAuth 1.0a for write operations if credentials available
        if self.api_key and self.api_secret and self.access_token and self.access_secret:
            # For write operations, we'd need OAuth 1.0a signing
            # This is a simplified implementation
            pass

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method == 'GET':
                    response = await client.get(url, headers=headers, params=params)
                elif method == 'POST':
                    response = await client.post(url, headers=headers, json=data)
                elif method == 'DELETE':
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f'Unsupported HTTP method: {method}')

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f'HTTP error: {e.response.status_code} - {e.response.text}')
                raise Exception(f'Twitter API error: {e.response.status_code}')
            except httpx.RequestError as e:
                logger.error(f'Request error: {str(e)}')
                raise Exception(f'Network error: {str(e)}')

    async def _get_my_user_id(self) -> str:
        """Get authenticated user's ID"""
        if self.user_id:
            return self.user_id

        result = await self._request('GET', 'users/me')
        self.user_id = result.get('data', {}).get('id')
        return self.user_id

    async def post_tweet(
        self,
        text: str,
        reply_tweet_id: str = None,
        media_ids: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new tweet"""
        data = {'text': text}

        if reply_tweet_id:
            data['reply'] = {'in_reply_to_tweet_id': reply_tweet_id}

        # Note: Media upload requires separate endpoint and OAuth 1.0a
        # This is a simplified implementation

        result = await self._request('POST', 'tweets', data=data, use_v1=True)

        return {
            'success': True,
            'tweet_id': result.get('data', {}).get('id'),
            'text': text,
            'message': 'Tweet posted successfully'
        }

    async def get_timeline(
        self,
        username: str = None,
        limit: int = 10,
        exclude: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user timeline or home timeline"""
        if exclude is None:
            exclude = ['retweets', 'replies']

        params = {
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,context_annotations',
            'exclude': ','.join(exclude)
        }

        if username:
            # Get user's tweets
            result = await self._request('GET', f'users/by/username/{username}/tweets', params=params)
        else:
            # Get home timeline (requires OAuth 1.0a)
            # Simplified - would need proper OAuth implementation
            raise Exception('Home timeline requires OAuth 1.0a authentication')

        tweets = []
        for tweet in result.get('data', []):
            tweets.append({
                'id': tweet.get('id'),
                'text': tweet.get('text', ''),
                'created_at': tweet.get('created_at'),
                'author_id': tweet.get('author_id'),
                'metrics': tweet.get('public_metrics', {})
            })

        return tweets

    async def get_mentions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get mentions of the authenticated user"""
        user_id = await self._get_my_user_id()

        params = {
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,text',
            'expansions': 'author_id',
            'user.fields': 'name,username,profile_image_url'
        }

        result = await self._request('GET', f'users/{user_id}/mentions', params=params)

        tweets = []
        users = {u['id']: u for u in result.get('includes', {}).get('users', [])}

        for tweet in result.get('data', []):
            author = users.get(tweet.get('author_id'), {})
            tweets.append({
                'id': tweet.get('id'),
                'text': tweet.get('text', ''),
                'created_at': tweet.get('created_at'),
                'author': {
                    'id': author.get('id'),
                    'name': author.get('name'),
                    'username': author.get('username')
                },
                'metrics': tweet.get('public_metrics', {})
            })

        return tweets

    async def reply_to_tweet(
        self,
        tweet_id: str,
        text: str
    ) -> Dict[str, Any]:
        """Reply to a tweet"""
        data = {
            'text': text,
            'reply': {
                'in_reply_to_tweet_id': tweet_id
            }
        }

        result = await self._request('POST', 'tweets', data=data, use_v1=True)

        return {
            'success': True,
            'tweet_id': result.get('data', {}).get('id'),
            'message': 'Reply posted successfully'
        }

    async def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        user_id = await self._get_my_user_id()

        data = {'tweet_id': tweet_id}

        result = await self._request('POST', f'users/{user_id}/retweets', data=data, use_v1=True)

        return {
            'success': True,
            'retweeted': result.get('data', {}).get('retweeted', False),
            'message': 'Tweet retweeted successfully'
        }

    async def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet"""
        user_id = await self._get_my_user_id()

        data = {'tweet_id': tweet_id}

        result = await self._request('POST', f'users/{user_id}/likes', data=data, use_v1=True)

        return {
            'success': True,
            'liked': result.get('data', {}).get('liked', False),
            'message': 'Tweet liked successfully'
        }

    async def get_tweet_insights(self, tweet_id: str) -> Dict[str, Any]:
        """Get insights/analytics for a tweet"""
        params = {
            'ids': tweet_id,
            'tweet.fields': 'public_metrics,non_public_metrics,organic_metrics,promoted_metrics'
        }

        result = await self._request('GET', 'tweets', params=params)

        tweet_data = result.get('data', [{}])[0]

        return {
            'tweet_id': tweet_id,
            'public_metrics': tweet_data.get('public_metrics', {}),
            'organic_metrics': tweet_data.get('organic_metrics', {}),
            'non_public_metrics': tweet_data.get('non_public_metrics', {})
        }

    async def search_tweets(
        self,
        query: str,
        limit: int = 10,
        start_time: str = None,
        end_time: str = None
    ) -> List[Dict[str, Any]]:
        """Search tweets"""
        params = {
            'query': query,
            'max_results': min(limit, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,text',
            'expansions': 'author_id',
            'user.fields': 'name,username'
        }

        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time

        result = await self._request('GET', 'tweets/search/recent', params=params)

        tweets = []
        users = {u['id']: u for u in result.get('includes', {}).get('users', [])}

        for tweet in result.get('data', []):
            author = users.get(tweet.get('author_id'), {})
            tweets.append({
                'id': tweet.get('id'),
                'text': tweet.get('text', ''),
                'created_at': tweet.get('created_at'),
                'author': {
                    'id': author.get('id'),
                    'name': author.get('name'),
                    'username': author.get('username')
                },
                'metrics': tweet.get('public_metrics', {})
            })

        return tweets

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information by username"""
        result = await self._request('GET', f'users/by/username/{username}')

        user = result.get('data', {})
        return {
            'id': user.get('id'),
            'name': user.get('name'),
            'username': user.get('username'),
            'description': user.get('description'),
            'public_metrics': user.get('public_metrics', {}),
            'created_at': user.get('created_at')
        }


# Global client instance
twitter_client: Optional[TwitterClient] = None


def get_client() -> TwitterClient:
    """Get or create Twitter client instance"""
    global twitter_client
    if twitter_client is None:
        if not TWITTER_BEARER_TOKEN:
            raise Exception(
                'Twitter credentials not configured. '
                'Set TWITTER_BEARER_TOKEN environment variable.'
            )
        twitter_client = TwitterClient(
            bearer_token=TWITTER_BEARER_TOKEN,
            api_key=TWITTER_API_KEY,
            api_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_secret=TWITTER_ACCESS_SECRET
        )
    return twitter_client


@server.list_tools()
async def list_tools() -> List[Dict[str, Any]]:
    """List available Twitter tools"""
    return [
        {
            'name': 'twitter_post_tweet',
            'description': 'Create a new tweet on Twitter/X',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': 'Tweet text content (max 280 characters)'
                    },
                    'reply_to_tweet_id': {
                        'type': 'string',
                        'description': 'ID of tweet to reply to (optional)'
                    }
                },
                'required': ['text']
            }
        },
        {
            'name': 'twitter_get_timeline',
            'description': 'Get tweets from a user timeline',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'Twitter username (without @)'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of tweets to retrieve (default: 10)',
                        'default': 10
                    }
                }
            }
        },
        {
            'name': 'twitter_get_mentions',
            'description': 'Get mentions of the authenticated user',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of mentions to retrieve (default: 20)',
                        'default': 20
                    }
                }
            }
        },
        {
            'name': 'twitter_reply_tweet',
            'description': 'Reply to a tweet',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'tweet_id': {
                        'type': 'string',
                        'description': 'ID of tweet to reply to'
                    },
                    'text': {
                        'type': 'string',
                        'description': 'Reply text content'
                    }
                },
                'required': ['tweet_id', 'text']
            }
        },
        {
            'name': 'twitter_retweet',
            'description': 'Retweet a tweet',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'tweet_id': {
                        'type': 'string',
                        'description': 'ID of tweet to retweet'
                    }
                },
                'required': ['tweet_id']
            }
        },
        {
            'name': 'twitter_like_tweet',
            'description': 'Like a tweet',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'tweet_id': {
                        'type': 'string',
                        'description': 'ID of tweet to like'
                    }
                },
                'required': ['tweet_id']
            }
        },
        {
            'name': 'twitter_get_insights',
            'description': 'Get analytics/insights for a tweet',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'tweet_id': {
                        'type': 'string',
                        'description': 'ID of tweet to get insights for'
                    }
                },
                'required': ['tweet_id']
            }
        },
        {
            'name': 'twitter_search',
            'description': 'Search tweets by query',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of tweets to retrieve (default: 10)',
                        'default': 10
                    },
                    'start_time': {
                        'type': 'string',
                        'description': 'Start time (ISO 8601 format)'
                    },
                    'end_time': {
                        'type': 'string',
                        'description': 'End time (ISO 8601 format)'
                    }
                },
                'required': ['query']
            }
        },
        {
            'name': 'twitter_get_user',
            'description': 'Get user information by username',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'description': 'Twitter username (without @)'
                    }
                },
                'required': ['username']
            }
        }
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute a Twitter tool"""
    try:
        client = get_client()

        if name == 'twitter_post_tweet':
            result = await client.post_tweet(
                text=arguments.get('text', ''),
                reply_tweet_id=arguments.get('reply_to_tweet_id')
            )
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'twitter_get_timeline':
            tweets = await client.get_timeline(
                username=arguments.get('username'),
                limit=arguments.get('limit', 10)
            )
            return [{'type': 'text', 'text': json.dumps(tweets, indent=2, default=str)}]

        elif name == 'twitter_get_mentions':
            mentions = await client.get_mentions(
                limit=arguments.get('limit', 20)
            )
            return [{'type': 'text', 'text': json.dumps(mentions, indent=2, default=str)}]

        elif name == 'twitter_reply_tweet':
            result = await client.reply_to_tweet(
                tweet_id=arguments.get('tweet_id', ''),
                text=arguments.get('text', '')
            )
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'twitter_retweet':
            result = await client.retweet(
                tweet_id=arguments.get('tweet_id', '')
            )
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'twitter_like_tweet':
            result = await client.like_tweet(
                tweet_id=arguments.get('tweet_id', '')
            )
            return [{'type': 'text', 'text': json.dumps(result, indent=2)}]

        elif name == 'twitter_get_insights':
            insights = await client.get_tweet_insights(
                tweet_id=arguments.get('tweet_id', '')
            )
            return [{'type': 'text', 'text': json.dumps(insights, indent=2, default=str)}]

        elif name == 'twitter_search':
            tweets = await client.search_tweets(
                query=arguments.get('query', ''),
                limit=arguments.get('limit', 10),
                start_time=arguments.get('start_time'),
                end_time=arguments.get('end_time')
            )
            return [{'type': 'text', 'text': json.dumps(tweets, indent=2, default=str)}]

        elif name == 'twitter_get_user':
            user = await client.get_user_info(
                username=arguments.get('username', '')
            )
            return [{'type': 'text', 'text': json.dumps(user, indent=2, default=str)}]

        else:
            return [{'type': 'text', 'text': f'Unknown tool: {name}'}]

    except Exception as e:
        logger.error(f'Tool execution error: {str(e)}')
        return [{'type': 'text', 'text': f'Error: {str(e)}'}]


async def main():
    """Run the Twitter MCP server"""
    logger.info('Starting Twitter MCP Server...')

    # Verify configuration
    if not TWITTER_BEARER_TOKEN:
        logger.warning('TWITTER_BEARER_TOKEN not set')
    else:
        logger.info('Twitter API configured')

    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == '__main__':
    asyncio.run(main())
