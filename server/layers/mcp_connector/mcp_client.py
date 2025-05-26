import logging
import asyncio
import os
from typing import Dict, Any
from contextlib import AsyncExitStack, suppress
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("mcp_connector.client")

class AlrisMCPClient:
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.exit_stack = AsyncExitStack()
        self.session = None
        self.connected = False
        self.protocol_version = "v1"
        
    async def connect(self) -> bool:
        try:
            logger.info(f"Connecting to MCP server at {self.host}:{self.port}")
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            server_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))            
            mcp_server_script = os.path.join(server_dir, 'mcp_server.py')
            if not os.path.exists(mcp_server_script):
                with open(mcp_server_script, 'w') as f:
                    f.write('''
import asyncio
import logging
from layers.mcp_connector import MCPConnector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("alris_mcp_server.log")
    ]
)
logger = logging.getLogger("mcp_server")

if __name__ == "__main__":
    logger.info("Starting standalone MCP server")
    mcp_connector = MCPConnector()
    mcp_connector.run()
''')
                logger.info(f"Created MCP server script at {mcp_server_script}")
            
            logger.info(f"Using MCP server script at: {mcp_server_script}")
            
            env = os.environ.copy()
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{server_dir}:{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = server_dir
            
            env['MCP_PROTOCOL_VERSION'] = self.protocol_version
            
            server_params = StdioServerParameters(
                command="python",
                args=[mcp_server_script],
                env=env
            )
            
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            read_stream, write_stream = stdio_transport
            
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(
                    read_stream, 
                    write_stream
                )
            )
            
            try:
                await self.session.initialize(protocol_version=self.protocol_version)
            except Exception as e:
                logger.warning(f"Failed to initialize with protocol version {self.protocol_version}: {e}")
                try:
                    await self.session.initialize()
                    logger.info("Successfully initialized without specifying protocol version")
                except Exception as e2:
                    logger.error(f"Also failed to initialize without protocol version: {e2}")
                    raise e2
            
            self.connected = True
            logger.info("Connected to MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            self.connected = False
            return False
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.connected or not self.session:
            logger.error("Not connected to MCP server")
            return {
                "status": "error",
                "message": "Not connected to MCP server"
            }
        
        try:
            logger.info(f"Calling MCP tool: {tool_name} with params: {params}")
            result = await self.session.call_tool(tool_name, params)
            logger.info(f"MCP tool result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error calling MCP tool: {str(e)}"
            }
    
    async def disconnect(self):
        """Safely disconnect from the MCP server with proper resource cleanup"""
        if not self.connected:
            logger.debug("MCP client already disconnected")
            return
            
        logger.info("Disconnecting from MCP server")
        
        self.connected = False
        
        self.session = None
        
        try:
            async def close_with_timeout():
                with suppress(asyncio.CancelledError, RuntimeError, Exception):
                    await self.exit_stack.aclose()
            
            await asyncio.wait_for(close_with_timeout(), timeout=2.0)
            logger.info("Successfully closed MCP exit stack")
        except asyncio.TimeoutError:
            logger.warning("MCP disconnect timed out, forcing exit")
        except asyncio.CancelledError:
            logger.warning("MCP disconnect operation was cancelled")
        except RuntimeError as e:
            logger.warning(f"Runtime error during MCP disconnect (likely task context issue): {str(e)}")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {str(e)}")
            
        self.exit_stack = AsyncExitStack() 