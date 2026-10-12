"""
Example 04 (extra) - The three ways to get structured output
===========================================================

Pydantic AI can ask an LLM for structured data in three ways:

  ToolOutput     (the default) The schema is offered to the LLM as a special
                 "final_result" tool; the LLM "calls" it with the answer.
  NativeOutput   The server forces the LLM to produce JSON that matches the
                 schema ("structured outputs" / response_format).
  PromptedOutput The schema is written into the instructions and the LLM's
                 text is parsed. Works with any model, but is the least strict.

If one mode gives bad results with your model, try another one.

Run from the repository root:
    python 04_structured_output_agent/output_modes.py
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput, PromptedOutput, ToolOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)


class Paper(BaseModel):
    """Bibliographic information about a scientific paper."""

    title: str
    authors: list[str] = Field(description="Author names, in order")
    year: int
    topic: str = Field(description="The research area in at most three words")


TEXT = (
    "In 1998, Duncan J. Watts and Steven H. Strogatz published 'Collective dynamics of "
    "small-world networks' in Nature, showing that a few random shortcuts make a regular "
    "lattice behave like a small world."
)

if __name__ == "__main__":
    for output_type in [ToolOutput(Paper), NativeOutput(Paper), PromptedOutput(Paper)]:
        agent = Agent(model, output_type=output_type, instructions="Extract the paper information.")
        result = agent.run_sync(TEXT)
        print(f"{type(output_type).__name__:<15} -> {result.output!r}")
