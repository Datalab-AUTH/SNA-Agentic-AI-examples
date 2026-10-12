"""
Example 05b - Programmatic hand-off: a pipeline of agents
========================================================

Here YOUR Python code decides the order: agent 1 runs, its output is given to
agent 2, and so on (like an assembly line). Nothing magic - just function calls.

  researcher  ->  has tools, collects the raw course data (free text)
  formatter   ->  no tools, turns that text into a validated CourseList

Run from the repository root:
    python 05_multi_agent/pipeline.py
"""

import asyncio
import os
from textwrap import shorten

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from tools import list_courses

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)


class Course(BaseModel):
    code: str
    title: str
    ects: float
    semester: int


class CourseList(BaseModel):
    courses: list[Course] = Field(description="The courses that answer the request")


researcher = Agent(
    model,
    name="researcher",
    instructions=(
        "Use the list_courses tool to find the courses that answer the request. "
        "Reply with the code, title, ECTS and semester of every matching course."
    ),
    tools=[list_courses],
)

formatter = Agent(
    model,
    name="formatter",
    output_type=CourseList,
    instructions="Convert the course information you are given into the requested structure.",
)


async def find_courses(request: str) -> CourseList:
    # Step 1: research (may call tools)
    research = await researcher.run(request)
    print(f"[researcher] {shorten(research.output, 200)}\n")

    # Step 2: format. We pass step 1's usage on, so the usage counts add up.
    formatted = await formatter.run(
        f"Request: {request}\n\nCourse information:\n{research.output}",
        usage=research.usage,
    )
    print(f"[pipeline] {formatted.usage.requests} LLM requests in total\n")
    return formatted.output


if __name__ == "__main__":
    course_list = asyncio.run(find_courses("All 1st semester courses with 'Analysis' in the title"))
    for course in course_list.courses:
        print(f"  {course.code:<8} {course.title:<40} sem {course.semester}  {course.ects} ECTS")
