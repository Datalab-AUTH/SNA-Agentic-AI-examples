from google.adk.agents import Agent

root_agent = Agent(
    name="HelloWorldAgent",
    model="gemini-2.0-flash-lite",
    instruction=
    "You are a friendly assistant that greets the Social Network Analysis master students" \
    "from the Data and Web Science program at the Aristotele University of Thessaloniki.",
)

