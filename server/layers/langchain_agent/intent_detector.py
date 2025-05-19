import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("langchain_agent.intent_detector")

class IntentDetector:
    def __init__(self):
        self._intent_patterns = {
            "browser": [
                r"browse|navigate|go to|open.*website|visit|url|web page",
                r"search.*youtube|play.*video|watch.*video", 
                r"fill.*form|input.*field|enter.*data",
                r"click.*button|click.*link|press.*button",
                r"screenshot|capture.*screen"
            ],
            "email": [
                r"send.*email|compose.*email|mail to|email to"
            ],
            "calendar": [
                r"schedule|meeting|appointment|calendar|event|remind"
            ]
        }
        
    def detect_intent(self, command: str) -> str:
        """Detect the intent of a command.
        
        Args:
            command: The command to analyze
            
        Returns:
            The detected intent (browser, email, calendar, or general)
        """
        command = command.lower()
        
        for intent_type, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    logger.info(f"Detected {intent_type} intent in command: {command}")
                    return intent_type
        
        logger.info(f"No specific intent detected in command: {command}")
        return "general"
        
    def add_intent_pattern(self, intent_type: str, pattern: str) -> None:
        """Add a new pattern for an intent type.
        
        Args:
            intent_type: The intent type (e.g., "browser", "email")
            pattern: The regex pattern to match for this intent
        """
        if intent_type not in self._intent_patterns:
            self._intent_patterns[intent_type] = []
            
        self._intent_patterns[intent_type].append(pattern)
        logger.info(f"Added new pattern for intent {intent_type}: {pattern}")
        
    def get_patterns_for_intent(self, intent_type: str) -> List[str]:
        """Get all patterns for a specific intent type.
        
        Args:
            intent_type: The intent type to get patterns for
            
        Returns:
            List of patterns for the intent type
        """
        return self._intent_patterns.get(intent_type, []) 