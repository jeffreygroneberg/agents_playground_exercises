# Day 1 - Module 1: Solutions

These are the solutions for the exercises in Module 1.

## Solution 1.1: Changing Language and Persona

Modify [`src/01-basics/hello-world.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/01-basics/hello-world.py){target="_blank"}:

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

# Modified messages
messages=[
    {
        "role": "system",
        # Changed system message to request pirate persona
        "content": "Answer everything like a pirate.", 
    },
    {
        "role": "user",
        # Changed user question
        "content": "What is the weather like today?", 
    }
]

response = client.chat.completions.create(
    messages=messages,
    model="gpt-4o-mini",
    temperature=1,
    max_tokens=4096,
    top_p=1
)

print(response.choices[0].message.content)

```

**Expected Output:** The model should respond to the weather question with pirate-like language (e.g., "Ahoy! The weather be..." etc.).

## Solution 1.2: Using the Time Tool for a Different City

Modify [`src/01-basics/tool-calling.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/01-basics/tool-calling.py){target="_blank"}:

```python
# ... (imports and function definitions remain the same) ...

# Initial user message asking for time in Tokyo
messages=[
    {
        "role": "user",
        "content": "What time is it in Tokyo?", # Changed city
    }
]

# ... (rest of the script remains the same) ...
```

**Expected Output:**
*   The script should print `Calling function 'get_current_time' with city_name='Asia/Tokyo'` (or similar valid timezone).
*   It should print the actual current time in Tokyo.
*   The final model response should incorporate the time in Tokyo (e.g., "The current time in Tokyo is [time].").

## Solution 1.3 (Advanced): Adding a Simple Calculator Tool

Modify [`src/01-basics/tool-calling.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/01-basics/tool-calling.py){target="_blank"}:

```python
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import pytz
from datetime import datetime

load_dotenv()

# --- Add the new function --- 
def add_numbers(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    print(f"Calling function 'add_numbers' with {a} and {b}")
    return a + b
# ---------------------------

def get_current_time(city_name: str) -> str:
    """Returns the current time in a given city."""
    # ... (implementation remains the same)
    try:
        print(f"Calling function 'get_current_time' with city_name='{city_name}'")
        timezone = pytz.timezone(city_name)
        now = datetime.now(timezone)
        current_time = now.strftime("%I:%M:%S %p")
        return current_time
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't find the timezone for that location."

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

model_name = "gpt-4o-mini"

# --- Define the schema for the new tool --- 
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
# -----------------------------------------

tool={
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": """Returns information about the current time in a given city. Use pytz timezone names like Europe/Berlin or Asia/Tokyo.""",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city in pytz timezone format, e.g. Europe/Berlin",
                }
            },
            "required": ["city_name"],
        },
    },
}

# --- Update the user query --- 
messages=[
    {
        "role": "user",
        "content": "What is 123 plus 456?", 
    }
]
# ---------------------------

# --- Update the tools list in BOTH API calls --- 
response = client.chat.completions.create(
    messages=messages,
    tools=[tool, add_tool], # Include both tools
    model=model_name,
)

if response.choices[0].finish_reason == "tool_calls":
    messages.append(response.choices[0].message)
    tool_call = response.choices[0].message.tool_calls[0]
    if tool_call.type == "function":
        function_args = json.loads(tool_call.function.arguments)
        # Ensure locals() can find the function
        if tool_call.function.name in locals():
            callable_func = locals()[tool_call.function.name]
            function_return = callable_func(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": str(function_return), # Ensure content is string
                }
            )
        else:
             print(f"Error: Function {tool_call.function.name} not found.")
             messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": f"Error: Function {tool_call.function.name} not found.",
                }
            )

    # --- Make sure the updated tools list is used here too --- 
    response = client.chat.completions.create(
        messages=messages,
        tools=[tool, add_tool], # Include both tools
        model=model_name,
    )

print(f"Model response = {response.choices[0].message.content}")
# -------------------------------------------------------

```

**Expected Output:**
*   The script should print `Calling function 'add_numbers' with 123 and 456`.
*   The final model response should be something like "123 plus 456 is 579.".

