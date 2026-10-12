"""
Example 06 - Conversations, async and streaming
==============================================

Every agent run is independent: the LLM does NOT remember earlier runs on its
own. To have a conversation, you pass the previous conversation into the next
run. Each result gives you `result.conversation` (all messages so far); you
hand it back with `conversation=...`.

This chat also STREAMS the answer: words are printed as they arrive instead of
all at once at the end. Streaming needs the async API (`async`/`await`).

Run from the repository root:
    python 06_conversations/chat.py
"""

import asyncio
import os

from dotenv import load_dotenv
from pydantic_ai import Agent, Conversation
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from tools import get_course, list_courses

load_dotenv()

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

agent = Agent(
    model,
    name="course_chat_agent",
    instructions=(
        "You are a friendly assistant for the Social Network Analysis master students at the "
        "Aristotle University of Thessaloniki. Use your tools for course information. "
        "Keep your answers short."
    ),
    tools=[list_courses, get_course],
)


async def main() -> None:
    conversation: Conversation | None = None  # no history before the first message

    print("Chat with the course assistant. Type 'exit' to quit.")
    while True:
        user_message = input("\nyou> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break
        if not user_message:
            continue

        # run_stream() is an async context manager; stream_text(delta=True) yields new text pieces.
        async with agent.run_stream(user_message, conversation=conversation) as run:
            print("agent> ", end="", flush=True)
            async for text_piece in run.stream_text(delta=True):
                print(text_piece, end="", flush=True)
            print()

        # Keep the whole conversation (all messages + usage) for the next turn.
        conversation = run.result.conversation
        print(f"      ({len(conversation.messages)} messages in memory)")


if __name__ == "__main__":
    asyncio.run(main())
