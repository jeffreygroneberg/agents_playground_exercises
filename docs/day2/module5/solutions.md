# Day 2 - Module 5: Solutions

These are the solutions or discussion points for the exercises in Module 5.

## Solution 5.1: Triggering Multiple Tools

**Goal:** Observe the agent calling multiple tools in sequence.

**Modification (Example using LangChain - `react-agent-lc.py`):**

```python
# ... (imports, tool definitions, llm setup, prompt template remain the same) ...

if __name__ == "__main__":
    # --- Modified Input Query --- 
    input = "What is the weather like for Dennis right now?"
    # --------------------------

    tools = [get_current_username, get_current_location, get_current_time, get_weather] # Ensure get_weather is defined and included
    prompt = PromptTemplate.from_template(promptString)
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = agents.AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True, 
        max_iterations=5 # Increase max_iterations if needed
    )

    response = agent_executor.invoke({"input": input})
    print(response)
```
*(Note: You would need to define a `get_weather(location: str)` tool similar to the others for this specific query)*

**Expected Output (Conceptual - Verbose Log):**

```
> Entering new AgentExecutor chain...
Thought: I need to find the weather for Dennis. First, I need to know who Dennis is, but the tools suggest I can get the current username directly. Let me get the username.
Action: get_current_username
Action Input: {}
Observation: Dennis
Thought: Okay, the user is Dennis. Now I need Dennis's location to get the weather.
Action: get_current_location
Action Input: {"username": "Dennis"} 
Observation: Berlin
Thought: Dennis is in Berlin. Now I can get the weather for Berlin.
Action: get_weather
Action Input: {"location": "Berlin"}
Observation: The weather in Berlin is currently sunny with a temperature of 22°C.
Thought: I have the weather information for Dennis in Berlin. I can now provide the final answer.
Final Answer: The weather for Dennis in Berlin is currently sunny with a temperature of 22°C.

> Finished chain.
`The agent calls `get_current_username`, then `get_current_location`, then `get_weather` before giving the final answer.Solution 5.2: Adding a New Tool

**Goal:** Extend the agent with a calculator tool.

**Modification (Example using LlamaIndex - `react-agent-li.py`):**

```python
# ... (imports, other tool definitions, llm setup remain the same) ...

# --- Define New Tool Function --- 
def add_numbers(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    print(f"Tool: Adding {a} + {b}")
    return a + b
# -------------------------------

# --- Create FunctionTool for the new function --- 
add_tool = FunctionTool.from_defaults(fn=add_numbers)
# ------------------------------------------------

# --- Include the new tool in the list --- 
tools = [
    FunctionTool.from_defaults(fn=get_current_username),
    FunctionTool.from_defaults(fn=get_current_location),
    FunctionTool.from_defaults(fn=get_current_time),
    add_tool, # Add the new tool here
]
# ----------------------------------------

# ... (LLM setup, agent creation remain the same, ensure tools list is passed) ...

if __name__ == "__main__":
    # ... (agent setup) ...
    # --- Modified Input Query --- 
    response_gen = agent.stream_chat("What is 25 plus 17?")
    # --------------------------
    response_gen.print_response_stream()

```

**Expected Output (Conceptual - Stream):**

The output stream should show the agent reasoning:
*   Thought: The user wants to add 25 and 17. I have a tool called `add_numbers` that can do this.
*   Action: `add_numbers`
*   Action Input: `{"a": 25, "b": 17}`
*   (Console output will show: `Tool: Adding 25 + 17`)
*   Observation: `42`
*   Thought: The result of adding 25 and 17 is 42. I can now answer the user.
*   Final Answer: 25 plus 17 is 42.

## Solution 5.3 (Conceptual): Handling Tool Errors in ReAct

This is a discussion point.

1.  **Agent's Reaction to Error:** When a tool returns an error observation (e.g., "Error: Weather API unavailable" or "Error: Invalid location provided"), the agent's next "Thought" step should ideally:
    *   **Acknowledge the error:** Recognize that the previous action failed.
    *   **Analyze the error:** Understand *why* it failed, if possible (e.g., was it the tool itself, or the input provided?).
    *   **Re-plan:** Decide on the next best course of action. This could be:
        *   **Retry (Cautiously):** If the error is transient (like a temporary API glitch), it can try the same tool again.
        *   **Try Alternative:** If the error suggests bad input (e.g., invalid location), it can try to get the input again (e.g., ask the user for clarification or use `get_current_location` again).
        *   **Inform User:** If the tool is fundamentally broken or the required information cannot be obtained, the agent should inform the user about the failure (e.g., "I tried to get the weather, but the weather service is currently unavailable.").
        *   **Abandon Goal (Rare):** If the failed tool was critical and there's no alternative, it may have to report it cannot complete the task.
    *   **Avoid Guessing:** The agent should generally avoid making up information if a tool fails.

2.  **Influence of the Prompt:** The ReAct system prompt is crucial. If the prompt includes instructions on how to handle errors or failed actions (e.g., "If a tool returns an error, report the error to the user and stop" or "If a tool fails, try to find an alternative way to get the information"), the LLM will follow that guidance. The prompts in the examples do not explicitly detail error handling, relying on the LLM's general reasoning.

3.  **`handle_parsing_errors` in LangChain:** This option specifically deals with situations where the LLM's output (its Thought/Action/Action Input block) doesn't conform to the format the `AgentExecutor` expects. For example, if the LLM forgets to specify an action or formats the JSON input incorrectly. `handle_parsing_errors=True` allows the executor to send the malformed output back to the LLM as an "Observation" with instructions to correct the format. It does *not* directly handle errors that occur *during the execution of the tool itself* (like an API failure). Tool execution errors are typically caught by the code calling the tool, and the error message is returned as the "Observation" for the agent to reason about in the next step.
