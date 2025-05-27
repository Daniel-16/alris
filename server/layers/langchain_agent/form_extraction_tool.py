import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    temperature=0
)

DEFAULTS = {
    "country": "Nigeria",
    "gender": "male"
}

prompt = PromptTemplate(
    input_variables=["user_command", "defaults"],
    template="""
You are an expert assistant for extracting user-provided web form fields from commands. Use the following defaults if a field is not specified:
{defaults}

Extract the following from the command and return a JSON object with these keys:
- url (string or null): the URL of the form to fill (extract from the command, or null if not found)
- form_data (object): a dictionary of all fields the user explicitly provided (e.g., name, email, phone, etc.)
- needs_clarification (string, optional): if neither name nor email is present, add a message here describing what is missing

Rules:
- Always try to extract the URL from the command (look for https:// or www. or domain names)
- Extract all user-provided values (e.g., name, email, phone, address, etc.) from the command
- If neither name nor email is present, set needs_clarification
- Output only a single JSON object as described
- Generate a reasonable value for each field if the user does not provide one

Examples:

Command: "Sign me up for a tech newsletter on https://example.com/newsletter with my name John Doe and email john.doe@example.com"
Defaults: {"country": "Nigeria", "gender": "male"}
Output:
{
  "url": "https://example.com/newsletter",
  "form_data": {
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}

Command: "Register for the event at https://event.com/register with email jane@sample.com"
Defaults: {"country": "Nigeria", "gender": "male"}
Output:
{
  "url": "https://event.com/register",
  "form_data": {
    "email": "jane@sample.com"
  }
}

Command: "Fill the registration form on www.example.com with my details"
Defaults: {"country": "Nigeria", "gender": "male"}
Output:
{
  "url": "www.example.com",
  "form_data": {},
  "needs_clarification": "Name and email are required but not provided. Please provide your name and email."
}

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