"""
LangChain Agent Layer

This layer contains the intelligent agents that interpret user commands,
plan task execution, and coordinate with the MCP layer to execute those tasks.
"""

from .agent_orchestrator import AgentOrchestrator
from .browser_agent import BrowserAgent
from .intent_detector import IntentDetector
from .calendar_handler import handle_calendar_intent
from .youtube_handler import detect_youtube_url, is_youtube_search_command
from .twitter_handler import is_twitter_post_command, handle_twitter_intent

__all__ = [
    'AgentOrchestrator',
    'BrowserAgent',
    'IntentDetector',
    'handle_calendar_intent',
    'detect_youtube_url',
    'is_youtube_search_command',
    'is_twitter_post_command',
    'handle_twitter_intent'
]
