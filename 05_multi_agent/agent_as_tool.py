"""
Example 05a - Agent delegation: an agent used as a tool
======================================================

A "main" assistant talks to the student. When it needs course information it
calls a TOOL, and inside that tool a second, specialised agent does the work.
The main agent gets the answer back and continues the conversation.

Why split the work? Each agent gets short, focused instructions and only the
tools it needs - which makes (especially small) LLMs much more reliable.

Run from the repository root:
    python 05_multi_agent/agent_as_tool.py
"""

import os
from textwrap import shorten

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from tools import get_course, list_courses

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

# The SPECIALIST: knows the course catalog, nothing else.
course_expert = Agent(
    model,
    name="course_expert",
    instructions=(
        "You answer factual questions about the courses of the Data and Web Science program. "
        "Always use your tools. Answer briefly and only with facts from the tools."
    ),
    tools=[list_courses, get_course],
)

# The MAIN agent: friendly, talks to the student, delegates course questions.
assistant = Agent(
    model,
    name="sna_assistant",
    instructions=(
        "You are a friendly assistant for the Social Network Analysis master students at the "
        "Aristotle University of Thessaloniki. For ANY question about courses, ECTS or semesters, "
        "use the ask_course_expert tool - do not answer such questions from memory."
    ),
)


@assistant.tool
async def ask_course_expert(ctx: RunContext, question: str) -> str:
    """Ask the course expert a question about the courses of the Data and Web Science program.

    Args:
        question: A complete, self-contained question about the courses.
    """
    print(f"  [assistant -> course_expert] {question}")
    # Run the other agent INSIDE this tool. Passing usage=ctx.usage adds the expert's
    # token usage to the main run, so result.usage shows the total cost.
    result = await course_expert.run(question, usage=ctx.usage)
    print(f"  [course_expert -> assistant] {shorten(result.output, 100)}")
    return result.output


if __name__ == "__main__":
    result = assistant.run_sync(
        "Hi! I love graphs and networks. Which course should I take, and in which semester is it?",
        # Safety net for multi-agent systems: stop if something loops.
        usage_limits=UsageLimits(request_limit=10),
    )
    print(f"\n{result.output}")
    print(f"\nLLM requests in total (both agents): {result.usage.requests}")
