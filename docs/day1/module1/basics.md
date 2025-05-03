# Day 1 - Module 1: Basic LLM Interaction & Tool Calling

**Objective:** Understand how to interact with Large Language Models (LLMs) programmatically, handle streaming responses, and enable models to use external tools.

**Source Code:** [`src/01-basics/`](https://github.com/denniszielke/agentic-playground/tree/main/src/01-basics){target="_blank"}

---

## Introduction

At the heart of AI agents lies the ability to interact with powerful Large Language Models (LLMs). These models can understand and generate human-like text, answer questions, translate languages, and much more. In this first module, we will explore the fundamental ways to communicate with an LLM using the OpenAI API pattern (as used by the GitHub Models endpoint in this repository) and introduce the concept of "tool calling," which allows the LLM to interact with external systems or functions.

We will cover:

1.  **Basic API Calls:** Sending a prompt to the model and receiving a complete response.
2.  **Streaming Responses:** Receiving the model's response incrementally as it's generated.
3.  **Tool Calling:** Defining functions (tools) that the model can request to use to gather information or perform actions.

!!! info "Core Concept: LLM Interaction"
    Understanding how to structure API calls, manage conversation history (messages), and interpret responses is foundational for building any LLM-powered application.

## Setup Review

!!! warning "Prerequisites"
    Before running the examples, ensure you have:

    1.  Cloned the `agentic-playground` repository.
    2.  Installed the required Python packages (`pip install -r requirements.txt`).
    3.  Created a `.env` file in the repository root with your `GITHUB_TOKEN` (a Personal Access Token with no specific permissions needed for GitHub Models inference).

    ```
    # .env file content
    GITHUB_TOKEN="your_github_pat_here"
    ```

## 1. Hello World: Basic API Interaction

**File:** [`src/01-basics/hello-world.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/01-basics/hello-world.py){target="_blank"}

This script demonstrates the simplest form of interaction: sending a message to the LLM and getting a single, complete response back.

**Code Breakdown:**

*   **Import necessary libraries:** `os` for environment variables, `OpenAI` for the client, `load_dotenv` to load the `.env` file.

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
```

*   **Initialize the OpenAI Client:**
    *   `base_url`: Points to the GitHub Models inference endpoint.
    *   `api_key`: Reads the `GITHUB_TOKEN` from your environment variables (loaded from `.env`).

```python
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)
```

*   **Define the Conversation:**
    *   Messages are provided as a list of dictionaries, each with a `role` (`system`, `user`, or `assistant`) and `content`.
    *   The `system` message sets the context or instructions for the model (e.g., "antworte alles in französisch" - answer everything in French).
    *   The `user` message contains the user's query.

```python
messages=[
    {
        "role": "system",
        "content": "antworte alles in französisch",
    },
    {
        "role": "user",
        "content": "What is the capital of France?",
    }
]
```

*   **Call the Chat Completions API:**
    *   `client.chat.completions.create()` sends the request.
    *   `messages`: The conversation history/prompt.
    *   `model`: Specifies the model to use (e.g., `gpt-4o-mini`).
    *   `temperature`, `max_tokens`, `top_p`: Control the creativity, length, and sampling strategy of the response.

```python
response = client.chat.completions.create(
    messages=messages,
    model="gpt-4o-mini",
    temperature=1,
    max_tokens=4096,
    top_p=1
)
```

*   **Print the Response:**
    *   The model's reply is found within the `response` object.

```python
print(response.choices[0].message.content)
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/01-basics
python hello-world.py
```

You should see the answer to "What is the capital of France?" printed in French.

## 2. Streaming Output

**File:** [`src/01-basics/streaming-output.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/01-basics/streaming-output.py){target="_blank"}

Sometimes, waiting for the entire response can take time, especially for longer answers. Streaming allows you to receive the response piece by piece, making the interaction feel more responsive.

**Code Breakdown:**

*   **Client Setup:** Similar to `hello-world.py`.
*   **API Call with Streaming:**
    *   The key difference is `stream=True`.
    *   `stream_options={'include_usage': True}` optionally requests token usage information at the end.

```python
response = client.chat.completions.create(
    messages=[
        # ... (system and user messages) ...
    ],
    model=model_name,
    stream=True,
    stream_options={'include_usage': True}
)
```

*   **Processing the Stream:**
    *   The `response` object is now an iterator.
    *   We loop through each `update` in the stream.
    *   Each `update` might contain a small piece of the response text (`delta.content`). We print these pieces immediately.
    *   If usage information is included, it appears in a final update.

```python
usage = None
for update in response:
    if update.choices and update.choices[0].delta:
        print(update.choices[0].delta.content or "", end="") # Print chunk without newline
    if update.usage:
        usage = update.usage

if usage:
    print("\n") # Add newline after full response
    for k, v in usage.model_dump().items():
        print(f"{k} = {v}")
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/01-basics
python streaming-output.py
```

You will see the reasons for exercising appear on the console incrementally, followed by the token usage statistics.

## 3. Tool Calling: Extending LLM Capabilities

**File:** [`src/01-basics/tool-calling.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/01-basics/tool-calling.py){target="_blank"}

LLMs are trained on vast datasets but lack real-time information and the ability to perform actions in the real world. Tool calling allows the LLM to request the execution of predefined functions (tools) to overcome these limitations.

**Concept:**

1.  **Define Tools:** You describe available functions (like getting the current time, searching the web, etc.) to the LLM, including their names, descriptions, and expected parameters.
2.  **LLM Request:** When the LLM determines it needs a tool to answer a user's query, it doesn't directly answer but instead outputs a special message indicating which tool to call and with what arguments.
3.  **Execute Tool:** Your code receives this request, executes the corresponding function with the provided arguments.
4.  **Provide Result:** You send the function's return value back to the LLM.
5.  **Final Response:** The LLM uses the tool's result to formulate the final answer to the user.

!!! success "Why Tool Calling is Powerful"
    Tool calling transforms LLMs from passive text generators into active agents capable of interacting with APIs, databases, or custom code, vastly expanding their potential applications.

**Code Breakdown:**

*   **Import additional libraries:** `json` for parsing arguments, `pytz` and `datetime` for the time function.
*   **Define the Tool Function:** A standard Python function (`get_current_time`) that takes a city name and returns the time. Note the docstring, which helps the LLM understand what the function does.

```python
import pytz
from datetime import datetime

def get_current_time(city_name: str) -> str:
    """Returns the current time in a given city."""
    # ... (implementation using pytz) ...
```

*   **Define the Tool Schema:** A dictionary describing the function to the LLM.
    *   `type`: Always "function".
    *   `function`: Contains details:
        *   `name`: Must match the Python function name.
        *   `description`: Crucial for the LLM to know *when* to use the tool.
        *   `parameters`: Describes the arguments (name, type, description, required).

```python
tool={
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": """Returns information about the current time...""",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city...",
                }
            },
            "required": ["city_name"],
        },
    },
}
```

!!! tip "Designing Good Tool Descriptions"
    The `description` field in the tool schema is critical. It should clearly and concisely explain what the tool does and when it should be used. Use natural language that the LLM can easily understand.

*   **Initial API Call with Tools:**
    *   The `tools` parameter is added to the `create` call, listing the available tools.

```python
response = client.chat.completions.create(
    messages=messages,
    tools=[tool], # Pass the tool definition
    model=model_name,
)
```

*   **Handling Tool Call Response:**
    *   Check if `finish_reason` is `tool_calls`.
    *   Append the model's request message to the history.
    *   Extract the `tool_call` information (ID, function name, arguments).
    *   Parse the JSON arguments.
    *   **Crucially, call the actual Python function (`locals()[tool_call.function.name](**function_args)`)**.
    *   Append the tool's result back to the message history, using the `tool_call_id` and `role: "tool"`.

```python
if response.choices[0].finish_reason == "tool_calls":
    messages.append(response.choices[0].message) # Append assistant's request
    tool_call = response.choices[0].message.tool_calls[0]
    if tool_call.type == "function":
        function_args = json.loads(tool_call.function.arguments)
        callable_func = locals()[tool_call.function.name]
        function_return = callable_func(**function_args)
        messages.append( # Append tool result
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": function_return,
            }
        )
```

*   **Second API Call:** Call the model *again* with the updated message history (including the tool result).

```python
response = client.chat.completions.create(
    messages=messages,
    tools=[tool],
    model=model_name,
)
print(f"Model response = {response.choices[0].message.content}")
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/01-basics
# Install pytz if you haven't: pip install pytz
python tool-calling.py
```

You will see output indicating the function call (`Calling function 'get_current_time'...`), the function's return value, and finally the model's response incorporating the time information.

---

## Hands-on Exercise Ideas (Module 1)

See the [Module 1 Exercises](./exercises.md) page for practical tasks.

---

!!! abstract "Further Reading & Resources"

    To deepen your understanding of basic LLM interaction and tool calling, explore these resources:

    *   **General LLM Interaction:**
        *   [The Beginner's Guide to Language Models with Python (Machine Learning Mastery)](https://machinelearningmastery.com/the-beginners-guide-to-language-models-with-python/){target="_blank"}
        *   [Using Large Language Models APIs with Python (Medium)](https://medium.com/@lokaregns/using-large-language-models-apis-with-python-a-comprehensive-guide-0020a51bf5b6){target="_blank"}
        *   [How to Build LLM Applications with LangChain Tutorial (DataCamp)](https://www.datacamp.com/tutorial/how-to-build-llm-applications-with-langchain){target="_blank"}
    *   **Tool Calling Specifics:**
        *   [LangChain Documentation: Tool calling concepts](https://python.langchain.com/docs/concepts/tool_calling/){target="_blank"}
        *   [LangChain Blog Post: Tool Calling with LangChain](https://blog.langchain.dev/tool-calling-with-langchain/){target="_blank"}
        *   [Analytics Vidhya Guide: Guide to Tool Calling in LLMs](https://www.analyticsvidhya.com/blog/2024/08/tool-calling-in-llms/){target="_blank"}
        *   [Medium Tutorial: Tool Calling for LLMs: A Detailed Tutorial](https://medium.com/@developer.yasir.pk/tool-calling-for-llms-a-detailed-tutorial-a2b4d78633e2){target="_blank"}
        *   [Apideck Introduction: An introduction to function calling and tool use](https://www.apideck.com/blog/llm-tool-use-and-function-calling){target="_blank"}
        *   [Mistral AI Docs: Function calling](https://docs.mistral.ai/capabilities/function_calling/){target="_blank"}
        *   [The Register Guide: A quick guide to tool-calling in large language models](https://www.theregister.com/2024/08/26/ai_llm_tool_calling/){target="_blank"}

---

This module covered the basics of interacting with LLMs and enabling them to use tools. In the next module, we'll explore how models can handle different types of input, specifically images and voice.

