import logging
from typing import Dict, Any
import asyncio
from .browser_agent import BrowserAgent
from .calendar_handler import handle_calendar_intent
from .youtube_handler import detect_youtube_url, is_youtube_search_command, extract_youtube_search_query, create_youtube_direct_url_response
from .intent_detector import IntentDetector
from .form_extraction_tool import extract_form_fields

logger = logging.getLogger("langchain_agent.orchestrator")

class AgentOrchestrator:
    def __init__(self):
        self.browser_agent = BrowserAgent()
        self._cleanup_tasks = set()
        self.mcp_client = None
        self.intent_detector = IntentDetector()
        
        logger.info("Agent Orchestrator initialized")
    
    def set_mcp_client(self, mcp_client):
        self.mcp_client = mcp_client
        self.browser_agent.set_mcp_client(mcp_client)
    
    async def _handle_calendar_intent(self, command: str) -> Dict[str, Any]:
        """Handle calendar-related commands by parsing time information and calling calendar tools."""
        return await handle_calendar_intent(command, self.mcp_client)
    
    async def process_command(self, command: str, thread_id: str = None, user_tokens: dict = None) -> Dict[str, Any]:
        try:
            logger.info(f"Processing command: {command}")
            
            video_url = detect_youtube_url(command)
            if video_url:
                return create_youtube_direct_url_response(command, video_url)
            
            if is_youtube_search_command(command):
                logger.info(f"Detected YouTube search in command: {command}")
                query = extract_youtube_search_query(command)
                
                result = await self.browser_agent.direct_youtube_search(query)
                
                response = {
                    "intent": "youtube_search",
                    "command": command,
                    "result": result
                }
                
                if "video_urls" in result:
                    response["video_urls"] = result["video_urls"]
                    logger.info(f"Added {len(result['video_urls'])} video URLs to response")
                
                return response
            
            intent = self.intent_detector.detect_intent(command)
            if intent == "fill_form":
                extraction = await extract_form_fields(command)
                url = extraction.get("url")
                form_data = extraction.get("form_data") or {}
                needs_clarification = extraction.get("needs_clarification")
                if not url:
                    logger.info("Form extraction missing URL. Prompting user for clarification.")
                    return {
                        "intent": "fill_form",
                        "command": command,
                        "result": {
                            "status": "clarification_needed",
                            "message": "The form URL is required but was not found in your command. Please provide the URL of the form you want to fill.",
                            "fields": extraction
                        }
                    }
                if needs_clarification:
                    logger.info(f"Form extraction needs clarification: {needs_clarification}")
                    return {
                        "intent": "fill_form",
                        "command": command,
                        "result": {
                            "status": "clarification_needed",
                            "message": needs_clarification,
                            "fields": extraction
                        }
                    }
                if self.mcp_client:
                    mcp_result = await self.mcp_client.call_tool("fill_form", {"params": {"url": url, "form_data": form_data}})
                    return {
                        "intent": "fill_form",
                        "command": command,
                        "result": mcp_result,
                        "fields": form_data
                    }
                else:
                    logger.error("MCP client not available for form filling.")
                    return {
                        "intent": "fill_form",
                        "command": command,
                        "result": {
                            "status": "error",
                            "message": "MCP client not available for form filling."
                        },
                        "fields": extraction
                    }
            elif intent == "browser":
                result = await self.browser_agent.execute(command, thread_id=thread_id)
            elif intent == "calendar":
                result = await self._handle_calendar_intent(command)
            else:
                logger.info(f"Using browser agent for general command: {command}")
                result = await self.browser_agent.execute(command, thread_id=thread_id)
            
            response = {
                "intent": intent,
                "command": command,
                "result": result
            }
            
            if isinstance(result, dict) and "video_urls" in result:
                response["video_urls"] = result["video_urls"]
                logger.info(f"Propagating {len(result['video_urls'])} video URLs to response")
            
            return response
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            logger.exception("Full command processing error:")
            return {
                "intent": "error",
                "command": command,
                "error": str(e)
            }
    
    async def cleanup(self):
        try:
            for task in self._cleanup_tasks:
                if not task.done():
                    task.cancel()
            
            if self._cleanup_tasks:
                await asyncio.gather(*self._cleanup_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        finally:
            self._cleanup_tasks.clear()