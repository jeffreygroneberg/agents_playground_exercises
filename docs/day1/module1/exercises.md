# Day 1 - Module 1: Exercises

These exercises are based on the concepts and code presented in Module 1: Basic LLM Interaction & Tool Calling (`src/01-basics/`).

## Exercise 1.1: Changing Language and Persona

**Goal:** Practice modifying the system prompt to change the LLM's behavior.

1.  Open the `src/01-basics/hello-world.py` script.
2.  Modify the `system` message content from "antworte alles in französisch" to instruct the model to respond like a pirate (e.g., "Answer everything like a pirate.").
3.  Modify the `user` message content to ask a different question (e.g., "What is the weather like today?").
4.  Run the script (`python hello-world.py`) and observe the pirate-themed response.

## Exercise 1.2: Using the Time Tool for a Different City

**Goal:** Practice changing the user input to trigger a tool call with different arguments.

1.  Open the `src/01-basics/tool-calling.py` script.
2.  Locate the initial `user` message:
    ```python
    messages=[
        {
            "role": "user",
            "content": "What time is it in my current location?",
        }
    ]
    ```
3.  Change the `content` to ask for the time in a specific city, for example, Tokyo: "What time is it in Tokyo?".
4.  Run the script (`python tool-calling.py`).
5.  Observe the output. Does the `get_current_time` function get called with `Asia/Tokyo` (or a similar valid timezone identifier derived by the LLM)? Does the final model response include the correct time for Tokyo?

## Exercise 1.3 (Advanced): Adding a Simple Calculator Tool

**Goal:** Practice defining and integrating a new tool for the LLM to use.

1.  Open the `src/01-basics/tool-calling.py` script.
2.  **Define a new Python function:** Add a function that performs simple addition.
    ```python
    def add_numbers(a: int, b: int) -> int:
        \"\"\"Adds two integer numbers together.\"\"\"
        print(f"Calling function 'add_numbers' with {a} and {b}")
        return a + b
    ```
3.  **Define the tool schema:** Create a new dictionary describing the `add_numbers` function to the LLM, similar to the `get_current_time` schema.
    ```python
    add_tool = {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Adds two integer numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "integer",
                        "description": "The second number.",
                    }
                },
                "required": ["a", "b"],
            },
        },
    }
    ```
4.  **Update the API calls:**
    *   Modify the `tools` list passed to `client.chat.completions.create` to include *both* the original time tool (`tool`) and the new `add_tool`:
        ```python
        tools=[tool, add_tool]
        ```
    *   Ensure this updated `tools` list is used in *both* the initial API call and the second call made after handling a potential tool invocation.
5.  **Update the user query:** Change the initial `user` message to ask an addition question, e.g., "What is 123 plus 456?".
6.  **Run the script:** `python tool-calling.py`.
7.  Observe the output. Does the LLM correctly identify the need for the `add_numbers` tool? Is the function called with the correct arguments? Does the final response contain the sum?
