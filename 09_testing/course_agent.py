"""
The agent we want to test in Example 09 (a compact version of Example 03's advisor).

Run it for real from the repository root:
    python 09_testing/course_agent.py
Test it WITHOUT an LLM:
    pytest 09_testing -v
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

COURSES_FILE = Path(__file__).resolve().parent.parent / "data" / "courses.json"


def load_courses() -> list[dict]:
    """Read data/courses.json and return one flat list of courses."""
    program = json.loads(COURSES_FILE.read_text(encoding="utf-8"))
    return [
        {**course, "semester": semester["number"]}
        for semester in program["semesters"]
        for course in semester["courses"]
    ]


def find_course(code: str) -> dict | None:
    """Return the course with this code, or None if it does not exist."""
    for course in load_courses():
        if course["code"].lower() == code.strip().lower():
            return course
    return None


@dataclass
class StudentProfile:
    name: str
    completed_courses: list[str]


model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

advisor_agent = Agent(
    model,
    name="study_advisor",
    deps_type=StudentProfile,
    instructions="You are a study advisor for the Data and Web Science master program. Use your tools.",
)


@advisor_agent.instructions
def personalise(ctx: RunContext[StudentProfile]) -> str:
    return f"The student's name is {ctx.deps.name}."


@advisor_agent.tool
def my_completed_courses(ctx: RunContext[StudentProfile]) -> list[dict]:
    """Return the courses the student has already completed."""
    courses = [find_course(code) for code in ctx.deps.completed_courses]
    return [course for course in courses if course is not None]


@advisor_agent.tool_plain(retries=2)
def course_details(code: str) -> dict:
    """Get the details of one course.

    Args:
        code: The course code, e.g. 'DWS105'.
    """
    course = find_course(code)
    if course is None:
        raise ModelRetry(f"There is no course {code!r}. Course codes look like 'DWS105'.")
    return course


if __name__ == "__main__":
    maria = StudentProfile(name="Maria", completed_courses=["DWS101", "DWS105"])
    result = advisor_agent.run_sync("What is DWS207 about, and which courses have I completed?", deps=maria)
    print(result.output)
