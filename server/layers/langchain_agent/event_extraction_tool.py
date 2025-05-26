import os
import json
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    temperature=0.5,
    convert_system_message_to_human=True
)

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

prompt = PromptTemplate(
    input_variables=["user_command", "current_date"],
    template="""
You are an expert assistant for extracting calendar event details from user commands. The current date is {current_date}. Use this to interpret relative dates like "this Saturday" or "tomorrow" accurately.

Extract the following fields from the command and return a JSON object with these keys:
- title (string)
- start_time (ISO 8601 string, e.g., "2025-05-31T10:00:00", or null if not specified)
- end_time (ISO 8601 string, or null if not specified)
- description (string or null)

Rules:
- If a relative date (e.g., "this Saturday") is mentioned, calculate it relative to {current_date}.
- If the user specifies a start time but no end time, set the end time to 1 hour after the start time, unless the event type (e.g., "wedding") suggests a longer duration, in which case set a reasonable default (e.g., 4 hours for a wedding).
- If any field is ambiguous or missing, set its value to null and add a "needs_clarification" field with a message describing what is unclear or missing.

Examples:

Command: "Schedule a meeting with John tomorrow at 3pm about the Q2 report"
Current Date: 2025-05-26
Output:
{{
  "title": "Meeting with John about the Q2 report",
  "start_time": "2025-05-27T15:00:00",
  "end_time": "2025-05-27T16:00:00",
  "description": null
}}

Command: "I plan on going for a wedding this Saturday by 10am"
Current Date: 2025-05-26
Output:
{{
  "title": "Wedding",
  "start_time": "2025-05-31T10:00:00",
  "end_time": "2025-05-31T14:00:00",
  "description": null
}}

Command: "Remind me to call Sarah"
Current Date: 2025-05-26
Output:
{{
  "title": "Call Sarah",
  "start_time": null,
  "end_time": null,
  "description": null,
  "needs_clarification": "No time specified. Please provide a date and time for the reminder."
}}

Command: "{user_command}"
Current Date: {current_date}
Output:
"""
)

event_extraction_chain = LLMChain(llm=llm, prompt=prompt)

async def extract_event_details(user_command: str) -> dict:
    response = await event_extraction_chain.arun(
        user_command=user_command,
        current_date=CURRENT_DATE
    )
    try:
        return json.loads(response)
    except Exception:
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {
            "status": "error",
            "result": "Failed to parse event details from LLM output.",
            "raw_response": response
        }