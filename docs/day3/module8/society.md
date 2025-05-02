# Day 3 - Module 8: Society of Agents (AutoGen/MagenticOne)

**Objective:** Explore dynamic multi-agent conversations and collaboration patterns using frameworks like AutoGen, specifically the MagenticOne group chat implementation.

**Source Code:** `/home/ubuntu/agentic-playground/src/08-society-of-agents/`

---

## Introduction

While structured workflows like LangGraph (Module 7) provide explicit control, some scenarios benefit from more dynamic interactions where agents converse more freely, deciding who speaks next based on the conversation flow or an orchestrator. Frameworks like AutoGen (and its MagenticOne group chat implementation used here) excel at simulating these "societies" of agents.

**Key Concepts (AutoGen/MagenticOne):**

*   **Agents (`AssistantAgent`):** Define individual agents with specific roles, instructions (system messages), and potentially tools.
*   **Group Chat (`MagenticOneGroupChat`):** Manages the conversation between multiple agents.
    *   **Orchestrator:** MagenticOne uses an underlying LLM (often a powerful reasoning model like `o1-mini` or `gpt-4o`) as an orchestrator. This orchestrator analyzes the conversation history and the agents' capabilities (descriptions, tools) to decide which agent should speak next to best advance the task.
    *   **Dynamic Turns:** Unlike predefined sequences or simple round-robin, the orchestrator dynamically selects the next speaker.
*   **Task Execution:** The group chat is initiated with a task, and the agents collaborate through conversation, managed by the orchestrator, until a termination condition is met.
*   **Termination:** Conditions like `MaxMessageTermination` (limit number of messages) or `TextMentionTermination` (stop when a specific keyword like "TERMINATE" is mentioned) are used to end the chat.

This module explores variations of MagenticOne group chats:

1.  **Simple Group:** Multiple specialized agents collaborating on a task.
2.  **Chef Group:** A more complex scenario involving agents with overlapping and dependent knowledge (user info, location, time, ingredients, allergies) to recommend a meal.
3.  **Group with Reasoning Oversight:** Adding a dedicated reasoning agent (`o1-mini`) to monitor and provide feedback on the group chat quality.

## 1. Simple Group Chat

**File:** `src/08-society-of-agents/simple-group.py`

This script sets up a basic MagenticOne group chat with agents specialized in getting user information, location, and time.

**Code Breakdown:**

*   **Import Libraries:** `autogen_agentchat`, `autogen_ext`, `asyncio`.
*   **Initialize Model Client:** `OpenAIChatCompletionClient` for the agents (using `gpt-4o` in this example).
*   **Define Tools:** Standard Python functions for `get_current_username`, `get_current_location_of_user`, `get_current_time`.
*   **Define Agents:** Multiple `AssistantAgent` instances:
    *   `users_agent`: Knows username, has `get_current_username` tool.
    *   `location_agent`: Knows location, has `get_current_location_of_user` tool.
    *   `time_agent`: Knows time, has `get_current_time` tool.
    *   `summary_agent`: Tasked with summarizing and concluding, instructed to use other agents and respond with "TERMINATE" when done.
    *   Each agent has a `description` which is crucial for the MagenticOne orchestrator to understand its capabilities.
*   **Create Group Chat:** `MagenticOneGroupChat(...)`:
    *   Takes the list of participating agents.
    *   Uses an underlying `model_client` (likely for the orchestrator LLM).
    *   Sets a `termination_condition` (`MaxMessageTermination(5)`).
*   **Run Chat:** `magenticteam.run_stream(task="what time is it here?.")` starts the chat with the initial task.
*   **Display Output:** `Console(stream)` prints the conversation flow to the console.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/08-society-of-agents
# Ensure autogen-agentchat, autogen-ext, pytz are installed
python simple-group.py
```

Observe the console output. You will see the agents conversing, likely involving the `users_agent`, `location_agent`, and `time_agent` being called upon by the orchestrator to gather the necessary information before the `summary_agent` potentially provides the final answer or the chat hits the message limit.

## 2. Chef Recommendation Group Chat

**File:** `src/08-society-of-agents/chef-and-group.py`

This example presents a more complex scenario where agents need to collaborate to recommend a meal, considering user details, location, time, ingredients, and allergies.

**Code Breakdown:**

*   **Similar Setup:** Imports, model client, tools (adds `get_medical_history`, `get_available_incredients`).
*   **Agents:**
    *   `users_agent`: Now also has `get_medical_history` tool.
    *   `location_agent`, `time_agent`: Similar to the simple group.
    *   `chef_agent`: Specialized in recommending dishes, has `get_available_incredients` tool, and importantly, its system message instructs it to ask about allergies if unknown.
    *   `summary_agent`: Similar role.
*   **Group Chat:** `MagenticOneGroupChat` includes the `chef_agent` in the list.
*   **Task:** `task="I want to have something to eat. What would you recommend?."`

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/08-society-of-agents
python chef-and-group.py
```

Observe the conversation. The orchestrator should guide the agents to gather necessary context: `users_agent` for username and allergies, `location_agent` for location, `time_agent` for time, and `chef_agent` for ingredients. The `chef_agent` should ideally ask about allergies if the `users_agent` didn't provide them, demonstrating rule-following and dynamic interaction based on missing information.

## 3. Group Chat with Reasoning Oversight (o1-mini)

**File:** `src/08-society-of-agents/o1-with-chef-group.py`

This script enhances the chef scenario by adding a dedicated, powerful reasoning agent (`o1-mini`) to act as a consultant or quality checker for the main group chat.

**Code Breakdown:**

*   **Multiple Model Clients:** Initializes clients for both `gpt-4o-mini` (for regular agents) and `o1-mini` (for the reasoning agent).
*   **Reasoning Agent (`reasoning_agent`):** An `AssistantAgent` configured to use the `o1_model_client`.
*   **Consultation Tool (`check_conversation`):** An async function defined as a tool. When called, it invokes the `reasoning_agent` with the current conversation messages, asking it to check for inconsistencies or open questions.
*   **Consultation Agent (`consultation_agent`):** A regular `AssistantAgent` (using `gpt-4o-mini`) whose *only* tool is `check_conversation`. Its system message tasks it with checking conversation quality.
*   **Agents:** The list of agents for the `MagenticOneGroupChat` now includes the `consultation_agent` along with the others (user, location, time, chef).
*   **Group Chat & Task:** Similar setup to `chef-and-group.py`.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/08-society-of-agents
# Ensure necessary autogen libraries are installed
python o1-with-chef-group.py
```

Observe the flow. The MagenticOne orchestrator might dynamically decide to call the `consultation_agent` at certain points. When called, the `consultation_agent` uses its `check_conversation` tool, which in turn invokes the powerful `o1-mini` `reasoning_agent` to analyze the chat history and provide feedback. This demonstrates a hierarchical pattern where one agent leverages another, more capable agent for specific complex tasks like quality control.

---

## Hands-on Exercise Ideas (Module 8)

1.  **Modify `simple-group.py`:**
    *   Change the initial `task` to something requiring different information (e.g., "Where does Dennis live?").
    *   Add a new `AssistantAgent` with a simple tool (e.g., a weather agent using the `get_weather` tool) and add it to the `MagenticOneGroupChat`. Change the task to include asking about the weather.
2.  **Modify `chef-and-group.py`:**
    *   Change the `get_medical_history` tool function to return *no* allergies for Dennis. Observe if the `chef_agent` correctly asks about allergies before making a recommendation.
    *   Change the available ingredients returned by `get_available_incredients`.
3.  **Modify `o1-with-chef-group.py`:** Change the prompt within the `check_conversation` tool to ask the `reasoning_agent` to check for something specific (e.g., "Ensure the chef confirmed allergies before recommending a dish.").

---

This module explored dynamic multi-agent conversations using AutoGen/MagenticOne, showcasing how specialized agents can collaborate under the guidance of an orchestrator, and how reasoning agents can be integrated for oversight. The final module will look at event-driven agent architectures.
