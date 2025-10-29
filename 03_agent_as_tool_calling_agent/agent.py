from google.adk.agents import Agent
from .tools import fetch_courses
from google.adk.tools import AgentTool, FunctionTool


fetch_courses_agent = Agent(
    name="DWS_SNA_Course_Info_Agent",
    model="gemini-2.0-flash-lite",
    instruction=
    "Use the fetch_courses tool to get information about the courses offered in the program.",
    tools=[
        FunctionTool(fetch_courses)
    ]
)

root_agent = Agent(
    name="DWS_SNA_Assistant_Agent",
    model="gemini-2.0-flash-lite",
    instruction=
    "You are a friendly assistant that helps the Social Network Analysis master students" \
    "from the Data and Web Science program at the Aristotele University of Thessaloniki."\
    "Call the fetch_courses_agent to get information about the courses offered in the program.",
    tools=[
        AgentTool(fetch_courses_agent)
    ],

)

