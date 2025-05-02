# Day 3 - Module 8: Solutions

These are the solutions or discussion points for the exercises in Module 8.

## Solution 8.1: Changing the Task (Simple Group)

Modify `src/08-society-of-agents/simple-group.py`:

```python
# ... (imports, model client, tools, agents definition remain the same) ...

if __name__ == "__main__":
    # ... (group chat setup) ...

    # --- Modified Task --- 
    task = "Where does Dennis live?"
    # -------------------
    
    stream = magenticteam.run_stream(task=task)
    console = Console()
    console.print(stream)
```

**Expected Output:**
The conversation flow should primarily involve the `users_agent` (to confirm the user is Dennis) and the `location_agent` (to get the location for Dennis). The `time_agent` should not be involved. The `summary_agent` might be called at the end to state the final answer (e.g., "Dennis lives in Berlin.") before terminating.

## Solution 8.2: Adding a Weather Agent (Simple Group)

Modify `src/08-society-of-agents/simple-group.py`:

```python
# ... (imports, model client, other tools definitions remain the same) ...

# --- Define New Weather Tool --- 
def get_weather(location: str) -> str:
    """Returns the current weather for a given location."""
    print(f"Tool: Getting weather for {location}")
    # Simple mock response
    return f"It is currently sunny in {location}."
# -----------------------------

# ... (definitions for users_agent, location_agent, time_agent, summary_agent) ...

# --- Define New Weather Agent --- 
weather_agent = AssistantAgent(
    name="WeatherAgent",
    description="Knows the weather.",
    system_message="You provide weather information.",
    model_client=model_client,
    registered_tools=[get_weather]
)
# ------------------------------

if __name__ == "__main__":
    # --- Add weather_agent to the list --- 
    agents = [users_agent, location_agent, time_agent, summary_agent, weather_agent]
    # -------------------------------------
    
    magenticteam = MagenticOneGroupChat(
        agents=agents,
        model_client=model_client, # Orchestrator model
        termination_condition=MaxMessageTermination(10) # Increased limit for more steps
    )

    # --- Modified Task --- 
    task = "What is the weather like where Dennis lives?"
    # -------------------

    stream = magenticteam.run_stream(task=task)
    console = Console()
    console.print(stream)
```

**Expected Output:**
The conversation should involve:
1.  `users_agent` (confirming user is Dennis).
2.  `location_agent` (getting Dennis's location, e.g., Berlin).
3.  `weather_agent` (being called with the location "Berlin" to get the weather).
4.  `summary_agent` (providing the final answer, e.g., "The weather where Dennis lives (Berlin) is currently sunny.") before terminating.

## Solution 8.3: Testing Chef Agent Logic (Chef Group)

Modify `src/08-society-of-agents/chef-and-group.py`:

```python
# ... (imports, model client, other tools definitions remain the same) ...

# --- Modified Medical History Tool --- 
def get_medical_history(username: str) -> str:
    """Returns the medical history for a given username."""
    if username == "Dennis":
        # return "Dennis is allergic to peanuts."
        return "No known allergies for Dennis."
    else:
        return "Unknown user."
# -----------------------------------

# ... (agent definitions, group chat setup, task remain the same) ...
```

**Expected Output:**
When the conversation reaches the `chef_agent`, having already learned the username is Dennis but that there are "No known allergies", the `chef_agent` *should* ask a clarifying question based on its system prompt (which likely includes instructions like "If allergies are unknown, ask the user"). The output should show the `chef_agent` asking something like:

```
ChefAgent: Okay Dennis, I see no known allergies on file. To make sure I recommend something safe, do you have any food allergies or dietary restrictions I should be aware of?
```
This demonstrates the agent following its instructions to proactively seek missing critical information.

## Solution 8.4: Modifying Reasoning Oversight (o1 Group)

Modify `src/08-society-of-agents/o1-with-chef-group.py`:

```python
# ... (imports, model clients, tools, agent definitions remain the same) ...

# Tool for consultation agent to check conversation quality
async def check_conversation(messages: list[dict[str, str]]) -> str:
    """Checks the conversation for inconsistencies or open questions."""
    # --- Modified Prompt for Reasoning Agent --- 
    prompt = "Review the conversation. Did the chef confirm the user's allergies before recommending a meal? Answer yes or no and explain briefly."
    # -----------------------------------------
    response = await reasoning_agent.on_messages(messages=[ChatMessage(role="user", content=prompt)])
    return response[0].content

# ... (consultation_agent definition using check_conversation tool) ...
# ... (group chat setup, task, main execution remain the same) ...
```

**Expected Output:**
When the `consultation_agent` is invoked by the orchestrator, its output (which comes from the `reasoning_agent` via the `check_conversation` tool) should now specifically address whether the chef confirmed allergies. For example:

*   If the chef *did* ask: `ConsultationAgent: Yes, the chef asked about allergies after learning none were on file before proceeding with the recommendation.`
*   If the chef *did not* ask (perhaps due to an LLM error or prompt issue): `ConsultationAgent: No, the chef did not explicitly confirm allergies with the user before making a recommendation, even though the initial medical history check showed no known allergies.`

This demonstrates tailoring the oversight provided by the reasoning agent to focus on specific quality aspects of the multi-agent interaction.
