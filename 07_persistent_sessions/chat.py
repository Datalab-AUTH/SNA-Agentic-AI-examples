"""
Example 07 - Persistent sessions with PostgreSQL
===============================================

In Example 06 the conversation lived in a Python variable, so it was gone when
the program stopped. Here we save it in PostgreSQL after every turn, so you can
stop the program and continue the same conversation later.

Start the database first (see the README), then run from the repository root:
    python 07_persistent_sessions/chat.py --user maria                 # new session
    python 07_persistent_sessions/chat.py --user maria --list          # your sessions
    python 07_persistent_sessions/chat.py --user maria --session <id>  # continue one
"""

import argparse
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import storage

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
    name="persistent_chat_agent",
    instructions=(
        "You are a friendly assistant for the Social Network Analysis master students at the "
        "Aristotle University of Thessaloniki. Keep your answers short."
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser(description="A chat whose history is stored in PostgreSQL.")
    parser.add_argument("--user", default="student", help="who is chatting")
    parser.add_argument("--session", help="the id of a stored conversation to continue")
    parser.add_argument("--list", action="store_true", help="list the user's stored conversations")
    args = parser.parse_args()

    storage.create_table()

    if args.list:
        for conversation_id, updated_at, n_messages in storage.list_conversations(args.user):
            print(f"{conversation_id}   {updated_at:%Y-%m-%d %H:%M}   {n_messages} messages")
        return

    conversation = None  # None = start a new conversation
    if args.session:
        conversation = storage.load_conversation(args.user, args.session)
        if conversation is None:
            print(f"No conversation {args.session} for user {args.user}. Use --list to see yours.")
            return
        print(f"Continuing a conversation with {len(conversation.messages)} stored messages.")

    print("Type 'exit' to quit.")
    while True:
        user_message = input("\nyou> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break
        if not user_message:
            continue

        result = agent.run_sync(user_message, conversation=conversation)
        print(f"agent> {result.output}")

        conversation = result.conversation
        storage.save_conversation(args.user, conversation)  # <- persist after every turn

    if conversation is not None:
        print(f"\nSaved. Continue later with: --user {args.user} --session {conversation.conversation_id}")


if __name__ == "__main__":
    main()
