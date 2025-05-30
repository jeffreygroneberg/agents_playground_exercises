# Day 3 - Module 7: Exercises

These exercises are based on the concepts and code presented in Module 7: Multi-Agent Collaboration (`src/07-multi-agent-collaboration/`).

## Exercise 7.1: Changing the Coding Task (Multi-Agent)

**Goal:** Observe how the Coder/Reviewer LangGraph agents handle a different programming task.

1.  Open the `src/07-multi-agent-collaboration/coding-agents.py` script.
2.  Locate the `query` variable near the end of the script:
    ```python
    query = "Create a function in python that trains a regression model..."
    ```
3.  Change the `query` to a different, relatively simple coding task. Examples:
    *   "Write a Python function that takes a list of numbers and returns the sum of squares."
    *   "Create a Python class `Rectangle` with methods to calculate area and perimeter."
    *   "Write a Python function to check if a given string is a palindrome."
4.  Run the script (`python coding-agents.py`).
5.  Observe the output. Does the Coder agent generate appropriate code for the new task? Does the Reviewer provide relevant feedback? Does the process converge to a reasonable solution?

## Exercise 7.2: Adjusting Review Criteria (Multi-Agent)

**Goal:** Modify the reviewer agent's instructions to influence the collaboration process.

1.  Open the `src/07-multi-agent-collaboration/coding-agents.py` script.
2.  Locate the `reviewer_start` prompt string variable.
3.  Modify the prompt to add a specific requirement for the reviewer. For example, add:
    *   "Ensure that all functions include type hints."
    *   "Verify that the code includes comments explaining complex logic."
    *   "Check if the code handles potential edge cases or errors (e.g., empty lists, invalid input)."
4.  Run the script using the original regression model `query` (or the query from Exercise 7.1).
5.  Compare the reviewer's feedback to previous runs. Does the reviewer now specifically mention the new criterion you added? Does this change how the Coder revises the code?

## Exercise 7.3: Comparing Single vs. Multi-Agent Output

**Goal:** Compare the code generated by the single reasoning agent (`reasoning-coder.py`) with the final code produced by the multi-agent system (`coding-agents.py`) for the same task.

1.  Choose a coding task (e.g., the original regression model task, or the factorial/palindrome task from Exercise 7.1).
2.  Run `coding-agents.py` with your chosen task and note the final code generated after the review cycles.
3.  Run `reasoning-coder.py` with the *exact same* task description.
4.  Compare the code generated by both scripts:
    *   Does the code achieve the objective in both cases?
    *   Are there differences in code style, structure, or quality?
    *   Did the multi-agent review process catch issues or lead to improvements that the single agent missed?
    *   Which approach seemed more effective or efficient for this specific task?

## Exercise 7.4 (Conceptual): Designing a Trip Planning Graph

**Goal:** Practice designing a multi-agent workflow using the LangGraph conceptual model.

1.  Imagine creating a multi-agent system to help a user plan a trip.
2.  Define potential agent roles. Examples:
    *   `FlightFinder`: Searches for flights based on origin, destination, dates.
    *   `HotelFinder`: Searches for hotels based on location, dates, budget.
    *   `ActivityPlanner`: Suggests activities based on interests and location.
    *   `ItineraryCompiler`: Gathers information from other agents and creates a structured itinerary.
    *   `UserInteraction`: Handles communication with the user (getting preferences, presenting options, asking for confirmation).
3.  Sketch a diagram or list the steps for a possible workflow using these agents in a LangGraph structure.
    *   What would the `GraphState` need to hold (e.g., destination, dates, flight_options, hotel_options, chosen_flight, chosen_hotel, itinerary)?
    *   Where would conditional edges be needed (e.g., based on user choices)?
    *   Where would human-in-the-loop interrupts be needed (e.g., for the user to select a flight or hotel)?
