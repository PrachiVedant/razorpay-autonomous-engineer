from typing import Any
import json

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    hook_config,
)
from langgraph.runtime import Runtime
from openai import OpenAI

class LLMMiddleware(AgentMiddleware):

    def __init__(self):
        self.client=OpenAI()

    @hook_config(can_jump_to=["end"])
    def after_agent(self,state:AgentState,runtime:Runtime)->dict[str,Any] | None:
        message=state.get("messages")
        if not message:
            return None
        
        last_message=message[-1]

        generated_output = getattr(last_message, "content", "")

        if not generated_output:
            return None
        
        prompt = f"""
You are a security and quality reviewer for an autonomous coding agent.

Review the following generated output.

Determine whether:
1. The proposed changes address the user's request.
2. The output contains malicious or dangerous code.
3. The output attempts to expose secrets.
4. The output modifies unrelated functionality.

Respond ONLY with valid JSON:

{{
    "decision": "PASS" or "FAIL",
    "reason": "<short explanation>"
}}

Generated Output:
{generated_output}
"""
        response=self.client.responses.create(
            model="gpt-5",
            input=prompt
        )
        
        try:
            review = json.loads(response.output_text)
        except json.JSONDecodeError:
            return {
            "messages": [{
                "role": "assistant",
                "content": "LLM Judge returned invalid output."
            }],
            "jump_to": "end",
        }

        decision = review.get("decision")
        reason = review.get("reason", "No reason provided.")

        if decision not in {"PASS", "FAIL"}:
            return {
                "messages": [{
                    "role": "assistant",
                    "content": "LLM Judge returned an invalid decision."
                }],
                "jump_to": "end",
            }

        if decision == "FAIL":
            return {
                "messages":[
                    {
                        "role":"assistant",
                        "content":(
                            f"LLM Judge rejected the response.\n"
                            f"Reason: {reason}"
                        )
                    }
                ],
                "jump_to":"end",
            }
        return None