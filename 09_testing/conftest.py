"""pytest loads this file before the tests (it is pytest's place for shared test setup)."""

import os

from pydantic_ai import models

# The tests never talk to a real LLM, but importing course_agent creates the Open WebUI model,
# which reads these settings. Use harmless dummy values, so the tests also run without a .env file.
os.environ.setdefault("OPENWEBUI_BASE_URL", "http://localhost:3000/api")
os.environ.setdefault("OPENWEBUI_API_KEY", "not-a-real-key")
os.environ.setdefault("OPENWEBUI_MODEL", "not-a-real-model")

# Safety net: any test that accidentally calls a real model fails immediately.
models.ALLOW_MODEL_REQUESTS = False
