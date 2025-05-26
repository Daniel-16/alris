import re
import logging
from typing import List

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
            ],
            "twitter": [
                r"(post|write|create|make|compose|craft|send|tweet|publish).*tweet",
                r"tweet (about|on)",
                r"(post|share|put).*(on|to) twitter",
                r"(create|make|compose) .* twitter (post|update)"
            ]
        }
        
    def detect_intent(self, command: str) -> str:
        command = command.lower()
        
        for intent_type, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    logger.info(f"Detected {intent_type} intent in command: {command}")
                    return intent_type
        
        logger.info(f"No specific intent detected in command: {command}")
        return "general"
        
    def add_intent_pattern(self, intent_type: str, pattern: str) -> None:
        if intent_type not in self._intent_patterns:
            self._intent_patterns[intent_type] = []
            
        self._intent_patterns[intent_type].append(pattern)
        logger.info(f"Added new pattern for intent {intent_type}: {pattern}")
        
    def get_patterns_for_intent(self, intent_type: str) -> List[str]:
        return self._intent_patterns.get(intent_type, []) 