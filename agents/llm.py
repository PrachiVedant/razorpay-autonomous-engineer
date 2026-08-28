from langchain_openai import ChatOpenAI


class OpenAIProvider:
    """
    Small wrapper around the OpenAI chat model.

    Keeping the provider behind this interface allows tests to
    monkeypatch `generate()` without making real API calls.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )

    def generate(
        self,
        prompt,
        model=None,
        max_tokens=None,
    ):
        llm = self.llm

        if model:
            llm = ChatOpenAI(
                model=model,
                temperature=0,
                max_tokens=max_tokens,
            )

        response = llm.invoke(prompt)

        return response.content