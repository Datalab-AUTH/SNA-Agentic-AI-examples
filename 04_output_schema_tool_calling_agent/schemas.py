from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import List

"""
		- code (str)
		- title (str)
		- ects (number)
		- type (str)
		- semester_number (int)
		- semester_name (str)

"""

@dataclass
class Course(BaseModel):
    code: str = Field(
        ...,
        description="The course code, e.g., 'SNA101'",
    )
    title: str = Field(
        ...,
        description="The title of the course, e.g., 'Introduction to Social Network Analysis'",
    )
    ects: float = Field(
        ...,
        description="The ECTS credits for the course, e.g., 6.0",
    )
    type: str = Field(
        ...,
        description="The type of the course, e.g., 'Mandatory' or 'Elective'",
    )
    semester_number: int = Field(
        ...,
        description="The semester number in which the course is offered, e.g., 1 for first semester",
    )
    semester_name: str = Field(
        ...,
        description="The name of the semester, e.g., 'Fall 2024'",
    )

@dataclass
class CoursesResponse(BaseModel):
    courses: List[Course] = Field(
        ...,
        description="A list of course dictionaries with detailed information.",
    )

