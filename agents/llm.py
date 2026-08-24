import os
from dotenv import load_dotenv

load_dotenv()
from langchain_openai import ChatOpenAI


class OpenAIProvider:
    def __init__(self):
        self.default_model = "gpt-5"
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
    ):
        llm = ChatOpenAI(
            model=model or self.default_model,
            api_key=self.api_key,
        )

        kwargs = {}

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = llm.invoke(prompt, **kwargs)

        return response.content