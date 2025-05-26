import os
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain.agents import Tool

logger = logging.getLogger("langchain_agent.react")

class BaseReactAgent(ABC):
    def __init__(self, model_name: Optional[str] = None):
        model = model_name or os.getenv('GEMINI_MODEL')
        
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0.5,
            convert_system_message_to_human=True
        )
        
        self.memory = MemorySaver()
        self.tools = self._get_tools()
        
        system_message = self._get_system_prompt()
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
            state_modifier=system_message,
            checkpointer=self.memory
        )
        
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def _get_tools(self) -> List[Tool]:
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        pass
    
    async def execute(self, input_text: str, thread_id: str = None) -> Dict[str, Any]:
        try:
            logger.debug(f"Executing agent with input: {input_text}")
            
            config = {
                "configurable": {
                    "thread_id": thread_id or "default",
                    "checkpoint_ns": "alris",
                    "checkpoint_id": f"agent_{thread_id or 'default'}"
                }
            }
            
            messages = [HumanMessage(content=input_text)]
            result = await self.agent_executor.ainvoke({"messages": messages}, config=config)
            
            logger.debug("Agent execution completed successfully")
            
            video_urls = None
            tool_outputs = []
            last_message = None
            awaited_messages = []
            
            is_youtube_request = any(keyword in input_text.lower() for keyword in ["youtube", "watch", "video", "tutorial"])
            youtube_query = None
            
            if is_youtube_request:
                search_terms = ["video", "tutorial", "watch"]
                for term in search_terms:
                    if term in input_text.lower():
                        parts = input_text.lower().split(term, 1)
                        if len(parts) > 1:
                            youtube_query = parts[1].strip()
                            break
                
                if not youtube_query and "youtube" in input_text.lower():
                    youtube_query = input_text.lower().replace("youtube", "").strip()
                
                if not youtube_query:
                    youtube_query = input_text
            
            if isinstance(result, dict):
                if "messages" in result:
                    for msg in result["messages"]:
                        content = msg.content
                        if asyncio.iscoroutine(content):
                            try:
                                logger.info(f"Awaiting coroutine content for message: {getattr(msg, 'name', 'unknown')}")
                                content = await content
                                logger.info(f"Coroutine result type: {type(content)}")
                            except Exception as e:
                                logger.error(f"Error awaiting message content: {str(e)}")
                                content = str(e)
                        
                        if isinstance(content, dict) and "video_urls" in content:
                            logger.info(f"Found video_urls in tool output: {content.get('video_urls')}")
                            video_urls = content.get("video_urls")
                        
                        msg.content = content
                        awaited_messages.append(msg)
                    
                    for msg in awaited_messages:
                        if hasattr(msg, 'name') and getattr(msg, 'name') == 'search_youtube':
                            logger.info(f"Found search_youtube tool output: {msg.content}")
                            if isinstance(msg.content, dict) and "video_urls" in msg.content:
                                video_urls = msg.content["video_urls"]
                                logger.info(f"Extracted video URLs from search_youtube output: {video_urls}")
                    
                    if is_youtube_request and not video_urls and youtube_query and hasattr(self, 'youtube_tool'):
                        logger.info(f"Direct YouTube search for query: {youtube_query}")
                        try:
                            youtube_tool = getattr(self, 'youtube_tool', None)
                            if not youtube_tool and hasattr(self, '_tools'):
                                for tool in self._tools:
                                    if tool.name == 'search_youtube':
                                        youtube_tool = tool
                                        break
                            
                            if youtube_tool:
                                from langchain_community.tools import YouTubeSearchTool
                                if not isinstance(youtube_tool, YouTubeSearchTool):
                                    youtube_tool = YouTubeSearchTool()
                                
                                try:
                                    video_ids_str = youtube_tool.run(f"{youtube_query},5")
                                    import ast
                                    video_ids = ast.literal_eval(video_ids_str) if isinstance(video_ids_str, str) else video_ids_str
                                    video_urls = []
                                    for video_id in video_ids:
                                        if 'watch?v=' in video_id:
                                            vid = video_id.split('watch?v=')[1].split('&')[0]
                                        else:
                                            vid = video_id
                                        url = f"https://www.youtube.com/watch?v={vid}"
                                        video_urls.append(url)
                                    
                                    logger.info(f"Direct YouTube search found {len(video_urls)} videos")
                                except Exception as e:
                                    logger.error(f"Error in direct YouTube search: {str(e)}")
                        except Exception as e:
                            logger.error(f"Failed to perform direct YouTube search: {str(e)}")
                    
                    last_message = awaited_messages[-1] if awaited_messages else None
                    
                    for msg in awaited_messages:
                        if hasattr(msg, 'tool_call_id'):
                            tool_output = {
                                "tool": getattr(msg, 'name', None),
                                "output": msg.content
                            }
                            tool_outputs.append(tool_output)
                    
                    last_message_content = last_message.content if last_message else ""
                    if isinstance(last_message_content, dict):
                        last_message_content = last_message_content.get("message", str(last_message_content))
                    
                    if video_urls and not any(url in last_message_content for url in video_urls):
                        video_links = "\n".join([f"- {url}" for url in video_urls])
                        if is_youtube_request:
                            last_message_content = f"Here are some videos I found:\n{video_links}"
                    
                    response = {
                        "status": "success",
                        "result": last_message_content,
                        "messages": awaited_messages,
                        "tool_outputs": tool_outputs
                    }
                    
                    if video_urls:
                        response["video_urls"] = video_urls
                        logger.info(f"Added {len(video_urls)} video URLs to response")
                    
                    return response
                else:
                    response = {
                        "status": "success",
                        "result": result.get("message", str(result)),
                        "action": result.get("action", "unknown"),
                        "messages": []
                    }
                    return response
            response = {
                "status": "success",
                "result": str(result),
                "messages": []
            }
            return response
            
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}")
            logger.exception("Full agent execution error:")
            return {
                "status": "error", 
                "error_type": type(e).__name__,
                "message": str(e),
                "details": f"Failed to execute agent: {str(e)}"
            } 