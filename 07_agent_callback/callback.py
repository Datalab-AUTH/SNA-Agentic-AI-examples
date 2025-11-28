import os
from google.adk.agents.callback_context import CallbackContext


async def save_session_callback(callback_context: CallbackContext):
    session = callback_context.session
    output_dir = "saved_sessions"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"session_{session.id}.json")

    session_json = session.model_dump_json(exclude_none=True, indent=2)

    with open(file_path, "w") as f:
        f.write(session_json)
    print(f"Session conversation saved to {file_path}")