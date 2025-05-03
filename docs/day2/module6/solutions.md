# Day 2 - Module 6: Solutions

These are the solutions or discussion points for the exercises in Module 6.

## Solution 6.1: Changing the Interrupt Message

Modify [`src/06-human-in-the-loop/interrupt.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/06-human-in-the-loop/interrupt.py){target="_blank"}:

```python
# ... (imports, State definition, node1, node3 remain the same) ...

async def node2(state: State):
    print("---Node 2--- AI is asking for input")
    # --- Modified Interrupt Call --- 
    human_input = await interrupt({"prompt_for_user": "Please provide your favorite color to continue.", "current_step": "node2"})
    # ---------------------------
    print(f"---Node 2--- Got human input: {human_input}")
    return {"human_answer": human_input}

# ... (graph building and run_graph function remain the same) ...
```

**Expected Output:**
When the script pauses after `node1`, instead of asking for age, the output before the input prompt should reflect the new dictionary passed to `interrupt`. The exact display depends on how the `astream` consumer prints the interrupt information, but it should contain the keys `prompt_for_user` and `current_step` with their corresponding values.

## Solution 6.2: Modifying the Reviewer Agent

**Part A: Change Initial Input:**
Running the script and providing "Write a tweet about the importance of testing software." at the `User:` prompt will initiate the Writer/Reviewer loop for this new topic.

**Part B: Modify Reviewer Instructions:**
Modify [`src/06-human-in-the-loop/report-agents.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/06-human-in-the-loop/report-agents.py){target="_blank"}:

```python
# ... (imports, other agent definitions remain the same) ...

# --- Modified Reviewer Instructions --- 
REVIEWER_INSTRUCTIONS = """
You are a strict reviewer. 
Review the text provided by the writer. 
Ensure the text is less than 100 characters and includes at least one hashtag. 
Provide detailed feedback if it does not meet the criteria. 
If it meets the criteria, respond with only the word "yes".
"""
# ------------------------------------

# ... (rest of the script, including agent creation and chat loop, remains the same) ...
```

**Expected Output Comparison (Part A vs. Part B):**
*   **Part A (Original Reviewer):** The reviewer provides general feedback on clarity or style. The number of turns is relatively small if the initial draft is decent.
*   **Part B (Stricter Reviewer):** The reviewer will specifically check for length (< 100 chars) and the presence of a hashtag. If the writer's initial draft (or revisions) fails these checks, the reviewer will provide targeted feedback (e.g., "The text is too long.", "Missing hashtag."). This will lead to more revision cycles (more turns in the conversation) before the reviewer responds with "yes".

## Solution 6.3 (Conceptual): Modifying Interrupt for Approval

This requires discussing changes to the node and graph structure.

**1. Modifying `node2`:**

```python
async def node2(state: State):
    print("---Node 2--- Presenting plan for approval")
    plan_result = "Plan A: Use algorithm X" # Simulate some result
    
    # Interrupt to ask for approval
    human_input = await interrupt({
        "data_to_approve": plan_result, 
        "prompt": f"Proposed plan: 
{plan_result}

Do you approve? (yes/no)"
    })
    
    print(f"---Node 2--- Got human input: {human_input}")
    # Store the decision in the state for conditional branching
    return {"human_approval": human_input.lower().strip()}
```

**2. Modifying Graph Structure:**

You need to define a function to handle the conditional logic and use `builder.add_conditional_edges`.

```python
from langgraph.graph import StateGraph, END
from typing import Literal

# ... (State definition including 'human_approval': str) ...
# ... (node1, node2, node3 definitions) ...

# Define a new node to handle rejection (optional)
async def handle_rejection(state: State):
    print("---Node Rejection--- Plan was not approved.")
    # Can loop back or end here
    return {}

# Conditional edge logic
def check_approval(state: State) -> Literal["approved", "rejected"]:
    if state.get("human_approval") == "yes":
        return "approved"
    else:
        return "rejected"

# Build the graph
builder = StateGraph(State)
builder.add_node("node1", node1)
builder.add_node("node2", node2) # Node 2 now returns 'human_approval'
builder.add_node("node3", node3) # The 'approved' path
builder.add_node("rejection_node", handle_rejection) # The 'rejected' path

builder.set_entry_point("node1")
builder.add_edge("node1", "node2")

# Add conditional edges after node2
builder.add_conditional_edges(
    "node2",
    check_approval, # Function to determine the branch
    {
        "approved": "node3", # If check_approval returns "approved", go to node3
        "rejected": "rejection_node" # If check_approval returns "rejected", go to rejection_node
    }
)

# Define endpoints
builder.add_edge("node3", END)
builder.add_edge("rejection_node", END) # Or loop back, e.g., builder.add_edge("rejection_node", "node1")

# Compile the graph (with checkpointer)
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# ... (run_graph function would work similarly, handling the interrupt from node2) ...
```
This structure allows the graph to branch based on the human's "yes" or "no" input received during the interrupt.
