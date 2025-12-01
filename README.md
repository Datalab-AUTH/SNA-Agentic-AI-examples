# SNA-Agentic-AI-Examples

A repository demonstrating examples of Agentic AI using the Google Agent Developer Kit (ADK).

## Getting Started

Follow these steps to set up your environment and run the Agentic AI examples.

### Prerequisites

    Python 3.11 installed on your system.

    A Google API Key for access to the Gemini API (this is not needed you use Datalab LLM)

### API Key Setup

    Obtain a Key: Get a free Google API Key from the Google AI Studio: https://aistudio.google.com.

    Create .env file: In the root directory of this repository, create a file named .env.

    Add Key: Inside the .env file, add your API key with the following format:
    Bash

    GOOGLE_API_KEY="YOUR_API_KEY_HERE"

#### Using Alternative LLMs (Datalab)

if you want to use alternative LLMs from the Datalab server at Aristotle University, add these additional variables to your .env file:

**Note:** You must be connected to the AUTH VPN to access the Datalab's LLM.

```bash
OLLAMA_API_BASE="https://babili.csd.auth.gr:11435"
```

### Environment Setup

    Install Dependencies: Open your terminal in the root directory and install the required packages:
    Bash

    pip install -r requirements.txt

## Running the Examples

This repository includes multiple methods for running the agents: the ADK Web UI, Command-Line Runners, and Docker-based persistent sessions.

### Examples 1-4: Using the ADK Web UI

The Google ADK provides a local web interface for easily testing and interacting with your agents.

1. **Start the Local Server**: From the root directory, run the following command:
   ```bash
   adk web
   ```

2. **Access the UI**: A local server will start, typically accessible at: http://localhost:8000

3. **Select Examples**: You can select and run the first four examples directly from the ADK Web UI environment.

#### Example Details:
- **01_hello_world_agent**: Basic agent setup and interaction
- **02_tool_calling_agent**: Agent with tool integration
- **03_agent_as_tool_calling_agent**: Hierarchical agent structure where one agent uses another as a tool
- **04_output_schema_tool_calling_agent**: Agent with structured output schemas

### Example 5: Command-Line Agent Runner (In-Memory Sessions)

The fifth example demonstrates how to run an agent directly from the command line with in-memory session management.

**Run the Agent**: Execute the Python script from your terminal:
```bash
python 05_sdk_agents_operations/agent_runner.py
```

The agent will execute its defined workflow and output the results directly in the terminal using in-memory session storage.

### Example 6: Command-Line Agent Runner with Database Sessions

This example demonstrates persistent session management using PostgreSQL for storing conversation history.

#### Setup PostgreSQL with Docker

1. **Build the Docker image**:
   ```bash
   docker build -t postgres-agent -f 06_sdk_agents_operations/Dockerfile 06_sdk_agents_operations/
   ```

2. **Run the PostgreSQL container**:
   ```bash
   docker run -d -p 5432:5432 --name postgres-agent postgres-agent
   ```

   This creates a PostgreSQL database with:
   - Username: `agent_user`
   - Password: `agent_password`
   - Database: `agent_sessions`
   - Port: `5432`

3. **Run the Agent**:
   ```bash
   python 06_sdk_agents_operations/agent_runner.py
   ```

**Key Features**:
- Persistent session storage in PostgreSQL
- Conversation history maintained across runs
- Session management with user and application context
- Same user can continue conversations by reusing session IDs

**Managing the Docker Container**:
- Stop container: `docker stop postgres-agent`
- Start container: `docker start postgres-agent`
- Remove container: `docker rm postgres-agent`
- View logs: `docker logs postgres-agent`

### Example 7: Agent with Callbacks

This example demonstrates using callbacks to save session data after each agent interaction, running through the ADK Web UI.

**Run with ADK Web UI**:
```bash
adk web
```

Then select example `07_agent_callback` from the UI.

**Key Features**:
- Implements `after_agent_callback` to execute custom logic after each agent turn
- Automatically saves complete session history to JSON files
- Sessions saved to `saved_sessions/` directory
- Each session file named as `session_{session_id}.json`
- Useful for debugging, logging, and conversation analysis

**Note**: The `saved_sessions/` directory will be created automatically if it doesn't exist.
