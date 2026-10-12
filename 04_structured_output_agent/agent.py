"""
Example 04 - Structured output
=============================

Instead of free text, ask the agent for a Pydantic model. You get back a
validated Python object that the rest of your program can use directly:
loop over it, sum it, store it in a database, return it from an API...

Run from the repository root:
    python 04_structured_output_agent/agent.py
"""

import os

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from schemas import CourseList
from tools import list_courses, load_courses

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

# output_type=CourseList is the only new thing compared to Example 02.
# result.output will now be a CourseList object instead of a str.
course_agent = Agent(
    model,
    name="course_list_agent",
    output_type=CourseList,
    instructions=(
        "You help students of the Data and Web Science master program find courses. "
        "Use the list_courses tool and only return courses that the tool gave you."
    ),
    tools=[list_courses],
    retries=3,  # allow up to 3 "please fix your answer" round trips
)


# An OUTPUT VALIDATOR runs after the answer passed Pydantic validation.
# Use it for checks a schema cannot express. Raise ModelRetry to make the LLM try again.
@course_agent.output_validator
def only_real_courses(output: CourseList) -> CourseList:
    real_codes = {course["code"] for course in load_courses()}
    invented = [course.code for course in output.courses if course.code not in real_codes]
    if invented:
        raise ModelRetry(f"These course codes do not exist: {invented}. Use the list_courses tool.")
    return output


if __name__ == "__main__":
    result = course_agent.run_sync("Which courses are about data or databases?")
    answer = result.output  # <- a CourseList, not a string!

    print(f"Type of result.output: {type(answer).__name__}\n")
    print(answer.summary)
    print()
    for course in answer.courses:
        print(f"  {course.code:<10} {course.title:<45} sem {course.semester}  {course.ects} ECTS")

    # Because the answer is data, plain Python can work with it reliably:
    print(f"\nTotal: {len(answer.courses)} courses, {sum(c.ects for c in answer.courses)} ECTS")

    print("\nAs JSON (e.g. to return from a web API):")
    print(answer.model_dump_json(indent=2)[:300], "...")
