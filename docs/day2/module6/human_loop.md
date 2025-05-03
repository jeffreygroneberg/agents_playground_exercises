# Day 2 - Module 6: Human-in-the-Loop Patterns

**Objective:** Understand why and how to incorporate human oversight, feedback, and intervention into agent workflows.

**Source Code:** [`src/06-human-in-the-loop/`](https://github.com/denniszielke/agentic-playground/tree/main/src/06-human-in-the-loop){target="_blank"}

---

## Introduction

While the goal is often to create fully autonomous agents, there are many scenarios where human involvement is crucial or desirable:

*   **Safety and Control:** Preventing agents from taking harmful or unintended actions, especially in high-stakes environments.
*   **Quality Assurance:** Reviewing or correcting agent outputs before they are finalized or used in downstream processes.
*   **Guidance and Decision Making:** Providing input when the agent faces ambiguity, requires subjective judgment, or needs to choose between multiple valid options.
*   **Learning and Improvement:** Using human feedback to fine-tune agent behavior, improve prompts, or identify areas for model retraining.

This module explores patterns for integrating humans into the agent execution loop, focusing on:

1.  **Interruptible Workflows (LangGraph):** Pausing agent execution at specific points to wait for human input before proceeding.
2.  **Collaborative Review Loops (Semantic Kernel):** Designing multi-agent systems where one agent's output is reviewed (potentially by a human or another agent acting as a proxy) before further action.

!!! info "Why Human-in-the-Loop (HIL)?"
    HIL combines the strengths of AI (speed, scale, data processing) with human capabilities (judgment, common sense, ethical reasoning, handling ambiguity). It's essential for building trustworthy, reliable, and effective AI systems in many real-world applications.

## 1. Interruptible Workflows with LangGraph

**File:** [`src/06-human-in-the-loop/interrupt.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/06-human-in-the-loop/interrupt.py){target="_blank"}

LangGraph is a library (often used with LangChain) for building stateful, multi-actor applications, including agentic workflows, as graphs. It explicitly supports interrupting the graph execution to wait for external input.

**Concept:**

*   **State Graph:** The workflow is defined as a graph where nodes represent processing steps (functions) and edges represent transitions based on the current state.
*   **State:** A shared dictionary (`State` TypedDict) holds data passed between nodes.
*   **Nodes:** Asynchronous functions that take the current state and return updates to the state.
*   **Interrupt:** A special function `interrupt()` can be called within a node. This pauses the graph execution and signals that human input is needed.
*   **Checkpointer:** Required for interrupts. It saves the graph's state when interrupted, allowing it to be resumed later (`MemorySaver` used here for in-memory checkpointing).
*   **Resuming:** The graph is resumed by sending a special `Command(resume=...)` object containing the human input.

**Code Breakdown:**

*   **Import Libraries:** `langgraph`, `asyncio`, `uuid`.
*   **Define State:** `State` TypedDict with `input`, `ai_answer`, `human_answer` fields.
*   **Define Nodes:** `node1`, `node2`, `node3` are simple async functions simulating work.
    *   `node2` calls `interrupt({"ai_answer": "What is your age?"})`. This pauses the graph and makes the dictionary available to the client waiting for the interrupt.
    *   The value returned by `interrupt()` is the input provided when resuming.
*   **Build Graph:**
    *   `StateGraph(State)` initializes the graph builder.
    *   `builder.add_node(...)` adds the nodes.
    *   `builder.add_edge(...)` defines the fixed sequence: START -> node1 -> node2 -> node3 -> END.
*   **Compile Graph:** `builder.compile(checkpointer=MemorySaver())` creates the runnable graph, enabling checkpointing.
*   **Run Graph (`run_graph` function):**
    1.  Creates a unique `thread_id` for the conversation state.
    2.  Starts the graph execution using `graph.astream(...)` with an initial input.
    3.  Iterates through the output chunks until the graph interrupts (implicitly, when `node2` calls `interrupt`).
    4.  Prompts the user for input (`resume=input(...)`).
    5.  Creates a `Command(resume=...)` object with the user's input.
    6.  Resumes the graph execution by sending the `Command` via `graph.astream(command, config)`.
    7.  Continues iterating through chunks until the graph reaches the END.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/06-human-in-the-loop
# Ensure langgraph is installed: pip install langgraph
python interrupt.py
```

Observe the output. The program will print the progress through `node1`, then pause after `node2` prints its message and asks for the interrupt command (your age). Enter an age. The graph will resume, `node2` will receive the age, `node3` will execute, and the graph will finish.

!!! tip "Key LangGraph Concepts for HIL"
    *   **Graphs:** Define the workflow structure.
    *   **`interrupt()`:** The core function to pause for human input.
    *   **Checkpointer:** Essential for saving and resuming state across interruptions.
    *   **`Command(resume=...)`:** The mechanism to inject human input and continue the flow.

## 2. Collaborative Review Loops (Semantic Kernel AgentGroupChat)

**File:** [`src/06-human-in-the-loop/report-agents.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/06-human-in-the-loop/report-agents.py){target="_blank"}

This example uses Semantic Kernel's `AgentGroupChat` to simulate a scenario where a "Writer" agent drafts content, and a "Reviewer" agent provides feedback. The loop continues until the Reviewer deems the content satisfactory. While the Reviewer is an AI agent here, it simulates the role a human might play in a review process.

**Concept (Semantic Kernel AgentGroupChat):**

*   **Agents:** Two `ChatCompletionAgent` instances are created: `agent_writer` and `agent_reviewer`, each with specific instructions defining their roles.
*   **Group Chat:** An `AgentGroupChat` manages the interaction between the agents (and potentially the user).
*   **Selection Strategy:** Determines which agent speaks next. Here, `KernelFunctionSelectionStrategy` uses an LLM prompt (`selection_function`) that enforces a turn order (User -> Writer -> Reviewer -> Writer -> ...).
*   **Termination Strategy:** Determines when the chat should end. Here, `KernelFunctionTerminationStrategy` uses another LLM prompt (`termination_function`) to check if the Reviewer's last message indicates satisfaction (contains "yes").
*   **Chat Loop:** The `main` function takes user input (the initial content or feedback), adds it to the chat, and then calls `chat.invoke()`. The `AgentGroupChat` orchestrates the conversation based on the selection and termination strategies:
    *   Writer revises content based on user input/reviewer feedback.
    *   Reviewer checks the writer's output.
    *   If satisfactory, the reviewer might say something indicating approval, triggering termination.
    *   If not satisfactory, the reviewer provides feedback, and the loop continues with the writer.

**Code Breakdown:**

*   **Agent Definitions:** `ChatCompletionAgent` instances for `agent_reviewer` and `agent_writer` with detailed instructions.
*   **Selection Prompt (`selection_function`):** Defines rules for turn-taking based on the last speaker.
*   **Termination Prompt (`termination_function`):** Defines rules for ending the chat based on the reviewer's response indicating satisfaction.
*   **`AgentGroupChat` Setup:** Configures the chat with the agents and the selection/termination strategies.
*   **Main Loop:** Takes user input, adds it to the chat, invokes the chat, and prints agent responses until `chat.is_complete` is true (due to termination strategy or max iterations).

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/06-human-in-the-loop
# Ensure semantic-kernel, pyperclip are installed
python report-agents.py
```

Enter some initial text at the `User:>` prompt (e.g., "Draft a short paragraph about the benefits of AI agents."). Observe the interaction: the Writer will draft, the Reviewer will critique, the Writer will revise, and so on, until the Reviewer is satisfied (or the iteration limit is reached). You can provide feedback as the user during the loop.

!!! success "Simulating Human Review"
    This pattern demonstrates how agent interactions can model human review processes. A human could replace the `agent_reviewer`, or the `AgentGroupChat` could be integrated with a UI that presents the Writer's output to a human for explicit approval or feedback before the next step. This is a powerful way to ensure quality and alignment with human expectations.

---

## Hands-on Exercise Ideas (Module 6)

See the [Module 6 Exercises](./exercises.md) page for practical tasks.

---

!!! abstract "Further Reading & Resources (Human-in-the-Loop)"

    Explore how different frameworks implement HIL:

    *   **LangGraph Documentation:** [Human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/){target="_blank"}
    *   **LlamaIndex Documentation:** [Human in the loop](https://docs.llamaindex.ai/en/stable/understanding/agent/human_in_the_loop/){target="_blank"}
    *   **Tutorials & Examples:**
        *   [Build Your First Human-in-the-Loop AI Agent with NVIDIA NIM (NVIDIA Blog)](https://developer.nvidia.com/blog/build-your-first-human-in-the-loop-ai-agent-with-nvidia-nim/){target="_blank"}
        *   [Hands-on Tutorial: Building an AI Agent with human-in-the-loop control (SAP Community)](https://community.sap.com/t5/artificial-intelligence-and-machine-learning-blogs/hands-on-tutorial-building-an-ai-agent-with-human-in-the-loop-control/ba-p/14050267){target="_blank"}
        *   [n8n Tutorial: AI Agents with Human Feedback (YouTube)](https://m.youtube.com/watch?v=4wsV1GgIsrs){target="_blank"}
        *   [How to Build AI Agents with Human-In-The-Loop (YouTube)](https://www.youtube.com/watch?v=vyuenkJQpX8){target="_blank"}
    *   **Conceptual Discussions:**
        *   [Agents with Human in the Loop : Everything You Need to Know (Dev.to)](https://dev.to/camelai/agents-with-human-in-the-loop-everything-you-need-to-know-3fo5){target="_blank"}

---

This concludes Day 2, covering how agents can use tools, DSLs, process frameworks, browser automation, implement autonomous patterns like ReAct, and incorporate human interaction points. Day 3 will focus on more complex architectures involving multiple agents collaborating.

