import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .intent_schema import IntentResult

class IntentDetector:
    def __init__(self):
        self.intents = ["browser", "email", "calendar", "general"]
        self.llm = ChatGoogleGenerativeAI(model=os.getenv('GEMINI_MODEL'), temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=IntentResult)
        self.prompt = PromptTemplate(
            template=(
                "You are an intent detection assistant.\n"
                "Given the following user input, classify it into one of these intents: {intents}.\n"
                "If none fit, return 'general'.\n"
                "Respond in the following JSON format:\n"
                "{format_instructions}\n"
                "User input: {user_input}\n"
            )
        )

    def detect_intent(self, command: str) -> str:
        prompt = self.prompt.format(
            intents=", ".join(self.intents),
            user_input=command,
            format_instructions=self.parser.get_format_instructions()
        )
        result = self.llm.invoke(prompt)
        parsed = self.parser.parse(result.content)
        return parsed.intent