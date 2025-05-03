# Setup & Prerequisites

Before starting the hands-on exercises, please ensure you have the following setup completed.

## 1. Clone the Repository

All code examples are sourced from the `agentic-playground` repository. Clone it to your local machine:

```bash
git clone https://github.com/denniszielke/agentic-playground.git
cd agentic-playground
```

## 2. Python Environment

We recommend using a virtual environment to manage dependencies.

*   **Ensure Python is installed:** Python 3.9 or higher is recommended.
*   **Create a virtual environment:**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```
*   **Install Dependencies:** The repository includes a `requirements.txt` file listing the necessary Python packages.
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Some examples require additional dependencies (e.g., `pytz`, `graphviz`, `requests`, `pyaudio`, `sounddevice`, `pydub`, `pyperclip`, specific `langchain`, `llama-index`, `semantic-kernel`, or `autogen` components). Install these as needed when running specific examples, following instructions in the module content or error messages.* 
    *For Graphviz visualization (`knowledge-graphs.py`), you also need to install the Graphviz binaries separately:* 
        *   *macOS:* `brew install graphviz`
        *   *Ubuntu/Debian:* `sudo apt-get update && sudo apt-get install -y graphviz`
        *   *Windows:* Download from the official Graphviz website and add to PATH.

## 3. GitHub Personal Access Token (PAT)

Many examples in this repository interact with LLMs hosted via GitHub Models inference endpoints. Accessing these requires a GitHub Personal Access Token (PAT).

*   **Generate a PAT:**
    1.  Go to your GitHub Settings > Developer settings > Personal access tokens > Tokens (classic).
    2.  Click "Generate new token" (or "Generate new token (classic)").
    3.  Give your token a descriptive name (e.g., "Agentic Playground Workshop").
    4.  Set an expiration date.
    5.  **Crucially, for GitHub Models inference, a token with no specific scopes/permissions is sufficient.**
    6.  Click "Generate token".
    7.  **Copy the generated token immediately.** You won't be able to see it again.
*   **Configure the PAT:** The scripts typically use the `python-dotenv` library to load environment variables from a `.env` file in the repository's root directory.
    1.  Create a file named `.env` in the root of the cloned `agentic-playground` directory.
    2.  Add the following line, replacing `your_github_pat_here` with the token you just copied:
        ```
        GITHUB_TOKEN="your_github_pat_here"
        ```

## 4. Key Libraries Overview (High Level)

The repository utilizes several popular libraries for building AI agents:

*   **OpenAI Python Library (`openai`):** Used for interacting with OpenAI-compatible APIs, including the GitHub Models endpoint. Provides methods for chat completions, streaming, tool calling, and multimodal inputs.
*   **LangChain (`langchain`, `langchain-openai`, etc.):** A framework for developing applications powered by language models. Provides tools for managing prompts, chains, agents (like ReAct), memory, and document loading.
*   **LlamaIndex (`llama-index`, `llama-index-llms-openai`, etc.):** A data framework for LLM applications, focusing on connecting LLMs with external data. Also provides agent implementations (like ReAct).
*   **Semantic Kernel (`semantic-kernel`):** A Microsoft-developed SDK for integrating LLMs into applications. Offers features like plugins (tools), planners, memory, and agent abstractions (including process frameworks and agent chats).
*   **AutoGen (`autogen-agentchat`, `autogen-core`, `autogen-ext`):** A framework for enabling multi-agent conversations and workflows, often using an orchestrator model to manage dynamic interactions.
*   **Pydantic:** Used for data validation and defining structured data models (like the `KnowledgeGraph` or state objects).

We will explore specific features of these libraries as we encounter them in the code examples throughout the workshop.

