"""
Example 00 - Check your connection to Open WebUI
===============================================

Run this FIRST. It checks, step by step, that:
  1. your .env file has the three settings we need,
  2. the Open WebUI server is reachable and accepts your API key,
  3. the model you picked exists,
  4. the model can chat, and
  5. the model can call tools (needed from Example 02 on).

Run from the repository root:
    python 00_check_connection/check_connection.py
"""

import os
import sys

import openai
from dotenv import load_dotenv
from pydantic_ai import Agent, ToolCallPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

base_url = os.getenv("OPENWEBUI_BASE_URL")
api_key = os.getenv("OPENWEBUI_API_KEY")
model_name = os.getenv("OPENWEBUI_MODEL")


def fail(message: str) -> None:
    print(f"\n[FAIL] {message}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Step 1: the settings
# ---------------------------------------------------------------------------
print("Step 1: reading settings from .env")
for name, value in [
    ("OPENWEBUI_BASE_URL", base_url),
    ("OPENWEBUI_API_KEY", api_key),
    ("OPENWEBUI_MODEL", model_name),
]:
    if not value:
        fail(f"{name} is not set. Copy .env.example to .env and fill it in.")
print(f"  OPENWEBUI_BASE_URL = {base_url}")
print(f"  OPENWEBUI_MODEL    = {model_name}")
if not base_url.rstrip("/").endswith("/api"):
    print("  [WARN] OPENWEBUI_BASE_URL usually ends with /api, e.g. http://localhost:3000/api")

# ---------------------------------------------------------------------------
# Step 2 + 3: list the models (GET {base_url}/models)
# Open WebUI speaks the OpenAI API, so the official `openai` client works as-is.
# ---------------------------------------------------------------------------
print("\nStep 2: asking Open WebUI for its models")
client = openai.OpenAI(base_url=base_url, api_key=api_key)
try:
    available = sorted(model.id for model in client.models.list())
except openai.AuthenticationError:
    fail("Open WebUI rejected your API key. Create a new one in Settings -> Account -> API keys.")
except openai.APIConnectionError:
    fail(f"Cannot reach {base_url}. Is the URL right? Are you connected to the VPN?")
except openai.NotFoundError:
    fail(f"{base_url}/models does not exist. Does OPENWEBUI_BASE_URL end with /api?")

print(f"  The server offers {len(available)} model(s):")
for model_id in available:
    print(f"    - {model_id}")

print("\nStep 3: checking your model")
if model_name not in available:
    fail(f"Model '{model_name}' is not in the list above. Set OPENWEBUI_MODEL to one of them.")
print(f"  '{model_name}' is available.")

# ---------------------------------------------------------------------------
# Step 4: a first Pydantic AI agent (Example 01 explains every line of this)
# ---------------------------------------------------------------------------
model = OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=base_url, api_key=api_key))

print("\nStep 4: sending a test message (the first request can take a while if the model must load)")
agent = Agent(model, instructions="Answer in at most one short sentence.")
result = agent.run_sync("Say hello to the Social Network Analysis students.")
print(f"  The model says: {result.output}")

# ---------------------------------------------------------------------------
# Step 5: tool calling
# ---------------------------------------------------------------------------
print("\nStep 5: checking that the model can call tools")
tool_agent = Agent(model, instructions="Use your tools to answer.")


@tool_agent.tool_plain
def get_room_number() -> str:
    """Return the room where the Social Network Analysis lecture takes place."""
    return "Room B.42"


try:
    result = tool_agent.run_sync("In which room is the Social Network Analysis lecture?")
except openai.BadRequestError as error:
    fail(f"The model rejected the tools ({error}). Pick a model that supports tool calling.")

called_tools = [
    part.tool_name
    for message in result.all_messages()
    for part in message.parts
    if isinstance(part, ToolCallPart)
]
if "get_room_number" in called_tools:
    print(f"  The model called the tool and answered: {result.output}")
else:
    print("  [WARN] The model answered without calling the tool. Tool-calling examples may not work")
    print("         well with this model; try a bigger one (e.g. llama3.1:8b or qwen3).")

print("\n[OK] Everything works. Continue with Example 01!")
