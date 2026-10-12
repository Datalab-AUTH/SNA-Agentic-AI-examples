"""
Example 06 (extra) - Chat with your agent in the browser
=======================================================

Pydantic AI ships a small web chat UI for local development. One line turns
an agent into a web app: `agent.to_web()`. Tool calls are shown in the UI,
which makes it great for debugging.

Run from the repository root, then open http://127.0.0.1:7932
    python 06_conversations/web_ui.py
"""

import uvicorn

from chat import agent  # the same agent as in chat.py

app = agent.to_web()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7932)
