"""
Example 01 - Hello World agent
=============================

The smallest useful Pydantic AI program: a MODEL + an AGENT + a RUN.

Run from the repository root:
    python 01_hello_world_agent/agent.py
"""

import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# Copy OPENWEBUI_BASE_URL, OPENWEBUI_API_KEY and OPENWEBUI_MODEL from .env into os.environ.
load_dotenv()

# 1. The MODEL: which LLM to use and how to reach it.
#    Open WebUI offers an OpenAI-compatible "Chat Completions" API, so we use
#    Pydantic AI's OpenAI model class and point it at our Open WebUI server.
model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

# 2. The AGENT: a model plus instructions (the "system prompt").
#    Create agents once (e.g. at module level) and reuse them for many runs.
agent = Agent(
    model,
    name="hello_world_agent",
    instructions=(
        "You are a friendly assistant that greets the Social Network Analysis master students "
        "from the Data and Web Science program at the Aristotle University of Thessaloniki."
    ),
)

if __name__ == "__main__":
    # 3. RUN the agent. run_sync() sends the prompt and waits for the final answer.
    result = agent.run_sync("Hi! Who are you, and who are you talking to?")

    print(result.output)  # the answer: a str, because we did not ask for structured output
    print()
    print(f"Requests to the LLM: {result.usage.requests}")
    print(f"Tokens in / out:     {result.usage.input_tokens} / {result.usage.output_tokens}")
