# SNA Agentic AI Examples

Examples for building AI agents with [Pydantic AI](https://pydantic.dev/docs/ai/overview/), using the course LLMs through [Open WebUI](https://filos.csd.auth.gr/).

## Setup

You need Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```


1. Copy `.env.example` to `.env` and paste your key into it. Never commit `.env`.
2. Check the connection:

```bash
python 00_check_connection/check_connection.py
```

Run all examples from the repository root.

## Connecting Pydantic AI to Open WebUI

Open WebUI offers an OpenAI-compatible API under `/api`, so we use Pydantic AI's OpenAI chat model. Every example starts like this:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    os.environ["OPENWEBUI_MODEL"],                    # e.g. datalab-2:latest
    provider=OpenAIProvider(
        base_url=os.environ["OPENWEBUI_BASE_URL"],    # https://filos.csd.auth.gr/api
        api_key=os.environ["OPENWEBUI_API_KEY"],
    ),
)

agent = Agent(model, instructions="You are a helpful assistant.")
result = agent.run_sync("Hello!")
print(result.output)
```

## Examples

Each file starts with a short explanation. Read the code from top to bottom.

| Example | Run | What it shows |
|---|---|---|
| 01 Hello world | `python 01_hello_world_agent/agent.py` | Model, agent, instructions, `run_sync()` |
| 02 Tools | `python 02_tool_calling_agent/agent.py` | Python functions that the LLM can call |
| 03 Dependencies | `python 03_dependencies_agent/agent.py` | `deps`, `RunContext`, dynamic instructions, `ModelRetry` |
| 04 Structured output | `python 04_structured_output_agent/agent.py` | Pydantic models as answers, output validators |
| | `python 04_structured_output_agent/output_modes.py` | Tool, native and prompted output modes |
| 05 Multi-agent | `python 05_multi_agent/agent_as_tool.py` | An agent called from another agent's tool |
| | `python 05_multi_agent/pipeline.py` | A pipeline of agents |
| 06 Conversations | `python 06_conversations/chat.py` | Chat history, async, streaming |
| | `python 06_conversations/web_ui.py` | A browser chat UI at <http://127.0.0.1:7932> |
| 07 Persistent sessions | `python 07_persistent_sessions/chat.py --user maria` | Conversations stored in PostgreSQL |
| 08 Hooks | `python 08_hooks/agent.py` | Your own code before and after model requests, tool calls and runs |
| 09 Testing | `pytest 09_testing -v` | Agent tests without an LLM (`TestModel`, `FunctionModel`) |

### Example 07: start PostgreSQL first

```bash
docker build -t postgres-agent -f 07_persistent_sessions/Dockerfile 07_persistent_sessions/
docker run -d -p 5432:5432 --name postgres-agent postgres-agent
```

Use `--list` to see your sessions and `--session <id>` to continue one.

## Cheat sheet

```python
agent = Agent(
    model,
    instructions="...",       # the system prompt
    tools=[my_function],      # functions the LLM may call
    deps_type=MyDeps,         # type of the data passed in at run time
    output_type=MyModel,      # structured answer (default: str)
    capabilities=[hooks],     # hooks and other add-ons
)

@agent.tool_plain             # a tool that needs no context
def add(a: int, b: int) -> int: ...

@agent.tool                   # a tool that reads ctx.deps
def whoami(ctx: RunContext[MyDeps]) -> str: ...

result = agent.run_sync("question", deps=my_deps)
result.output                 # the answer
result.all_messages()         # every message, including tool calls
result.conversation           # pass it as conversation=... to continue the chat
```

## Models

The default is `datalab-2:latest`. `datalab-1` and `datalab-3` also work with every example. The small Llama models (`datalab-4`, `datalab-5`) are faster, but they fail at structured output (examples 04 and 05). To see all models, run `00_check_connection/check_connection.py`.

## Troubleshooting

- **401 Unauthorized:** create a new API key and update `.env`. API keys must be enabled by the Open WebUI admin (*Settings → Admin → Authentication → API Keys*).
- **Cannot connect:** check `OPENWEBUI_BASE_URL` (it must end with `/api`), or connect to the AUTH VPN.
- **The first answer is slow:** the server is loading the model. Later answers are faster.
- **`UnicodeEncodeError` on Windows:** run `$env:PYTHONUTF8=1` in PowerShell before running Python.

## Learn more

- [Pydantic AI docs](https://pydantic.dev/docs/ai/overview/)
- [Open WebUI API](https://docs.openwebui.com/reference/api-endpoints)
