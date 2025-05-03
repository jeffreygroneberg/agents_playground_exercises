# Day 3 - Module 8: Society of Agents (AutoGen/MagenticOne)

**Objective:** Explore dynamic multi-agent conversations and collaboration patterns using frameworks like AutoGen, specifically the MagenticOne group chat implementation.

**Source Code:** [`src/08-society-of-agents/`](https://github.com/denniszielke/agentic-playground/tree/main/src/08-society-of-agents){target="_blank"}

---

## Introduction

While structured workflows like LangGraph (Module 7) provide explicit control, some scenarios benefit from more dynamic interactions where agents converse more freely, deciding who speaks next based on the conversation flow or an orchestrator. Frameworks like AutoGen (and its MagenticOne group chat implementation used here) excel at simulating these "societies" of agents.

**Key Concepts (AutoGen/MagenticOne):**

*   **Agents (`AssistantAgent`):** Define individual agents with specific roles, instructions (system messages), and tools.
*   **Group Chat (`MagenticOneGroupChat`):** Manages the conversation between multiple agents.
    *   **Orchestrator:** MagenticOne uses an underlying LLM (often a powerful reasoning model like `o1-mini` or `gpt-4o`) as an orchestrator. This orchestrator analyzes the conversation history and the agents' capabilities (descriptions, tools) to decide which agent should speak next to best advance the task.
    *   **Dynamic Turns:** Unlike predefined sequences or simple round-robin, the orchestrator dynamically selects the next speaker.
*   **Task Execution:** The group chat is initiated with a task, and the agents collaborate through conversation, managed by the orchestrator, until a termination condition is met.
*   **Termination:** Conditions like `MaxMessageTermination` (limit number of messages) or `TextMentionTermination` (stop when a specific keyword like "TERMINATE" is mentioned) are used to end the chat.

!!! info "AutoGen & MagenticOne"
    AutoGen is a framework for building multi-agent applications. MagenticOne is a specific group chat implementation within or compatible with AutoGen, leveraging an LLM orchestrator for dynamic turn-taking based on agent descriptions and conversation context.

This module explores variations of MagenticOne group chats:

1.  **Simple Group:** Multiple specialized agents collaborating on a task.
2.  **Chef Group:** A more complex scenario involving agents with overlapping and dependent knowledge (user info, location, time, ingredients, allergies) to recommend a meal.
3.  **Group with Reasoning Oversight:** Adding a dedicated reasoning agent (`o1-mini`) to monitor and provide feedback on the group chat quality.

## 1. Simple Group Chat

**File:** [`src/08-society-of-agents/simple-group.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/08-society-of-agents/simple-group.py){target="_blank"}

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
    *   Uses an underlying `model_client` (for the orchestrator LLM).
    *   Sets a `termination_condition` (`MaxMessageTermination(5)`).
*   **Run Chat:** `magenticteam.run_stream(task="what time is it here?.")` starts the chat with the initial task.
*   **Display Output:** `Console(stream)` prints the conversation flow to the console.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/08-society-of-agents
# Ensure autogen-agentchat, autogen-ext, pytz are installed
python simple-group.py
```

Observe the console output. You will see the agents conversing, involving the `users_agent`, `location_agent`, and `time_agent` being called upon by the orchestrator to gather the necessary information before the `summary_agent` provides the final answer or the chat hits the message limit.

## 2. Chef Recommendation Group Chat

**File:** [`src/08-society-of-agents/chef-and-group.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/08-society-of-agents/chef-and-group.py){target="_blank"}

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

**File:** [`src/08-society-of-agents/o1-with-chef-group.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/08-society-of-agents/o1-with-chef-group.py){target="_blank"}

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

Observe the flow. The MagenticOne orchestrator dynamically decides to call the `consultation_agent` at certain points. When called, the `consultation_agent` uses its `check_conversation` tool, which in turn invokes the powerful `o1-mini` `reasoning_agent` to analyze the chat history and provide feedback. This demonstrates a hierarchical pattern where one agent leverages another, more capable agent for specific complex tasks like quality control.

!!! success "Hierarchical Agent Structures"
    Integrating a powerful reasoning agent as a consultant or reviewer within a group of specialized agents is a common and effective pattern. It allows the specialized agents to handle routine tasks while the reasoning agent provides higher-level oversight, analysis, or complex decision-making.

---

## Hands-on Exercise Ideas (Module 8)

See the [Module 8 Exercises](./exercises.md) page for practical tasks.

---

!!! abstract "Further Reading & Resources (Society of Agents / AutoGen)"

    Delve deeper into AutoGen and dynamic multi-agent systems:

    *   **AutoGen Documentation:**
        *   [Microsoft AutoGen Homepage](https://microsoft.github.io/autogen/){target="_blank"}
        *   [AutoGen Concepts: Agents](https://microsoft.github.io/autogen/docs/concepts/agent-concepts/){target="_blank"}
        *   [AutoGen Concepts: Group Chat](https://microsoft.github.io/autogen/docs/concepts/groupchat-and-routing/){target="_blank"}
    *   **Tutorials & Examples:**
        *   [AutoGen Tutorial: Automated Task Solving with Code Generation, Execution & Debugging](https://microsoft.github.io/autogen/docs/tutorial/task-solving-agents/){target="_blank"}
        *   [AutoGen Tutorial: Group Chat](https://microsoft.github.io/autogen/docs/tutorial/groupchat/){target="_blank"}
        *   [AutoGen Cookbook](https://microsoft.github.io/autogen/docs/Examples/){target="_blank"} (Various examples)
        *   [Building Multi-Agent Systems with AutoGen (YouTube - James Briggs)](https://www.youtube.com/watch?v=h_Ky0qLq7yM){target="_blank"}
    *   **Related Concepts:**
        *   [AgentLite: Enabling Efficient Agent Interaction via Lite LLM](https://blog.llamaindex.ai/agentlite-enabling-efficient-agent-interaction-via-lite-llm-1d4d254a87c5){target="_blank"} (Discusses efficient orchestration)

---

This concludes the core modules of the workshop, covering the journey from basic LLM interaction to complex, collaborative multi-agent systems. Remember to explore the exercises for each module to solidify your understanding.

