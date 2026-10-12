"""
Example 08 - Hooks: run your own code at every step of the agent loop
====================================================================

Hooks are functions that Pydantic AI calls at fixed moments of a run:

    before_run
      before_model_request -> (LLM) -> before_tool_execute -> (tool) -> after_tool_execute
      ... repeated until the LLM gives its final answer ...
    after_run

A "wrap" hook surrounds a whole step (here: the whole run), so it can do
something before AND after it - e.g. measure how long it takes.

Use hooks for logging, measuring, guard rails, or - like here - saving every
finished session to a JSON file. Hooks are collected in a `Hooks` object and
given to the agent as a CAPABILITY.

Run from the repository root:
    python 08_hooks/agent.py
"""

import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, AgentRunResult, ConversationTypeAdapter, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks, WrapRunHandler
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from tools import list_courses

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

SAVED_SESSIONS_DIR = Path("saved_sessions")

hooks = Hooks()


@hooks.on.before_run
async def log_start(ctx: RunContext) -> None:
    print(f"[before_run]           prompt: {ctx.prompt!r}")


@hooks.on.before_model_request
async def log_model_request(ctx: RunContext, request_context: ModelRequestContext) -> ModelRequestContext:
    print(f"[before_model_request] sending {len(request_context.messages)} message(s) to the LLM")
    return request_context  # you could change the request here


@hooks.on.before_tool_execute
async def log_tool_call(ctx: RunContext, *, call, tool_def, args: dict) -> dict:
    print(f"[before_tool_execute]  {call.tool_name}({args})")
    return args  # you could change the arguments here


@hooks.on.after_tool_execute
async def log_tool_result(ctx: RunContext, *, call, tool_def, args: dict, result):
    print(f"[after_tool_execute]   {call.tool_name} returned {len(result)} item(s)")
    return result  # you could change the result here


@hooks.on.after_run
async def save_session(ctx: RunContext, *, result: AgentRunResult) -> AgentRunResult:
    """Save the whole session (all messages + usage) to saved_sessions/ as JSON."""
    SAVED_SESSIONS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = SAVED_SESSIONS_DIR / f"session_{timestamp}_{result.conversation_id}.json"
    path.write_bytes(ConversationTypeAdapter.dump_json(result.conversation, indent=2))
    print(f"[after_run]            session saved to {path}")
    return result


# A wrap hook: `hooks.on.run` wraps the whole run. Calling handler() runs everything above.
@hooks.on.run
async def measure_time(ctx: RunContext, *, handler: WrapRunHandler) -> AgentRunResult:
    start = time.perf_counter()
    result = await handler()
    print(f"[run]                  the whole run took {time.perf_counter() - start:.1f}s")
    return result


agent = Agent(
    model,
    name="course_agent_with_hooks",
    instructions=(
        "You help the Social Network Analysis master students with questions about the courses "
        "of the Data and Web Science program. Use your tools."
    ),
    tools=[list_courses],
    capabilities=[hooks],  # <- plug the hooks into the agent
)

if __name__ == "__main__":
    result = agent.run_sync("How many courses are there in the 1st semester?")
    print(f"\nANSWER: {result.output}")
