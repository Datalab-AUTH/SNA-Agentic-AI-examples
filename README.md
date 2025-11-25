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

```bash
OPENAI_API_KEY="sk-5f2d89665d45439eb3d460f38b996abf"
OPENAI_API_BASE="https://babili.csd.auth.gr/api"
```

### Environment Setup

    Install Dependencies: Open your terminal in the root directory and install the required packages:
    Bash

    pip install -r requirements.txt

## Running the Examples

This repository includes two main methods for running the agents: the ADK Web UI and a Command-Line Runner.

Examples 1-4: Using the ADK Web UI

The Google ADK provides a local web interface for easily testing and interacting with your agents.

    Start the Local Server: From the root directory, run the following command:
    Bash

    adk web

    Access the UI: A local server will start, typically accessible at: http://localhost:8000

    Select Examples: You can select and run the first four examples directly from the ADK Web UI environment.

Example 5: Command-Line Agent Runner

The fifth example demonstrates how to run an agent directly from the command line, which is useful for integration and deployment.

    Run the Agent: Execute the Python script from your terminal:
    Bash

    python 05_sdk_agents_operations/agent_runner.py

    The agent will execute its defined workflow and output the results directly in the terminal.
