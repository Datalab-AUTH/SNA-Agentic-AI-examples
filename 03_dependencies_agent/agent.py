"""
Example 03 - Dependencies, RunContext and dynamic instructions
=============================================================

Real agents need data that only exists at RUN time: who the user is, a
database connection, an HTTP client... In Pydantic AI you pass such things
as DEPENDENCIES ("deps"). Instructions and tools can read them through the
RunContext object (`ctx.deps`).

You will also see ModelRetry: a tool can tell the LLM "that was wrong, try
again" - and the LLM gets a second chance.

Run from the repository root:
    python 03_dependencies_agent/agent.py
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from tools import find_course, load_courses

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)


# 1. Describe the dependencies. A dataclass is the usual choice.
@dataclass
class StudentProfile:
    name: str
    semester: int
    completed_courses: list[str]  # course codes, e.g. ["DWS101", "DWS105"]


# 2. Tell the agent which TYPE of dependencies it will receive (deps_type).
#    This gives you type checking and auto-completion for ctx.deps.
advisor_agent = Agent(
    model,
    name="study_advisor",
    deps_type=StudentProfile,
    instructions=(
        "You are a study advisor for the Data and Web Science master program at the "
        "Aristotle University of Thessaloniki. Use your tools to look up the student's "
        "courses. Never guess course codes or ECTS numbers."
    ),
)


# 3. DYNAMIC instructions: a function that is called at the start of every run.
#    It receives the RunContext, so the text can depend on the deps.
@advisor_agent.instructions
def personalise(ctx: RunContext[StudentProfile]) -> str:
    return f"You are talking to {ctx.deps.name}, who is in semester {ctx.deps.semester}."


# 4. Tools that need the run context use @agent.tool (not tool_plain).
#    The first parameter is the RunContext; the LLM never sees it.
@advisor_agent.tool
def completed_courses(ctx: RunContext[StudentProfile]) -> list[dict]:
    """Return the courses the student has already completed."""
    courses = [find_course(code) for code in ctx.deps.completed_courses]
    return [course for course in courses if course is not None]


@advisor_agent.tool
def earned_ects(ctx: RunContext[StudentProfile]) -> float:
    """Return the total number of ECTS credits the student has earned so far."""
    return sum(course["ects"] for course in completed_courses(ctx))


@advisor_agent.tool
def remaining_courses(ctx: RunContext[StudentProfile], semester: int) -> list[dict]:
    """Return the courses of a semester that the student has NOT completed yet.

    Args:
        semester: The semester number (1 or 2).
    """
    done = {code.lower() for code in ctx.deps.completed_courses}
    return [
        course
        for course in load_courses()
        if course["semester"] == semester and course["code"].lower() not in done
    ]


# 5. ModelRetry: when the LLM passes a bad argument, raise ModelRetry with a hint.
#    Pydantic AI sends the message back to the LLM, which can then try again.
@advisor_agent.tool(retries=2)
def course_details(ctx: RunContext[StudentProfile], code: str) -> dict:
    """Get the details (title, ECTS, semester, type) of one course.

    Args:
        code: The course code, e.g. 'DWS105'.
    """
    course = find_course(code)
    if course is None:
        valid_codes = ", ".join(course["code"] for course in load_courses())
        raise ModelRetry(f"There is no course {code!r}. Valid codes are: {valid_codes}")
    return course


if __name__ == "__main__":
    # The SAME agent, two different students -> two different, personalised answers.
    maria = StudentProfile(name="Maria", semester=2, completed_courses=["DWS101", "DWS104", "DWS105"])
    nikos = StudentProfile(name="Nikos", semester=1, completed_courses=[])

    question = "How many ECTS have I earned so far, and which 1st semester courses do I still need?"
    for student in [maria, nikos]:
        result = advisor_agent.run_sync(question, deps=student)  # <- deps are passed per run
        print(f"\n=== {student.name} ===\n{result.output}")
