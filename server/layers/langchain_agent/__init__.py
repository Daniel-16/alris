"""
LangChain Agent Layer

This layer contains the intelligent agents that interpret user commands,
plan task execution, and coordinate with the MCP layer to execute those tasks.
"""

from .agent_orchestrator import AgentOrchestrator
from .browser_agent import BrowserAgent
from .intent_detector import IntentDetector
from .calendar_handler import *
from .youtube_handler import *

__all__ = [
    'AgentOrchestrator',
    'BrowserAgent',
    'IntentDetector',
    'handle_calendar_intent',
    'detect_youtube_url',
    'is_youtube_search_command'
]
