# Day 2 - Module 5: Exercises

These exercises are based on the concepts and code presented in Module 5: Implementing Single Agents (ReAct Pattern) (`src/05-single-agent/`). Choose one of the framework examples (`react-agent-lc.py`, `react-agent-li.py`, or `reasoning-agent-sk.py`) to work with for exercises 5.1 and 5.2.

## Exercise 5.1: Triggering Multiple Tools

**Goal:** Modify the input query to require the agent to use a sequence of tools to find the answer.

1.  Choose one of the agent scripts (`react-agent-lc.py`, `react-agent-li.py`, or `reasoning-agent-sk.py`).
2.  Modify the initial user input/query. Instead of asking for the time, ask a question that requires chaining information from multiple tools. For example:
    *   "What is the weather like for Dennis right now?" (Requires `get_current_username` -> `get_current_location_of_user` -> `get_weather`)
    *   "What time is it where Dennis is located?" (Requires `get_current_username` -> `get_current_location_of_user` -> `get_current_time`)
3.  Run the chosen script.
4.  Observe the verbose output (enable `verbose=True` if needed in LangChain/LlamaIndex, or observe the sequence of calls in Semantic Kernel). Does the agent correctly identify the need for multiple tools? Does it call them in a logical order (e.g., get username first, then location, then weather/time)? Does it arrive at the correct final answer?

## Exercise 5.2: Adding a New Tool

**Goal:** Practice extending the agent's capabilities by adding a new tool.

1.  Choose one of the agent scripts.
2.  **Define a new tool function:** Add a simple Python function, for example, a basic calculator.
    ```python
    def add_numbers(a: int, b: int) -> int:
        \"\"\"Adds two integer numbers together.\"\"\"
        print(f"Tool: Adding {a} + {b}")
        return a + b
    ```
3.  **Integrate the tool:**
    *   **LangChain (`react-agent-lc.py`):** Add the `@tool` decorator above your `add_numbers` function and include the function object in the `tools` list passed to `create_react_agent`.
    *   **LlamaIndex (`react-agent-li.py`):** Create a `FunctionTool` from your function (`add_tool = FunctionTool.from_defaults(fn=add_numbers)`) and add `add_tool` to the `tools` list passed to `ReActAgent.from_tools`.
    *   **Semantic Kernel (`reasoning-agent-sk.py`):** Add the `add_numbers` function to the `ChefPlugin` class in `plugins.py` and decorate it with `@kernel_function`.
4.  **Modify the input query:** Change the user input to ask a question that requires the new tool, e.g., "What is 25 plus 17?".
5.  Run the chosen script.
6.  Observe the output. Does the agent recognize the need for the `add_numbers` tool? Does it call the tool with the correct arguments (25 and 17)? Does it provide the correct sum (42) in its final answer?

## Exercise 5.3 (Conceptual): Handling Tool Errors in ReAct

**Goal:** Think about how an agent reacts when a tool fails.

1.  Consider the ReAct loop: Thought -> Action -> Action Input -> Observation -> Thought...
2.  Imagine the `get_weather` tool fails (e.g., the API is down, invalid location provided) and returns an error message or raises an exception.
3.  What should the agent do in its next "Thought" step after receiving this error "Observation"?
    *   Should it try the same tool again?
    *   Should it try a different tool?
    *   Should it inform the user it cannot get the weather?
    *   Should it try to guess the weather?
4.  How does the specific prompt given to the ReAct agent (like the ones in `react-agent-lc.py` or `react-agent-li.py`) influence how it handles errors? Do the prompts explicitly mention error handling?
5.  How does the `handle_parsing_errors=True` option in LangChain's `AgentExecutor` relate to this? Does it handle *tool execution* errors or just errors in parsing the LLM's output?
