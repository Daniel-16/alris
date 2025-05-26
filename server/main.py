from dotenv import load_dotenv
load_dotenv()
import logging
import json
import threading
import asyncio
import signal
import sys
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from fastapi.responses import JSONResponse
from layers.langchain_agent import AgentOrchestrator
from layers.mcp_connector import MCPConnector, AlrisMCPClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("alris_server.log")
    ]
)
logger = logging.getLogger("alris_server")

mcp_client = None
mcp_thread = None
mcp_connector = None
shutdown_requested = False
shutdown_lock = threading.Lock()

def handle_sigterm(*args):
    global shutdown_requested
    with shutdown_lock:
        shutdown_requested = True
    logger.info("Received SIGTERM signal, initiating graceful shutdown")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_client, mcp_thread, mcp_connector
    
    logger.info("Starting Alris server with layered architecture")
    
    try:
        if mcp_connector is None:
            mcp_connector = MCPConnector()
            logger.info("MCP connector initialized with calendar tool registered")
        
        if mcp_thread is None or not mcp_thread.is_alive():
            mcp_thread = threading.Thread(target=mcp_connector.run, daemon=True)
            mcp_thread.start()
            logger.info("MCP connector server thread started")
            await asyncio.sleep(1)
        
        if mcp_client is None:
            mcp_client = AlrisMCPClient()
            
            max_retries = 3
            retry_count = 0
            connected = False
            
            while retry_count < max_retries and not connected:
                logger.info(f"Attempting to connect MCP client (attempt {retry_count + 1}/{max_retries})")
                connected = await mcp_client.connect()
                
                if connected:
                    logger.info("MCP client connected successfully")
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Failed to connect MCP client, retrying in 2 seconds...")
                        await asyncio.sleep(2)
                    else:
                        logger.error("Failed to connect MCP client after maximum retries")
        
        agent_orchestrator = AgentOrchestrator()
        agent_orchestrator.set_mcp_client(mcp_client)
        logger.info("Agent orchestrator initialized with MCP client")
        
        app.state.mcp_connector = mcp_connector
        app.state.mcp_thread = mcp_thread
        app.state.mcp_client = mcp_client
        app.state.agent_orchestrator = agent_orchestrator
        
        yield
    finally:
        logger.info("FastAPI application shutting down")
        
        if mcp_client and hasattr(mcp_client, 'disconnect'):
            try:
                await asyncio.wait_for(mcp_client.disconnect(), timeout=3.0)
                logger.info("MCP client disconnected successfully")
                mcp_client = None
            except asyncio.TimeoutError:
                logger.warning("MCP client disconnect timed out, forcing closure")
            except Exception as e:
                logger.error(f"Error disconnecting MCP client: {str(e)}")
        
        if hasattr(mcp_connector, 'shutdown') and mcp_connector:
            try:
                await mcp_connector.shutdown()
                logger.info("MCP connector shut down successfully")
                mcp_connector = None
            except Exception as e:
                logger.error(f"Error shutting down MCP connector: {str(e)}")

        if hasattr(app.state, 'agent_orchestrator'):
            await app.state.agent_orchestrator.cleanup()

app = FastAPI(
    title="Alris Server", 
    lifespan=lifespan,
    websocket_ping_interval=None,
    websocket_ping_timeout=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("Received WebSocket connection")
    await websocket.accept()
    
    thread_id = str(uuid.uuid4())
    logger.debug(f"Generated thread ID for connection: {thread_id}")
    
    try:
        while True:
            message = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {message}")
            
            try:
                data = json.loads(message)
                command = data.get("command")
                
                if not command:
                    raise ValueError("Command is required")
                
                response = await app.state.agent_orchestrator.process_command(command, thread_id=thread_id)
                logger.debug(f"Agent response: {response}")
                
                video_urls = None
                if isinstance(response, dict):
                    if "video_urls" in response:
                        video_urls = response["video_urls"]
                    elif isinstance(response.get("result"), dict) and "video_urls" in response["result"]:
                        video_urls = response["result"]["video_urls"]
                
                message_content = ""
                if isinstance(response, dict):
                    if "intent" in response and response["intent"] == "youtube_search":
                        if isinstance(response.get("result"), dict):
                            message_content = response["result"].get("message", "")
                    elif isinstance(response.get("result"), dict):
                        if "message" in response["result"]:
                            message_content = response["result"]["message"]
                        elif "result" in response["result"]:
                            message_content = response["result"]["result"]
                        else:
                            message_content = str(response["result"])
                    else:
                        message_content = str(response.get("result", response))
                else:
                    message_content = str(response)
                
                ws_response = {
                    "type": "response",
                    "data": message_content
                }
                
                ws_response["metadata"] = {}
                
                if video_urls:
                    ws_response["video_urls"] = video_urls
                    logger.info(f"Including {len(video_urls)} video URLs in WebSocket response")
                    ws_response["metadata"]["content_type"] = "youtube_videos"
                    ws_response["metadata"]["query"] = response.get("result", {}).get("query", "")
                    ws_response["metadata"]["count"] = len(video_urls)
                
                if isinstance(response, dict) and "intent" in response:
                    intent_type = response["intent"]
                    ws_response["metadata"]["intent"] = intent_type
                    
                    if "resolution" in response:
                        ws_response["metadata"]["resolution"] = response["resolution"]
                        logger.info(f"Including resolution instructions in WebSocket response")
                
                logger.debug(f"Sending WebSocket response: {ws_response}")
                
                await websocket.send_text(json.dumps(ws_response))
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON format received")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    
    mcp_status = "running" if app.state.mcp_thread and app.state.mcp_thread.is_alive() else "stopped"
    mcp_client_status = "connected" if app.state.mcp_client and app.state.mcp_client.connected else "disconnected"
    
    return {
        "status": "healthy",
        "components": {
            "mcp_connector": {
                "status": mcp_status,
                "tools": list(app.state.mcp_connector.tools.keys()) if hasattr(app.state.mcp_connector, "tools") else []
            },
            "mcp_client": {
                "status": mcp_client_status
            },
            "agent_orchestrator": {
                "status": "initialized",
                "agents": ["BrowserAgent"]
            },
            "websocket": {
                "status": "available",
                "endpoint": "/ws"
            }
        },
        "version": "0.2.0"
    }

@app.post("/command")
async def command_endpoint(request: Request):
    try:
        data = await request.json()
        command = data.get("command")
        if not command:
            return JSONResponse(
                status_code=400,
                content={"type": "error", "message": "Command is required"}
            )

        thread_id = str(uuid.uuid4())
        response = await app.state.agent_orchestrator.process_command(command, thread_id=thread_id)

        message_content = ""
        video_urls = None
        if isinstance(response, dict):
            if "video_urls" in response:
                video_urls = response["video_urls"]
            elif isinstance(response.get("result"), dict) and "video_urls" in response["result"]:
                video_urls = response["result"]["video_urls"]

        if isinstance(response, dict):
            if "intent" in response and response["intent"] == "youtube_search":
                if isinstance(response.get("result"), dict):
                    message_content = response["result"].get("message", "")
            elif isinstance(response.get("result"), dict):
                if "message" in response["result"]:
                    message_content = response["result"]["message"]
                elif "result" in response["result"]:
                    message_content = response["result"]["result"]
                else:
                    message_content = str(response["result"])
            else:
                message_content = str(response.get("result", response))
        else:
            message_content = str(response)

        api_response = {
            "type": "response",
            "data": message_content,
            "metadata": {}
        }

        if video_urls:
            api_response["video_urls"] = video_urls
            api_response["metadata"]["content_type"] = "youtube_videos"
            api_response["metadata"]["query"] = response.get("result", {}).get("query", "")
            api_response["metadata"]["count"] = len(video_urls)

        if isinstance(response, dict) and "intent" in response:
            api_response["metadata"]["intent"] = response["intent"]

        return JSONResponse(content=api_response)

    except Exception as e:
        logger.error(f"Error in /command endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"type": "error", "message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="debug"
    )