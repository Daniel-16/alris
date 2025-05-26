#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import signal
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("alris_mcp_run.log")
    ]
)
logger = logging.getLogger("alris_start")

processes = []

def cleanup():
    logger.info("Cleaning up processes...")
    for proc in processes:
        if proc.poll() is None:
            logger.info(f"Terminating process {proc.pid}")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {proc.pid} did not terminate gracefully, killing")
                proc.kill()
            except Exception as e:
                logger.error(f"Error terminating process {proc.pid}: {e}")
    
    logger.info("All processes terminated")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def main():
    logger.info("Starting Alris with MCP server")

    python_path = os.environ.get("PYTHONPATH", "")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in python_path:
        if python_path:
            os.environ["PYTHONPATH"] = f"{current_dir}:{python_path}"
        else:
            os.environ["PYTHONPATH"] = current_dir
    
    logger.info("Starting MCP server...")
    mcp_server_path = os.path.join(current_dir, "mcp_server.py")
    
    if not os.path.exists(mcp_server_path):
        logger.info("MCP server script not found, creating it...")
        with open(mcp_server_path, 'w') as f:
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
        logger.info(f"Created MCP server script at {mcp_server_path}")
    
    mcp_process = subprocess.Popen(
        [sys.executable, mcp_server_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(mcp_process)
    logger.info(f"MCP server started with PID {mcp_process.pid}")
    
    time.sleep(2)
    
    if mcp_process.poll() is not None:
        logger.error(f"MCP server failed to start. Exit code: {mcp_process.returncode}")
        stderr = mcp_process.stderr.read()
        logger.error(f"MCP server error output: {stderr}")
        cleanup(None, None)
        return
    
    logger.info("Starting main Alris application...")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    main_cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", host, 
        "--port", str(port)
    ]
    
    if os.getenv("ALRIS_RELOAD", "False").lower() == "true":
        main_cmd.append("--reload")
    
    main_process = subprocess.Popen(
        main_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(main_process)
    logger.info(f"Main application started with PID {main_process.pid}")
    
    while True:
        if mcp_process.poll() is not None:
            logger.error(f"MCP server terminated unexpectedly with exit code {mcp_process.returncode}")
            stderr = mcp_process.stderr.read()
            logger.error(f"MCP server error output: {stderr}")
            cleanup(None, None)
            break
        
        if main_process.poll() is not None:
            logger.error(f"Main application terminated unexpectedly with exit code {main_process.returncode}")
            stderr = main_process.stderr.read() 
            logger.error(f"Main application error output: {stderr}")
            cleanup(None, None)
            break
        
        time.sleep(1)

if __name__ == "__main__":
    main() 