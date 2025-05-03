# Day 2 - Module 6: Exercises

These exercises are based on the concepts and code presented in Module 6: Human-in-the-Loop Patterns (`src/06-human-in-the-loop/`).

## Exercise 6.1: Changing the Interrupt Message

**Goal:** Practice modifying the information presented to the user when a workflow is interrupted.

1.  Open the `src/06-human-in-the-loop/interrupt.py` script.
2.  Locate the `node2` function.
3.  Find the line where `interrupt()` is called:
    ```python
    human_input = await interrupt({"ai_answer": "What is your age?"})
    ```
4.  Change the dictionary passed to `interrupt`. For example, change the question or add more context:
    ```python
    human_input = await interrupt({"prompt_for_user": "Please provide your favorite color to continue.", "current_step": "node2"})
    ```
5.  Run the script (`python interrupt.py`).
6.  Observe the output when the script pauses. Does it display the new message or data structure you provided in the `interrupt` call?

## Exercise 6.2: Modifying the Reviewer Agent

**Goal:** Observe how changing an agent's instructions affects its behavior in a collaborative loop.

1.  Open the `src/06-human-in-the-loop/report-agents.py` script.
2.  **Part A: Change Initial Input:**
    *   Locate the `main` function and the initial user prompt:
        ```python
        user_input = input("User: ")
        ```
    *   Run the script (`python report-agents.py`). When prompted for `User:`, provide a different piece of text than the example, e.g., "Write a tweet about the importance of testing software."
    *   Observe the interaction between the Writer and Reviewer agents.
3.  **Part B: Modify Reviewer Instructions:**
    *   Stop the script if it's running.
    *   Find the `REVIEWER_INSTRUCTIONS` variable.
    *   Modify the instructions to make the reviewer stricter or more lenient. For example:
        *   **Stricter:** Add a requirement like "Ensure the text is less than 100 characters and includes a hashtag."
        *   **Lenient:** Change the instructions to something like "Briefly check for major grammatical errors only. Approve if it looks reasonable."
    *   Run the script again, providing the same initial input as in Part A.
    *   Compare the interaction to Part A. Does the reviewer's feedback change? Does the conversation take more or fewer turns to complete?

## Exercise 6.3 (Conceptual): Modifying Interrupt for Approval

**Goal:** Think about how to adapt the interrupt pattern for a yes/no approval step.

1.  Consider the `interrupt.py` example where `node2` interrupts to get the user's age.
2.  Imagine you want `node2` to present some data (e.g., `result = "Plan A"`) and ask the human for approval before `node3` runs.
3.  How would you modify `node2`?
    *   What dictionary would you pass to `interrupt()`? (e.g., `{"data_to_approve": result, "prompt": "Do you approve this plan? (yes/no)"}`)
    *   How would you check the `human_input` received after the interrupt?
4.  How would you modify the graph structure (`builder.add_edge`)? Conditional edges would be needed after `node2`.
    *   If `human_input` is "yes", add an edge from `node2` to `node3`.
    *   If `human_input` is "no", what should happen? Add an edge back to `node1`? Add an edge to a new "handle_rejection" node? Add an edge directly to `END`?
