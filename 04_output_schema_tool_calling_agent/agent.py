from google.adk.agents import Agent, SequentialAgent
from .tools import fetch_courses
from google.adk.tools import AgentTool, FunctionTool
from .schemas import CoursesResponse
from google.adk.models.lite_llm import LiteLlm


# Use Datalab LLM

fetch_courses_agent = Agent(
    name="DWS_SNA_Course_Info_Agent",
    model=LiteLlm(model="openai/llama3.1:8b"),
    instruction=
    "Use the fetch_courses tool to get information about the courses offered in the program.",
    tools=[
        FunctionTool(fetch_courses)
    ]
)

format_agent = Agent(
    name="Courses_Format_Agent",
    model=LiteLlm(model="openai/llama3.1:8b"),
    instruction=
    "Format the course information into a human-readable string format.",
    output_schema=CoursesResponse
)

courses_agent = SequentialAgent(
    name="Courses_Sequential_Agent",
    sub_agents=[
        fetch_courses_agent,
        format_agent
    ],
    description="An agent that fetches course information and formats it."
)
    

root_agent = Agent(
    name="DWS_SNA_Assistant_Agent",
    model=LiteLlm(model="openai/llama3.1:8b"),
    instruction=
    "You are a friendly assistant that helps the Social Network Analysis master students" \
    "from the Data and Web Science program at the Aristotele University of Thessaloniki."\
    "Call the fetch_courses_agent to get information about the courses offered in the program.",
    tools=[
        AgentTool(courses_agent)
    ],

)



# Use Gemini LLM
# fetch_courses_agent = Agent(
#     name="DWS_SNA_Course_Info_Agent",
#     model="gemini-2.0-flash-lite",
#     instruction=
#     "Use the fetch_courses tool to get information about the courses offered in the program.",
#     tools=[
#         FunctionTool(fetch_courses)
#     ]
# )

# format_agent = Agent(
#     name="Courses_Format_Agent",
#     model="gemini-2.0-flash-lite",
#     instruction=
#     "Format the course information into a human-readable string format.",
#     output_schema=CoursesResponse
# )

# courses_agent = SequentialAgent(
#     name="Courses_Sequential_Agent",
#     sub_agents=[
#         fetch_courses_agent,
#         format_agent
#     ],
#     description="An agent that fetches course information and formats it."
# )
    

# root_agent = Agent(
#     name="DWS_SNA_Assistant_Agent",
#     model="gemini-2.0-flash-lite",
#     instruction=
#     "You are a friendly assistant that helps the Social Network Analysis master students" \
#     "from the Data and Web Science program at the Aristotele University of Thessaloniki."\
#     "Call the fetch_courses_agent to get information about the courses offered in the program.",
#     tools=[
#         AgentTool(courses_agent)
#     ],

# )

