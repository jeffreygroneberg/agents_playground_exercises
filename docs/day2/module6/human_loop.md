# Day 2 - Module 6: Human-in-the-Loop Patterns

**Objective:** Understand why and how to incorporate human oversight, feedback, and intervention into agent workflows.

**Source Code:** `/home/ubuntu/agentic-playground/src/06-human-in-the-loop/`

---

## Introduction

While the goal is often to create fully autonomous agents, there are many scenarios where human involvement is crucial or desirable:

*   **Safety and Control:** Preventing agents from taking harmful or unintended actions.
*   **Quality Assurance:** Reviewing or correcting agent outputs before they are finalized.
*   **Guidance and Decision Making:** Providing input when the agent faces ambiguity or requires subjective judgment.
*   **Learning and Improvement:** Using human feedback to fine-tune agent behavior.

This module explores patterns for integrating humans into the agent execution loop, focusing on:

1.  **Interruptible Workflows (LangGraph):** Pausing agent execution at specific points to wait for human input before proceeding.
2.  **Collaborative Review Loops (Semantic Kernel):** Designing multi-agent systems where one agent's output is reviewed (potentially by a human or another agent acting as a proxy) before further action.

## 1. Interruptible Workflows with LangGraph

**File:** `src/06-human-in-the-loop/interrupt.py`

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

**Key LangGraph Concepts for HIL:**
*   Graphs define the flow.
*   `interrupt()` pauses execution and waits for input.
*   Checkpointer saves state during interruption.
*   `Command(resume=...)` provides input to resume.

## 2. Collaborative Review Loops (Semantic Kernel AgentGroupChat)

**File:** `src/06-human-in-the-loop/report-agents.py`

This example uses Semantic Kernel's `AgentGroupChat` to simulate a scenario where a 

"Writer" agent drafts content, and a "Reviewer" agent provides feedback. The loop continues until the Reviewer deems the content satisfactory. While the Reviewer is an AI agent here, it simulates the role a human might play in a review process.

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

**Simulating Human Review:**
This pattern demonstrates how agent interactions can model human review processes. A human could replace the `agent_reviewer`, or the `AgentGroupChat` could be integrated with a UI that presents the Writer's output to a human for explicit approval or feedback before the next step.

---

## Hands-on Exercise Ideas (Module 6)

1.  **Modify `interrupt.py`:** Change the message sent during the interrupt in `node2`. Run the script and see the new message when it pauses.
2.  **Modify `report-agents.py`:**
    *   Change the initial user input to provide a different piece of text for review.
    *   Modify the `REVIEWER_NAME` agent's instructions to be more lenient or stricter in its review criteria. Observe how this affects the number of revision cycles.
3.  **(Conceptual)** How could the `interrupt.py` example be modified to ask the human for *approval* before `node3` runs, rather than just asking for data? (Hint: The human input could be "yes" or "no", and the graph could have conditional edges after `node2` based on this input).

---

This concludes Day 2, covering how agents can use tools, DSLs, process frameworks, browser automation, implement autonomous patterns like ReAct, and incorporate human interaction points. Day 3 will focus on more complex architectures involving multiple agents collaborating.
