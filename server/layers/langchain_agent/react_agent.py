import os
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langchain.agents import Tool
from config.prompt import SYSTEM_PROMPT

logger = logging.getLogger("langchain_agent.react")

class BaseReactAgent(ABC):
    def __init__(self, model_name: Optional[str] = None):
        model_engine = model_name or os.getenv('GEMINI_MODEL')

        self.llm = ChatGoogleGenerativeAI(
            model=model_engine,
            temperature=0.5
        )

        self.memory = MemorySaver()
        self.tools = self._get_tools()
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.memory
        )

        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def _get_tools(self) -> List[Tool]:
        pass

    @abstractmethod
    def _get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

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

            system_prompt_content = self._get_system_prompt()
            messages: List[BaseMessage] = [
                SystemMessage(content=system_prompt_content),
                HumanMessage(content=input_text)
            ]

            result = await self.agent_executor.ainvoke({"messages": messages}, config=config)

            logger.debug("Agent execution completed successfully")

            video_urls = None
            tool_outputs = []
            last_message_content_str = ""
            awaited_messages_list: List[BaseMessage] = []

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

            if isinstance(result, dict) and "messages" in result:
                raw_messages = result["messages"]
                for i, msg_item in enumerate(raw_messages):
                    current_content = msg_item.content
                    if asyncio.iscoroutine(current_content):
                        try:
                            logger.info(f"Awaiting coroutine content for message {i}: {getattr(msg_item, 'type', 'unknown')}")
                            current_content = await current_content
                            logger.info(f"Coroutine result type for message {i}: {type(current_content)}")
                        except Exception as e:
                            logger.error(f"Error awaiting message content for message {i}: {str(e)}")
                            current_content = f"Error resolving content: {str(e)}"                 
                    msg_item.content = current_content 
                    awaited_messages_list.append(msg_item)


                    if isinstance(current_content, dict) and "video_urls" in current_content:
                        logger.info(f"Found video_urls in awaited content of message {i}: {current_content.get('video_urls')}")
                        video_urls = current_content.get("video_urls")

                    if msg_item.type == 'tool' and isinstance(current_content, dict) and "video_urls" in current_content:
                         video_urls = current_content["video_urls"]
                         logger.info(f"Extracted video URLs from tool message {i} output: {video_urls}")


                for msg_item in awaited_messages_list:
                    if hasattr(msg_item, 'name') and getattr(msg_item, 'name') == 'search_youtube':
                        if isinstance(msg_item.content, dict) and "video_urls" in msg_item.content:
                            video_urls = msg_item.content["video_urls"]
                            logger.info(f"Extracted video URLs from 'search_youtube' named message: {video_urls}")

                if is_youtube_request and not video_urls and youtube_query:
                    youtube_tool_instance = getattr(self, 'youtube_tool', None)
                    if youtube_tool_instance:
                        logger.info(f"Performing direct YouTube search via self.youtube_tool for query: {youtube_query}")
                        try:
                            video_ids_str = youtube_tool_instance.run(f"{youtube_query},5")
                            import ast
                            parsed_ids = ast.literal_eval(video_ids_str) if isinstance(video_ids_str, str) else video_ids_str
                            temp_video_urls = []
                            if isinstance(parsed_ids, list):
                                for video_id in parsed_ids:
                                    vid_part = video_id
                                    if 'watch?v=' in video_id:
                                        vid_part = video_id.split('watch?v=')[1].split('&')[0]
                                    temp_video_urls.append(f"https://www.youtube.com/watch?v={vid_part}")
                                video_urls = temp_video_urls
                                logger.info(f"Direct YouTube search (self.youtube_tool) found {len(video_urls)} videos")
                        except Exception as e:
                            logger.error(f"Error in direct YouTube search (self.youtube_tool): {str(e)}")
                
                last_ai_message = next((m for m in reversed(awaited_messages_list) if isinstance(m, AIMessage) and m.content), None)
                
                if last_ai_message:
                    last_message_content_str = last_ai_message.content
                    if isinstance(last_message_content_str, dict):
                        last_message_content_str = last_message_content_str.get("message", str(last_message_content_str))
                elif awaited_messages_list:
                    last_message_content_str = awaited_messages_list[-1].content
                    if isinstance(last_message_content_str, dict):
                        last_message_content_str = last_message_content_str.get("message", str(last_message_content_str))


                for msg_item in awaited_messages_list:
                    if msg_item.type == 'tool':
                         tool_outputs.append({
                            "tool_name": getattr(msg_item, 'name', msg_item.tool_call_id),
                            "tool_output": msg_item.content
                        })

                if video_urls and (not isinstance(last_message_content_str, str) or not any(url in last_message_content_str for url in video_urls)):
                    video_links_str = "\n".join([f"- {url}" for url in video_urls])
                    if is_youtube_request:
                        last_message_content_str = f"Here are some videos I found:\n{video_links_str}"

                response_dict = {
                    "status": "success",
                    "result": last_message_content_str,
                    "messages": [msg.model_dump() for msg in awaited_messages_list],
                    "tool_outputs": tool_outputs
                }
                if video_urls:
                    response_dict["video_urls"] = video_urls
                return response_dict
            else:
                output_val = str(result)
                if isinstance(result, dict):
                    output_val = result.get("output", result.get("message", str(result)))

                return {
                    "status": "success",
                    "result": output_val,
                    "messages": [],
                    "tool_outputs": []
                }

        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "details": f"Failed to execute agent: {str(e)}"
            }