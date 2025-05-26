import logging
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from ..external_services import BrowserService, EmailService, CalendarService, CalendarEventParams

logger = logging.getLogger("mcp_connector.server")

class NavigateParams(BaseModel):
    url: str

class YoutubeSearchParams(BaseModel):
    search_query: str

class FormParams(BaseModel):
    form_data: Dict[str, str]
    selectors: Optional[Dict[str, str]] = None

class ClickParams(BaseModel):
    selector: str

class EmailParams(BaseModel):
    recipient: str
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    is_html: bool = False

class CalendarEventParams(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = None

class MCPConnector:
    """MCP Connector that bridges agents and external services"""
    
    def __init__(self, name: str = "Alris MCP Connector"):
        """Initialize the MCP connector with required services"""
        self.mcp = FastMCP(name)
        
        self.browser_service = BrowserService()
        self.email_service = EmailService()
        
        self._register_tools()
        
        logger.info("MCP Connector initialized")
    
    def _register_tools(self):
        """Register all tools with the MCP server"""
        
        @self.mcp.tool()
        async def navigate(params: Dict[str, Any]) -> Dict[str, Any]:
            """Navigate to a URL in the browser"""
            try:
                if "url" in params:
                    url = params["url"]
                elif "params" in params and isinstance(params["params"], dict) and "url" in params["params"]:
                    url = params["params"]["url"]
                else:
                    return {
                        "status": "error",
                        "message": "URL parameter is required"
                    }
                
                success = await self.browser_service.navigate(url)
                if success:
                    return {
                        "status": "success",
                        "message": f"Successfully navigated to {url}"
                    }
                return {
                    "status": "error",
                    "message": f"Failed to navigate to {url}"
                }
            except Exception as e:
                logger.error(f"Error in navigate tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error in navigate tool: {str(e)}"
                }
        
        @self.mcp.tool()
        async def search_youtube(params: Dict[str, Any]) -> Dict[str, Any]:
            """Search for a video on YouTube"""
            try:
                if "search_query" in params:
                    search_query = params["search_query"]
                elif "params" in params and isinstance(params["params"], dict) and "search_query" in params["params"]:
                    search_query = params["params"]["search_query"]
                else:
                    return {
                        "status": "error",
                        "message": "search_query parameter is required"
                    }
                
                query = search_query.replace(" ", "+")
                url = f"https://www.youtube.com/results?search_query={query}"
                success = await self.browser_service.navigate(url)
                if success:
                    await self.browser_service.click_element("a#video-title")
                    return {
                        "status": "success",
                        "message": f"Successfully searched for and played YouTube video: {search_query}"
                    }
                return {
                    "status": "error",
                    "message": f"Failed to search YouTube for {search_query}"
                }
            except Exception as e:
                logger.error(f"Error in search_youtube tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error in search_youtube tool: {str(e)}"
                }
        
        @self.mcp.tool()
        async def fill_form(params: Dict[str, Any]) -> Dict[str, Any]:
            """Fill a form with the provided data"""
            try:
                form_data = None
                selectors = None
                
                if "form_data" in params:
                    form_data = params["form_data"]
                    selectors = params.get("selectors")
                elif "params" in params and isinstance(params["params"], dict):
                    form_data = params["params"].get("form_data")
                    selectors = params["params"].get("selectors")
                
                if not form_data:
                    return {
                        "status": "error",
                        "message": "form_data parameter is required"
                    }
                
                success = await self.browser_service.fill_form(form_data, selectors)
                if success:
                    return {
                        "status": "success",
                        "message": "Successfully filled form"
                    }
                return {
                    "status": "error",
                    "message": "Failed to fill form"
                }
            except Exception as e:
                logger.error(f"Error in fill_form tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error in fill_form tool: {str(e)}"
                }
        
        @self.mcp.tool()
        async def click_element(params: Dict[str, Any]) -> Dict[str, Any]:
            """Click on an element in the browser"""
            try:
                if "selector" in params:
                    selector = params["selector"]
                elif "params" in params and isinstance(params["params"], dict) and "selector" in params["params"]:
                    selector = params["params"]["selector"]
                else:
                    return {
                        "status": "error",
                        "message": "selector parameter is required"
                    }
                
                success = await self.browser_service.click_element(selector)
                if success:
                    return {
                        "status": "success",
                        "message": f"Successfully clicked element: {selector}"
                    }
                return {
                    "status": "error",
                    "message": f"Failed to click element: {selector}"
                }
            except Exception as e:
                logger.error(f"Error in click_element tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error in click_element tool: {str(e)}"
                }
        
        @self.mcp.tool()
        async def send_email(params: Dict[str, Any]) -> Dict[str, Any]:
            """Send an email"""
            try:
                email_params = None
                
                if all(k in params for k in ["recipient", "subject", "body"]):
                    email_params = params
                elif "params" in params and isinstance(params["params"], dict):
                    p = params["params"]
                    if all(k in p for k in ["recipient", "subject", "body"]):
                        email_params = p
                
                if not email_params:
                    return {
                        "status": "error",
                        "message": "Required email parameters (recipient, subject, body) are missing"
                    }
                
                success = await self.email_service.send_email(
                    recipient=email_params["recipient"],
                    subject=email_params["subject"],
                    body=email_params["body"],
                    cc=email_params.get("cc"),
                    bcc=email_params.get("bcc"),
                    is_html=email_params.get("is_html", False)
                )
                
                if success:
                    return {
                        "status": "success",
                        "message": f"Successfully sent email to {email_params['recipient']}"
                    }
                return {
                    "status": "error",
                    "message": f"Failed to send email to {email_params['recipient']}"
                }
            except Exception as e:
                logger.error(f"Error in send_email tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error in send_email tool: {str(e)}"
                }
        
        @self.mcp.tool()
        async def schedule_calendar_event(params: Dict[str, Any]) -> Dict[str, Any]:
            """Schedule an event in Google Calendar using a pre-configured Google Apps Script."""
            try:
                if all(key in params for key in ["title", "start_time", "end_time"]):
                    event_params = CalendarEventParams(**params)
                elif "params" in params and isinstance(params["params"], dict):
                    event_params = CalendarEventParams(**params["params"])
                else:
                    return {
                        "status": "error",
                        "message": f"Invalid parameter structure: {params}"
                    }
                
                return await CalendarService.schedule_event(event_params)
            except Exception as e:
                logger.error(f"Error in schedule_calendar_event: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error processing calendar event: {str(e)}"
                }
        
        logger.info("MCP tools registered")
    
    @property
    def tools(self) -> Dict[str, Any]:
        """Get all registered tools"""
        if hasattr(self.mcp, "_tool_manager"):
            return self.mcp._tool_manager._tools
        return {}
    
    def run(self):
        """Run the MCP server"""
        logger.info("Starting MCP server")
        self.mcp.run()
    
    async def shutdown(self):
        """Shutdown the MCP server and services"""
        logger.info("Shutting down MCP server")
        
        try:
            await self.browser_service.close()
            logger.info("Browser service closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser service: {str(e)}")
            
        try:
            if hasattr(self.mcp, "close") and callable(self.mcp.close):
                await self.mcp.close()
                logger.info("MCP server closed successfully")
            elif hasattr(self.mcp, "shutdown") and callable(self.mcp.shutdown):
                await self.mcp.shutdown()
                logger.info("MCP server shut down successfully")
            else:
                logger.info("No direct shutdown method for MCP server, skipping")
        except Exception as e:
            logger.error(f"Error shutting down MCP server: {str(e)}")
            
        logger.info("MCP connector shutdown complete")