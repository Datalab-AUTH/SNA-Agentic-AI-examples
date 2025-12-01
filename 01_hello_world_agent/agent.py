from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


# Use Datalab LLM
root_agent = Agent(
    name="HelloWorldAgent",
    model=LiteLlm(model="ollama_chat/llama3.1:8b"),
    instruction=
 "You are a friendly assistant that greets the Social Network Analysis master students" \
    "from the Data and Web Science program at the Aristotele University of Thessaloniki.",
)


# Use Gemini LLM
# root_agent = Agent(
#     name="HelloWorldAgent",
#     model="gemini-2.0-flash-lite",
#     instruction=
#     "You are a friendly assistant that greets the Social Network Analysis master students" \
#     "from the Data and Web Science program at the Aristotele University of Thessaloniki.",
# )

