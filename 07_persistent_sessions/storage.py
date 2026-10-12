"""
Save and load Pydantic AI conversations in PostgreSQL.

Pydantic AI does not force a database schema on you. It gives you one thing to
store - the Conversation - and a serializer for it (ConversationTypeAdapter).
Here we keep each conversation as one JSONB value in a single table.
"""

import os
from datetime import datetime

import psycopg
from pydantic_ai import Conversation, ConversationTypeAdapter


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["DATABASE_URL"])


def create_table() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id         TEXT PRIMARY KEY,
                user_id    TEXT NOT NULL,
                data       JSONB NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


def save_conversation(user_id: str, conversation: Conversation) -> None:
    """Insert the conversation, or overwrite it if it is already stored."""
    data = ConversationTypeAdapter.dump_json(conversation).decode()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO conversations (id, user_id, data) VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data, updated_at = now()
            """,
            (conversation.conversation_id, user_id, data),
        )


def load_conversation(user_id: str, conversation_id: str) -> Conversation | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT data::text FROM conversations WHERE id = %s AND user_id = %s",
            (conversation_id, user_id),
        ).fetchone()
    return ConversationTypeAdapter.validate_json(row[0]) if row else None


def list_conversations(user_id: str) -> list[tuple[str, datetime, int]]:
    """Return (id, last update, number of messages) for each of the user's conversations."""
    with connect() as conn:
        return conn.execute(
            """
            SELECT id, updated_at, jsonb_array_length(data -> 'messages')
            FROM conversations WHERE user_id = %s ORDER BY updated_at DESC
            """,
            (user_id,),
        ).fetchall()
