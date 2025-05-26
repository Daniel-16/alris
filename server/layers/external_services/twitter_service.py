import logging
import os
from typing import Dict, Any
import tweepy

logger = logging.getLogger("external_services.twitter")

class TwitterService:
    def __init__(self):
        self._client = None
        self._has_write_permissions = False
        self._initialize()
    
    def _initialize(self):
        try:
            logger.info("Initializing Twitter API service")
            
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                if not bearer_token:
                    logger.error("Twitter API credentials not found in environment variables")
                    return
                self._client = tweepy.Client(bearer_token=bearer_token)
                logger.info("Twitter client initialized with bearer token only (read-only mode)")
                logger.warning("Bearer token only provides read access, not write access for posting tweets")
                return
            
            auth = tweepy.OAuth1UserHandler(
                api_key, 
                api_secret,
                access_token,
                access_token_secret
            )
            api_v1 = tweepy.API(auth)
            
            try:
                verify_credentials = api_v1.verify_credentials(skip_status=True)
                if hasattr(verify_credentials, 'verified') and verify_credentials.verified:
                    self._has_write_permissions = True
            except Exception as e:
                logger.warning(f"Failed to verify write permissions: {str(e)}")
            
            self._client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                bearer_token=bearer_token
            )
            
            logger.info(f"Twitter client initialized successfully. Write permissions: {self._has_write_permissions}")
        except Exception as e:
            logger.error(f"Error initializing Twitter service: {str(e)}")
            self._client = None
    
    async def post_tweet(self, text: str, access_token: str = None, access_token_secret: str = None) -> Dict[str, Any]:
        """Post a new tweet with the given text, using per-user tokens if provided"""
        try:
            logger.info(f"Posting tweet: {text}")
            if access_token and access_token_secret:
                api_key = os.getenv("TWITTER_API_KEY")
                api_secret = os.getenv("TWITTER_API_SECRET")
                client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                )
            else:
                if not self._client:
                    return {
                        "status": "error",
                        "message": "Twitter client not initialized. Check if API credentials are properly set in environment variables."
                    }
                client = self._client

            response = client.create_tweet(text=text)
            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            return {
                "status": "success",
                "message": "Tweet posted successfully",
                "tweet_id": str(tweet_id),
                "tweet_url": tweet_url
            }
        except tweepy.TweepyException as e:
            error_msg = str(e)
            logger.error(f"Error posting tweet: {error_msg}")
            return {
                "status": "error",
                "message": f"Failed to post tweet: {error_msg}"
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post tweet: {str(e)}"
            }
    
    async def reply_to_tweet(self, tweet_id: str, text: str) -> Dict[str, Any]:
        """Reply to an existing tweet"""
        if not self._client:
            return {
                "status": "error",
                "message": "Twitter client not initialized"
            }
        
        try:
            logger.info(f"Replying to tweet {tweet_id}: {text}")
            response = self._client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            reply_id = response.data["id"]
            reply_url = f"https://twitter.com/i/web/status/{reply_id}"
            
            return {
                "status": "success",
                "message": "Reply posted successfully",
                "tweet_id": str(reply_id),
                "tweet_url": reply_url
            }
        except tweepy.TweepyException as e:
            error_msg = str(e)
            logger.error(f"Error replying to tweet: {error_msg}")
            
            if "403 Forbidden" in error_msg and "oauth1 app permissions" in error_msg:
                return {
                    "status": "error",
                    "message": f"Failed to reply to tweet: {error_msg}",
                    "resolution": (
                        "Your Twitter app doesn't have write permissions. "
                        "Please go to the Twitter Developer Portal, select your app, "
                        "go to 'App permissions' and change from 'Read' to 'Read and Write'. "
                        "Then regenerate your access token and token secret."
                    )
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to reply to tweet: {error_msg}"
                }
        except Exception as e:
            logger.error(f"Error replying to tweet: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to reply to tweet: {str(e)}"
            }
    
    async def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Get a tweet by ID"""
        if not self._client:
            return {
                "status": "error",
                "message": "Twitter client not initialized"
            }
        
        try:
            logger.info(f"Getting tweet with ID: {tweet_id}")
            response = self._client.get_tweet(
                id=tweet_id,
                expansions=["author_id"],
                tweet_fields=["created_at", "text", "public_metrics"]
            )
            
            if not response.data:
                return {
                    "status": "error",
                    "message": f"Tweet with ID {tweet_id} not found"
                }
            
            tweet_data = response.data
            
            return {
                "status": "success",
                "tweet": {
                    "id": str(tweet_data.id),
                    "text": tweet_data.text,
                    "created_at": str(tweet_data.created_at),
                    "author_id": str(tweet_data.author_id),
                    "metrics": tweet_data.public_metrics,
                    "url": f"https://twitter.com/i/web/status/{tweet_data.id}"
                }
            }
        except Exception as e:
            logger.error(f"Error getting tweet: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get tweet: {str(e)}"
            } 