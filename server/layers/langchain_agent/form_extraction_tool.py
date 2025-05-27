import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    temperature=0.5
)

DEFAULTS = {
    "country": "Nigeria",
    "gender": "male"
}

prompt = PromptTemplate(
    input_variables=["user_command", "defaults"],
    template="""
You are an expert assistant for extracting and inferring web form fields from user commands. Use the following defaults if a field is not specified:
{defaults}

Extract all possible fields for a web form from the command and return a JSON object with these keys:
- name (string or null)
- email (string or null)
- country (string or null)
- gender (string or null)
- any other fields mentioned (add as key-value pairs)

Rules:
- If a field is not specified, use the default value if available.
- If a required field (name, email) is missing, set its value to null and add a "needs_clarification" field with a message describing what is missing.
- If you can infer a field from context, do so (e.g., "sign me up" implies a registration form).
- Return all extracted and inferred fields in the JSON output.

Examples:

Command: "Sign me up for a tech newsletter on example.com with my name John Doe and email john.doe@example.com"
Defaults: {"country": "Nigeria", "gender": "male"}
Output:
{{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "country": "Nigeria",
  "gender": "male"
}}

Command: "Register for the event with email jane@sample.com"
Defaults: {"country": "Nigeria", "gender": "male"}
Output:
{{
  "name": null,
  "email": "jane@sample.com",
  "country": "Nigeria",
  "gender": "male",
  "needs_clarification": "Name is required but not provided. Please provide your name."
}}

Command: "Fill the registration form on example.com with my details"
Defaults: {"country": "Nigeria", "gender": "male"}
Output:
{{
  "name": null,
  "email": null,
  "country": "Nigeria",
  "gender": "male",
  "needs_clarification": "Name and email are required but not provided. Please provide your name and email."
}}

Command: "{user_command}"
Defaults: {defaults}
Output:
"""
)

form_extraction_chain = LLMChain(llm=llm, prompt=prompt)

async def extract_form_fields(user_command: str) -> dict:
    defaults_str = json.dumps(DEFAULTS)
    response = await form_extraction_chain.arun(
        user_command=user_command,
        defaults=defaults_str
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
            "result": "Failed to parse form fields from LLM output.",
            "raw_response": response
        } 