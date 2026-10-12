"""Helpers to read the course catalog (same data as Example 02)."""

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


def find_course(code: str) -> dict | None:
    """Return the course with this code, or None if it does not exist."""
    for course in load_courses():
        if course["code"].lower() == code.strip().lower():
            return course
    return None
