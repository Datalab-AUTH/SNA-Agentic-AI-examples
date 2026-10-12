"""
Example 02 - Tool calling agent
==============================

Give the agent Python functions ("tools") it may call to look things up.
The LLM decides WHEN to call a tool and WITH WHICH ARGUMENTS; Pydantic AI
runs the function and sends the result back to the LLM.

Run from the repository root:
    python 02_tool_calling_agent/agent.py
"""

import os
from textwrap import shorten

from dotenv import load_dotenv
from pydantic_ai import Agent, AgentRunResult, ToolCallPart, ToolReturnPart
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

agent = Agent(
    model,
    name="course_info_agent",
    instructions=(
        "You are a friendly assistant that helps the Social Network Analysis master students "
        "from the Data and Web Science program at the Aristotle University of Thessaloniki. "
        "Always use your tools to look up course information; never invent courses."
    ),
    # Way 1 to register tools: pass plain functions in the `tools` list.
    tools=[list_courses, get_course],
)


# Way 2 to register tools: the @agent.tool_plain decorator.
# ("plain" = the function does not need the run context; Example 03 shows @agent.tool.)
@agent.tool_plain
def total_ects(course_codes: list[str]) -> float:
    """Add up the ECTS credits of the given courses. Use this instead of doing arithmetic yourself.

    Args:
        course_codes: The course codes to add up, for example ['DWS101', 'DWS105'].
    """
    wanted = {code.strip().lower() for code in course_codes}
    return sum(course["ects"] for course in list_courses() if course["code"].lower() in wanted)


def print_tool_calls(result: AgentRunResult) -> None:
    """Show what happened behind the scenes: which tools the LLM called and what they returned."""
    for message in result.all_messages():
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                print(f"  [LLM -> tool]  {part.tool_name}({part.args_as_dict()})")
            elif isinstance(part, ToolReturnPart):
                print(f"  [tool -> LLM]  {part.tool_name} returned: {shorten(str(part.content), 90)}")


if __name__ == "__main__":
    questions = [
        "Which courses are offered in the 2nd semester?",
        "How many ECTS do DWS101 and DWS105 give together?",
    ]
    for question in questions:
        print(f"\nQUESTION: {question}")
        result = agent.run_sync(question)
        print_tool_calls(result)
        print(f"ANSWER: {result.output}")
