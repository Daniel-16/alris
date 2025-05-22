import logging
import re
from typing import Dict, Any
import json

logger = logging.getLogger("langchain_agent.twitter_handler")

def is_twitter_post_command(command: str) -> bool:
    """Check if the command is a Twitter posting request"""
    patterns = [
        r"(post|write|create|make|compose|craft|send|tweet|publish).*tweet",
        r"tweet (about|on)",
        r"(post|share|put).*(on|to) twitter",
        r"(create|make|compose) .* twitter (post|update)"
    ]
    
    for pattern in patterns:
        if re.search(pattern, command.lower()):
            logger.info(f"Detected Twitter post command: {command}")
            return True
    
    return False

async def handle_twitter_intent(command: str, mcp_client, user_tokens: dict = None) -> Dict[str, Any]:
    """Handle Twitter-related commands by generating and posting tweets"""
    if not mcp_client:
        return {
            "status": "error", 
            "message": "MCP client not available"
        }
    
    try:
        quote_match = re.search(r"['\"]([^'\"]+)['\"]", command)
        if quote_match:
            tweet_text = quote_match.group(1).strip()
            logger.info(f"Extracted tweet text from quotes: {tweet_text}")
        else:
            content_match = re.search(r"(?:should\s+be|should\s+say|text\s+is|content\s+is|text|content)['\s]+([^'\"]+)['\"]?", command.lower())
            if content_match:
                tweet_text = content_match.group(1).strip()
                logger.info(f"Extracted tweet text from 'should be/say' pattern: {tweet_text}")
            else:
                match = re.search(r'(?:post|tweet|write|create|send|publish)(?:\s+a|\s+an)?(?:\s+inspiring|\s+new|\s+interesting)?\s+tweet(?:\s+about|\s+on)?\s+(.+?)(?:$|\s+to\s+twitter|\s+on\s+twitter)', command.lower())
                
                tweet_text = None
                if match:
                    tweet_text = match.group(1).strip()
                
                if not tweet_text:
                    cleaned_text = re.sub(r'(?:post|tweet|write|create|send|publish)(?:\s+a|\s+an)?(?:\s+inspiring|\s+new|\s+interesting)?\s+tweet(?:\s+about|\s+on)?', '', command.lower())
                    cleaned_text = re.sub(r'(?:\s+to\s+twitter|\s+on\s+twitter)', '', cleaned_text)
                    tweet_text = cleaned_text.strip()
                
                tweet_text = re.sub(r'(?:text|content)\s+should\s+(?:be|say)', '', tweet_text).strip()
                
                tweet_text = tweet_text.strip('\'"').strip()
        
        logger.info(f"Final tweet content: {tweet_text}")
        
        tool_params = {"params": {"text": tweet_text}}
        if user_tokens:
            if "access_token" in user_tokens and "access_token_secret" in user_tokens:
                tool_params["params"]["access_token"] = user_tokens["access_token"]
                tool_params["params"]["access_token_secret"] = user_tokens["access_token_secret"]
        result = await mcp_client.call_tool("post_tweet", tool_params)
        
        if hasattr(result, "content") and result.content:
            content_text = result.content[0].text if result.content[0].text else ""
            
            try:
                response_data = json.loads(content_text)
                
                if response_data.get("status") == "error":
                    error_msg = response_data.get("message", "Unknown error")
                    resolution = response_data.get("resolution", "")
                    
                    if resolution:
                        logger.error(f"Twitter API error: {error_msg}")
                        logger.info(f"Resolution suggestion: {resolution}")
                        return {
                            "status": "error",
                            "message": f"Failed to post tweet: {error_msg}",
                            "resolution": resolution
                        }
                    else:
                        logger.error(f"Error from Twitter API: {error_msg}")
                        return {
                            "status": "error",
                            "message": f"Failed to post tweet: {error_msg}"
                        }
                else:
                    return {
                        "status": "success",
                        "message": f"Successfully posted tweet: '{tweet_text}'",
                        "tweet_text": tweet_text,
                        "tweet_id": response_data.get("tweet_id", ""),
                        "tweet_url": response_data.get("tweet_url", "")
                    }
            except json.JSONDecodeError:
                if "Error executing tool" in content_text or result.isError:
                    logger.error(f"Error from Twitter API: {content_text}")
                    return {
                        "status": "error",
                        "message": f"Failed to post tweet: {content_text}"
                    }
                else:
                    return {
                        "status": "success",
                        "message": f"Successfully posted tweet: '{tweet_text}'",
                        "tweet_text": tweet_text
                    }
        else:
            if isinstance(result, dict) and result.get("status") == "success":
                return {
                    "status": "success",
                    "message": f"Successfully posted tweet: '{tweet_text}'",
                    "tweet_url": result.get("tweet_url", ""),
                    "tweet_id": result.get("tweet_id", "")
                }
            else:
                return {
                    "status": "error",
                    "message": "Unknown error posting tweet"
                }
    except Exception as e:
        logger.error(f"Error handling Twitter intent: {str(e)}")
        return {
            "status": "error",
            "message": f"Error handling Twitter intent: {str(e)}"
        } 