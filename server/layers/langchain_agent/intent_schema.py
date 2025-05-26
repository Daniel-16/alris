from pydantic import BaseModel, Field

class IntentResult(BaseModel):
    intent: str = Field(..., description="The detected user intent, e.g. browser, email, calendar, general")
    reasoning: str = Field(..., description="Reasoning for the detected intent") 