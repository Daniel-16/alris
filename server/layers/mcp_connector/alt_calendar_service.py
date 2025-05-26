import logging
import os
import json
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("alt_calendar_service")

class SimpleCalendarService:
    
    @staticmethod
    async def schedule_event(title: str, 
                           start_time: str, 
                           end_time: str, 
                           description: Optional[str] = None) -> Dict[str, Any]:
        
        try:
            logger.info(f"Scheduling calendar event: {title} at {start_time}")
            
            apps_script_url = os.getenv("GOOGLE_APPS_SCRIPT_CALENDAR_URL")
            if not apps_script_url:
                logger.error("GOOGLE_APPS_SCRIPT_CALENDAR_URL not set in environment")
                return {
                    "status": "error",
                    "message": "Calendar service misconfigured: missing API URL"
                }            
            if apps_script_url.endswith('%'):
                apps_script_url = apps_script_url[:-1]
                logger.info(f"Fixed Google Apps Script URL by removing trailing % character")
            
            logger.info(f"Using Google Apps Script URL: {apps_script_url}")
            
            payload = {
                "title": title,
                "startTime": start_time,
                "endTime": end_time
            }
            
            if description:
                payload["description"] = description
            
            logger.info(f"Sending calendar request to Apps Script: {payload}")
            response = requests.post(
                apps_script_url, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Calendar event created successfully")
                try:
                    result = response.json()
                    return {
                        "status": "success",
                        "message": f"Successfully scheduled '{title}' in your calendar",
                        "event_id": result.get("eventId", "unknown")
                    }
                except (ValueError, json.JSONDecodeError):
                    logger.warning("Could not parse response JSON, but event creation succeeded")
                    return {
                        "status": "success",
                        "message": f"Successfully scheduled '{title}' in your calendar"
                    }
            else:
                logger.error(f"Failed to create calendar event. Status: {response.status_code}, Response: {response.text[:100]}")
                return {
                    "status": "error",
                    "message": f"Failed to create calendar event: {response.text[:100]}"
                }
                
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error creating calendar event: {str(e)}"
            } 