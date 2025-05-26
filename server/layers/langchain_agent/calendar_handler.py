import logging
import datetime
import json
import re
from typing import Dict, Any
from dateutil import parser
from ..mcp_connector.alt_calendar_service import SimpleCalendarService
from .event_extraction_tool import extract_event_details

logger = logging.getLogger("langchain_agent.calendar_handler")

async def extract_date_time_from_command(command: str) -> tuple:
    today = datetime.datetime.now()
    start_time = today
    end_time = today + datetime.timedelta(hours=1)
    
    time_pattern = r'(?:at|by|on|for)\s+([\w\s:]+(?:am|pm|AM|PM)?)'
    time_match = re.search(time_pattern, command)
    
    if time_match:
        time_str = time_match.group(1).strip()
        try:
            parsed_time = parser.parse(time_str, fuzzy=True)
            
            if parsed_time < today:
                if time_str.lower().endswith(('am', 'pm')) or ':' in time_str:
                    parsed_time = datetime.datetime.combine(today.date(), parsed_time.time())
                    
                if parsed_time < today:
                    parsed_time = parsed_time + datetime.timedelta(days=1)
            
            start_time = parsed_time
            end_time = start_time + datetime.timedelta(hours=1)
        except Exception as e:
            logger.warning(f"Failed to parse time string '{time_str}': {e}")
    
    return start_time, end_time

async def use_alternative_calendar_service(title, start_time, end_time, description=None):
    logger.info(f"Using alternative calendar service for event: {title}")
    
    result = await SimpleCalendarService.schedule_event(
        title=title,
        start_time=start_time,
        end_time=end_time,
        description=description
    )
    
    if result.get("status") == "success":
        parsed_start = parser.parse(start_time) if isinstance(start_time, str) else start_time
        parsed_end = parser.parse(end_time) if isinstance(end_time, str) else end_time
        return {
            "status": "success",
            "result": f"I've scheduled an event titled '{title}' starting at {parsed_start.strftime('%I:%M %p on %A, %B %d')} and ending at {parsed_end.strftime('%I:%M %p')}."
        }
    else:
        return {
            "status": "error",
            "result": f"I couldn't schedule your event. {result.get('message', 'Please check your Google Apps Script configuration.')}"
        }

async def handle_calendar_intent(command: str, mcp_client=None) -> Dict[str, Any]:
    logger.info(f"Handling calendar intent for command: {command}")
    try:
        event_details = await extract_event_details(command)
        if event_details.get("needs_clarification"):
            logger.warning(f"Clarification needed: {event_details['needs_clarification']}")
            return {
                "status": "clarification_needed",
                "result": event_details["needs_clarification"]
            }
        title = event_details.get("title")
        start_time = event_details.get("start_time")
        end_time = event_details.get("end_time")
        description = event_details.get("description")

        if not title or not start_time or not end_time:
            logger.error(f"Missing required event fields: {event_details}")
            return {
                "status": "error",
                "result": "Could not extract all required event details. Please clarify your request."
            }

        start_time_str = start_time if isinstance(start_time, str) else str(start_time)
        end_time_str = end_time if isinstance(end_time, str) else str(end_time)

        if not mcp_client:
            logger.error("MCP client not available")
            logger.info("Falling back to alternative calendar service")
            return await use_alternative_calendar_service(title, start_time_str, end_time_str, description)

        if not mcp_client.connected:
            logger.error("MCP client not connected")
            try:
                logger.info("Attempting to reconnect MCP client")
                connected = await mcp_client.connect()
                if connected:
                    logger.info("MCP client reconnected successfully")
                else:
                    logger.error("Failed to reconnect MCP client")
                    logger.info("Falling back to alternative calendar service")
                    return await use_alternative_calendar_service(title, start_time_str, end_time_str, description)
            except Exception as e:
                logger.error(f"Error reconnecting MCP client: {str(e)}")
                logger.info("Falling back to alternative calendar service")
                return await use_alternative_calendar_service(title, start_time_str, end_time_str, description)

        logger.info(f"Scheduling event with title: {title}, start: {start_time_str}, end: {end_time_str}")
        event_params = {
            "title": title,
            "start_time": start_time_str,
            "end_time": end_time_str
        }
        if description:
            event_params["description"] = description
        try:
            response = await mcp_client.call_tool("schedule_calendar_event", event_params)
            logger.info(f"Calendar service response: {response}")
            if hasattr(response, "content"):
                response_content = response.content
                if isinstance(response_content, str):
                    try:
                        response_content = json.loads(response_content)
                    except json.JSONDecodeError:
                        pass
                if isinstance(response_content, dict) and response_content.get("status") == "success":
                    status = "success"
                else:
                    status = "error"
            else:
                status = response.get("status")
            if status == "success":
                parsed_start = parser.parse(start_time_str) if isinstance(start_time_str, str) else start_time_str
                parsed_end = parser.parse(end_time_str) if isinstance(end_time_str, str) else end_time_str
                return {
                    "status": "success",
                    "result": f"I've scheduled an event titled '{title}' starting at {parsed_start.strftime('%I:%M %p on %A, %B %d')} and ending at {parsed_end.strftime('%I:%M %p')}."
                }
            else:
                logger.info("MCP tool call didn't return success, falling back to alternative calendar service")
                return await use_alternative_calendar_service(title, start_time_str, end_time_str, description)
        except Exception as e:
            logger.error(f"Error calling MCP calendar tool: {str(e)}")
            logger.info("Falling back to alternative calendar service")
            return await use_alternative_calendar_service(title, start_time_str, end_time_str, description)
    except Exception as e:
        logger.error(f"Error in calendar intent handler: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "result": f"I had trouble scheduling your event: {str(e)}"
        } 