# Day 3 - Module 7: Multi-Agent Collaboration

**Objective:** Explore patterns and frameworks for building systems where multiple specialized agents collaborate to achieve a common goal.

**Source Code:** [`src/07-multi-agent-collaboration/`](https://github.com/denniszielke/agentic-playground/tree/main/src/07-multi-agent-collaboration){target="_blank"}

---

## Introduction

While single agents (Module 5) can handle complex tasks, breaking down problems and assigning specialized roles to different agents leads to more robust, maintainable, and scalable solutions. Multi-agent systems allow for:

*   **Specialization:** Each agent focuses on a specific task or expertise (e.g., coding, reviewing, planning, research).
*   **Modularity:** Easier to develop, test, and update individual agents.
*   **Complex Problem Decomposition:** Tackling problems too large or diverse for a single agent.

This module explores different approaches to multi-agent collaboration, contrasting a structured workflow using LangGraph with a more reasoning-focused approach.

1.  **Structured Collaboration (LangGraph):** Defining explicit roles and interaction patterns (e.g., a Coder agent and a Reviewer agent improving code iteratively).
2.  **Reasoning-Based Approach (AutoGen/MagenticOne):** Using a powerful reasoning model (like o1-mini) to handle tasks that would otherwise require multiple specialized agents.

!!! info "The Power of Collaboration"
    Just like human teams, multi-agent systems leverage diverse skills and parallel processing to solve problems more effectively than a single entity can. Designing the communication and workflow between agents is key.

## 1. Structured Collaboration: Coder & Reviewer (LangGraph)

**File:** [`src/07-multi-agent-collaboration/coding-agents.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/07-multi-agent-collaboration/coding-agents.py){target="_blank"}

This script implements a multi-agent system using LangGraph where two agents, a Coder and a Reviewer, collaborate to generate and refine code based on an initial objective.

**Concept:**

*   **Roles:**
    *   **Coder:** Writes or improves code based on an objective or feedback.
    *   **Reviewer:** Reviews the code provided by the Coder, checking for PEP8 compliance, bugs, and adherence to the objective, providing feedback.
*   **Workflow (Graph):** The interaction follows a defined cycle:
    1.  Initial code is generated (or provided).
    2.  Reviewer checks the code and provides feedback.
    3.  A decision node checks if the feedback indicates the code is satisfactory or if the iteration limit is reached.
    4.  If not satisfactory, the Coder receives the feedback and revises the code.
    5.  The revised code goes back to the Reviewer (Step 2).
    6.  If satisfactory, the process ends, followed by a final rating.
*   **LangGraph Implementation:**
    *   `StateGraph(GraphState)` defines the structure.
    *   `GraphState` holds shared information (objective, code, feedback, history, iterations, etc.).
    *   Nodes (`handle_reviewer`, `handle_coder`, `handle_result`) encapsulate the logic for each agent/step, interacting with an LLM.
    *   Conditional Edges (`workflow.add_conditional_edges`) implement the decision logic based on the reviewer's feedback (using an LLM call `classify_feedback` to interpret if the feedback is addressed).

**Code Breakdown:**

*   **Import Libraries:** `langgraph`, `langchain_openai`, `pydantic`, etc.
*   **Initialize LLM:** `ChatOpenAI` client.
*   **Define State (`GraphState`):** TypedDict holding all relevant information passed between nodes.
*   **Define Nodes:**
    *   `handle_reviewer`: Takes current code and specialization, calls LLM with reviewer instructions, returns feedback and increments iteration count.
    *   `handle_coder`: Takes current code, feedback, and specialization, calls LLM with coder instructions, returns improved code.
    *   `handle_result`: Called at the end. Calls LLM to rate the coder's skills based on the history and compares the final code with the initial code.
*   **Define Conditional Logic (`deployment_ready`):** A function that calls an LLM (`classify_feedback`) to determine if the reviewer's feedback has been addressed in the latest code. Also checks iteration count.
*   **Build Graph:**
    *   Adds nodes.
    *   Sets entry point (`handle_reviewer`).
    *   Adds edges (`handle_coder` -> `handle_reviewer`, `handle_result` -> END).
    *   Adds conditional edge from `handle_reviewer` based on `deployment_ready` function (either to `handle_coder` for more revisions or `handle_result` to finish).
*   **Compile & Invoke:** `workflow.compile()` creates the runnable graph. `app.invoke(...)` starts the process with the initial objective, code, and state.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/07-multi-agent-collaboration
# Ensure langgraph, langchain-openai are installed
python coding-agents.py
```

Observe the output. You'll see the Coder generating initial code, the Reviewer providing feedback, the Coder revising, and the cycle repeating until the `deployment_ready` condition is met (either feedback addressed or iteration limit exceeded), finally ending with the `handle_result` node.

!!! tip "LangGraph for Structured Workflows"
    LangGraph excels at defining explicit, complex workflows involving multiple agents or steps with clear transitions and conditional logic. It provides more control over the interaction pattern compared to more free-form agent frameworks.

## 2. Reasoning-Based Approach: Single Reasoning Coder (AutoGen/MagenticOne)

**File:** [`src/07-multi-agent-collaboration/reasoning-coder.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/07-multi-agent-collaboration/reasoning-coder.py){target="_blank"}

This script contrasts the multi-agent approach by using a single, powerful reasoning agent (specifically targeting `o1-mini` via `autogen-ext`) to handle the coding task directly.

**Concept:**

Instead of breaking the task into explicit Coder and Reviewer roles managed by a graph, this approach relies on the advanced reasoning capabilities of the `o1-mini` model to understand the request and generate the code in one go (or through internal reasoning steps not exposed externally in this simple script).

*   **Agent:** An `AssistantAgent` from `autogen_agentchat` is configured to use the `o1-mini` model via `OpenAIChatCompletionClient`.
*   **Direct Invocation:** The `generate_code` function directly invokes the `reasoning_agent` with the coding task.

**Code Breakdown:**

*   **Import Libraries:** `autogen_agentchat`, `autogen_core`, `autogen_ext`, `asyncio`.
*   **Initialize Model Client:** `OpenAIChatCompletionClient` configured for `o1-mini` at the GitHub Models endpoint.
*   **Define Reasoning Agent:** `AssistantAgent` named `reasoning_agent` using the `o1_model_client`.
*   **`generate_code` Function:** An async function that takes the task description and calls `reasoning_agent.on_messages(...)` to get the code.
*   **Main Execution:** Calls `generate_code` with the same query used in the LangGraph example and prints the result.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/07-multi-agent-collaboration
# Ensure autogen-agentchat, autogen-core, autogen-ext are installed
# Note: `autogen-ext` is used here; ensure it is installed correctly, either as a custom extension within this repository or via separate installation steps if required.
python reasoning-coder.py
```

Observe the output. It should directly print the generated code for the regression model task, produced by the single `o1-mini` agent.

!!! success "When to Use a Single Powerful Reasoner"
    If a single, highly capable LLM (like `o1-mini` or GPT-4) can reliably handle the entire task through its own reasoning, and explicit intermediate steps or checks aren't strictly necessary, this approach can be simpler to implement.

**Comparison:**

*   **LangGraph (Multi-Agent):**
    *   Pros: Explicit control over workflow, clear roles, better for complex processes requiring specific steps or checks, easier debugging of individual components.
    *   Cons: More setup required to define the graph, nodes, and transitions.
*   **AutoGen/o1-mini (Single Reasoning Agent):**
    *   Pros: Simpler setup for certain tasks, leverages the advanced reasoning of the model.
    *   Cons: Less explicit control over the process, relies heavily on the model's ability to understand and execute the task correctly, debugging can be harder as the reasoning is internal to the LLM.

The choice between these approaches depends on the complexity of the task, the need for explicit control and intermediate checks, and the capabilities of the underlying LLMs.

---

!!! abstract "Further Reading & Resources (Multi-Agent Collaboration)"

    Explore frameworks and concepts for building multi-agent systems:

    *   **Frameworks & Libraries:**
        *   [LangGraph Documentation: Multi-agent Collaboration](https://langchain-ai.github.io/langgraphjs/tutorials/multi_agent/multi_agent_collaboration/){target="_blank"}
        *   [crewAI Documentation](https://docs.crewai.com/){target="_blank"} (Popular framework for collaborative agents)
        *   [Microsoft AutoGen Documentation](https://microsoft.github.io/autogen/){target="_blank"} (Framework for multi-agent conversation)
        *   [Semantic Kernel Documentation: Agents](https://learn.microsoft.com/en-us/semantic-kernel/agents/){target="_blank"} (Includes concepts for agent collaboration)
    *   **Tutorials & Guides:**
        *   [How to Build the Ultimate AI Automation with Multi-Agent Collaboration (LangChain Blog)](https://blog.langchain.dev/how-to-build-the-ultimate-ai-automation-with-multi-agent-collaboration/){target="_blank"}
        *   [Building Multi AI Agent Systems: A Practical Guide! (LinkedIn)](https://www.linkedin.com/pulse/building-multi-ai-agentsystems-practical-guide-pavan-belagatti-fjarc){target="_blank"}
        *   [Step by Step guide to develop AI Multi-Agent system using Microsoft Semantic Kernel (Medium)](https://medium.com/@akshaykokane09/step-by-step-guide-to-develop-ai-multi-agent-system-using-microsoft-semantic-kernel-and-gpt-4o-f5991af40ea6){target="_blank"}
        *   [How to Build a Multi Agent AI System (YouTube - IBM)](https://www.youtube.com/watch?v=gUrENDkPw_k){target="_blank"}
        *   [Build a Multi-Agent System with CrewAI | Agentic AI Tutorial (YouTube)](https://www.youtube.com/watch?v=qsrl2DHYi1Y){target="_blank"}
    *   **Courses:**
        *   [Multi AI Agent Systems with crewAI (DeepLearning.AI)](https://learn.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai/){target="_blank"}

---

This module introduced multi-agent collaboration using structured workflows (LangGraph) and contrasted it with a single powerful reasoning agent. The next module will explore more dynamic multi-agent interactions and hierarchical structures using frameworks like AutoGen.

