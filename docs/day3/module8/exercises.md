# Day 3 - Module 8: Exercises

These exercises are based on the concepts and code presented in Module 8: Society of Agents (AutoGen/MagenticOne) (`src/08-society-of-agents/`).

## Exercise 8.1: Changing the Task (Simple Group)

**Goal:** Observe how the MagenticOne orchestrator directs different agents based on the initial task.

1.  Open the `src/08-society-of-agents/simple-group.py` script.
2.  Locate the line where the chat is initiated:
    ```python
    stream = magenticteam.run_stream(task="what time is it here?.")
    ```
3.  Change the initial `task` string to ask for different information that requires different agents. Examples:
    *   `task="Where does Dennis live?"` (Should primarily involve `users_agent` and `location_agent`)
    *   `task="Who is the current user?"` (Should primarily involve `users_agent`)
4.  Run the script (`python simple-group.py`).
5.  Observe the conversation flow printed to the console. Does the orchestrator correctly involve the agents relevant to the new task? Does the `summary_agent` still get involved appropriately?

## Exercise 8.2: Adding a Weather Agent (Simple Group)

**Goal:** Practice adding a new agent with a specific capability to the group chat.

1.  Open the `src/08-society-of-agents/simple-group.py` script.
2.  **Define a weather tool:** Add a `get_weather(location: str)` function (you can make it return a fixed string like "It is sunny in [location]" for simplicity).
3.  **Define a weather agent:** Create a new `AssistantAgent` named `weather_agent`.
    *   Give it a relevant `description` (e.g., "Knows the weather.").
    *   Provide it with the `get_weather` tool function.
    *   Use the same `model_client` as the other agents.
4.  **Add agent to group:** Include the `weather_agent` in the `agents` list passed to `MagenticOneGroupChat`.
5.  **Modify the task:** Change the initial `task` to include asking about the weather, e.g., `task="What is the weather like where Dennis lives?"`.
6.  Run the script (`python simple-group.py`).
7.  Observe the conversation. Does the orchestrator involve the new `weather_agent` after finding Dennis's location? Does the final summary include the weather information?

## Exercise 8.3: Testing Chef Agent Logic (Chef Group)

**Goal:** Verify if the chef agent correctly handles missing information (allergies) based on its instructions.

1.  Open the `src/08-society-of-agents/chef-and-group.py` script.
2.  Locate the `get_medical_history` tool function.
3.  Modify the function to return an empty string or a message indicating no known allergies:
    ```python
    def get_medical_history(username: str) -> str:
        """Returns the medical history for a given username."""
        if username == "Dennis":
            # return "Dennis is allergic to peanuts."
            return "No known allergies for Dennis."
        else:
            return "Unknown user."
    ```
4.  Run the script (`python chef-and-group.py`) with the task "I want to have something to eat. What would you recommend?."
5.  Carefully read the conversation flow. Does the `chef_agent`, after finding out there are no known allergies from the `users_agent`, explicitly ask something like "Do you have any allergies I should be aware of?" before recommending a dish? (This depends on its system prompt instructions being followed correctly by the LLM).

## Exercise 8.4: Adding Constraints and preferences into a planning agent
**Goal:** Understand how a group of agents can collaborate without a moderator. Learn how context agents (location, user preferences) feed into a planning agent (chef). Work with a real agent configuration and extend it with constraints. 

1. **Add Domain Expertise (10–15 min):**

   * Add a new agent: `nutritionist_agent`.

     * Role: Evaluate the nutritional quality of the suggested meal.
   * Provide it a tool: `analyze_nutrition(meal: str)` — mock this as a function returning “balanced”, “high-fat”, etc.

2. **Inject a Constraint (5 min):**

   * Modify `users_agent` to include a dietary preference, e.g., `"low-carb"` or `"vegan"`.
   * Ensure the `chef_agent` respects this constraint when generating meal options.

3. **Optional Extensions:**

   * Add a `budget_agent` with a `get_cost_estimate(meal)` tool.
   * Let agents negotiate (by reasoning in messages) over trade-offs between cost and nutrition.



## Exercise 8.5: Modifying Reasoning Oversight (o1 Group)

**Goal:** Change the focus of the quality check performed by the reasoning agent.

1.  Open the `src/08-society-of-agents/o1-with-chef-group.py` script.
2.  Locate the `check_conversation` async function (which acts as a tool for the `consultation_agent`).
3.  Find the prompt string passed to `reasoning_agent.on_messages` inside this function:
    ```python
    prompt = "Check the messages for inconsistencies or open questions..."
    ```
4.  Modify this `prompt` to ask the `reasoning_agent` (o1-mini) to check for something specific. Examples:
    *   `prompt = "Review the conversation. Did the chef confirm the user's allergies before recommending a meal? Answer yes or no and explain briefly."`
    *   `prompt = "Analyze the conversation. Was the final meal recommendation appropriate given the available ingredients mentioned earlier?"`
5.  Run the script (`python o1-with-chef-group.py`).
6.  Observe the output from the `consultation_agent` (which includes the response from the `reasoning_agent`). Does the feedback now focus specifically on the new check you asked the `reasoning_agent` to perform?
