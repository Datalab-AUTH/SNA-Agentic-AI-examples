"""
Pydantic models that describe the SHAPE of the answer we want from the agent.

The field names, types and descriptions are sent to the LLM as a JSON schema,
and the LLM's answer is validated against them. If validation fails, the LLM
is asked to fix its answer automatically.
"""

from pydantic import BaseModel, Field


class Course(BaseModel):
    code: str = Field(description="The course code, e.g. 'DWS105'")
    title: str = Field(description="The title of the course, e.g. 'Social Network Analysis'")
    ects: float = Field(gt=0, description="The ECTS credits of the course, e.g. 7.5")
    semester: int = Field(ge=1, le=2, description="The semester of the course: 1 or 2")


class CourseList(BaseModel):
    """A list of courses that answers the student's request."""

    courses: list[Course] = Field(description="The courses that match the request")
    summary: str = Field(description="One friendly sentence that summarises the list for the student")
