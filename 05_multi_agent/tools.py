"""The course catalog tools from Example 02."""

import json
from pathlib import Path

COURSES_FILE = Path(__file__).resolve().parent.parent / "data" / "courses.json"


def load_courses() -> list[dict]:
    """Read data/courses.json and return one flat list of courses."""
    program = json.loads(COURSES_FILE.read_text(encoding="utf-8"))
    return [
        {**course, "semester": semester["number"]}
        for semester in program["semesters"]
        for course in semester["courses"]
    ]


def list_courses(semester: int | None = None) -> list[dict]:
    """List the courses of the Data and Web Science (DWS) master program.

    Args:
        semester: Only return the courses of this semester (1 or 2). Leave empty for all courses.
    """
    courses = load_courses()
    if semester is not None:
        courses = [course for course in courses if course["semester"] == semester]
    return courses


def get_course(code: str) -> dict:
    """Get one course of the DWS program by its course code.

    Args:
        code: The course code, for example 'DWS105'.
    """
    for course in load_courses():
        if course["code"].lower() == code.strip().lower():
            return course
    return {"error": f"There is no course with code {code!r}."}
