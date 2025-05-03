# Day 2 - Module 4: Solutions

These are the solutions or discussion points for the exercises in Module 4.

## Solution 4.1: Modifying the Trucking DSL Plan

Modify `src/04-complex-problems/trucking-plan.py`:

```python
# ... (imports, client setup, commandprompt definition remain the same) ...

# --- Modified User Query --- 
user_input = "I have 2 green boxes (10kg each) and 1 yellow box (5kg). Load them onto truck 1 and travel 250 km."
# -------------------------

messages=[
    {"role": "system", "content": commandprompt},
    {"role": "user", "content": user_input},
]

response = client.chat.completions.create(
    messages=messages,
    model=model_name,
)

print(f"{response.choices[0].message.content}")
```

**Expected Output:** The output should be a sequence of DSL commands similar to this (exact box IDs can vary):

```
prepare_truck(truck_id=1)
load_box_on_truck(truck_id=1, box_id=1, weight=10)
load_box_on_truck(truck_id=1, box_id=2, weight=10)
load_box_on_truck(truck_id=1, box_id=3, weight=5)
calculate_weight_of_truck(truck_id=1)
drive_truck_to_location(truck_id=1, weight=25, distance=250)
```
This demonstrates the LLM correctly interpreting the new box quantities, weights, truck ID, and distance, and translating them into the defined DSL.

## Solution 4.2: Triggering a Tool in the Trucking DSL Execution

Modify `src/04-complex-problems/trucking-execute.py`:

```python
# ... (imports, tool definitions, client setup, commandprompt, run_conversation remain the same) ...

# --- Modified User Query --- 
user_query = "Prepare truck 3. Load a 20kg package. Calculate the travel time for a 300 km journey and tell me the estimated arrival time based on the current time."
# -------------------------

response = run_conversation(user_query)
print(response)
```

**Expected Output:**
*   The script execution trace should show calls to `get_current_time` (without arguments, or the LLM invents a location if not specified) and `calculate_travel_time` (with `distance=300`).
*   The final output from the `print(response)` statement will be a natural language sentence incorporating the results, such as: "Okay, truck 3 is prepared with the 20kg package. The current time is [time from tool]. The estimated travel time for 300 km is [time from tool]. Therefore, the estimated arrival time is approximately [calculated arrival time]."
*   Alternatively, the LLM can also output some DSL commands mixed with the tool calls and final answer, depending on its interpretation.

This shows the LLM using the available tools (`get_current_time`, `calculate_travel_time`) when the query explicitly requires information provided by those tools, integrating the results into its response.

## Solution 4.3 (Conceptual): Designing a Tea-Making DSL

This requires defining commands and a sample plan.

**Example DSL Commands:**

*   `boil_water(kettle_id: str)`: Starts boiling water in the specified kettle.
*   `check_kettle_boiled(kettle_id: str) -> bool`: Checks if the water in the kettle has boiled.
*   `get_cup(cup_id: str)`: Retrieves a clean cup.
*   `add_tea_bag(cup_id: str, tea_type: str)`: Places a tea bag of the specified type into the cup.
*   `pour_water(kettle_id: str, cup_id: str)`: Pours boiled water from the kettle into the cup.
*   `wait(seconds: int)`: Pauses execution for the specified duration (for steeping).
*   `remove_tea_bag(cup_id: str)`: Removes the tea bag from the cup.
*   `add_milk(cup_id: str, amount_ml: int)`: Adds the specified amount of milk.
*   `add_sugar(cup_id: str, spoons: int)`: Adds the specified number of spoons of sugar.
*   `stir(cup_id: str)`: Stirs the contents of the cup.
*   `serve(cup_id: str)`: Presents the finished cup of tea.

**Sample Plan (Black tea, milk, 2 sugars, 60s steep):**

```
get_cup(cup_id="my_cup")
add_tea_bag(cup_id="my_cup", tea_type="black_tea")
boil_water(kettle_id="kitchen_kettle")
# Loop or wait until check_kettle_boiled(kettle_id="kitchen_kettle") returns true
pour_water(kettle_id="kitchen_kettle", cup_id="my_cup")
wait(seconds=60)
remove_tea_bag(cup_id="my_cup")
add_milk(cup_id="my_cup", amount_ml=30)
add_sugar(cup_id="my_cup", spoons=2)
stir(cup_id="my_cup")
serve(cup_id="my_cup")
```

## Solution 4.4 (Conceptual): Adding Summarization to Research Agent

This requires discussing modifications to the agent's task or tools.

**1. Modifying the Task Description:**

You could modify the `task` string given to the `Agent` class in `do-research.py`:

*   **Original (Conceptual):** "Research battery chemistry based on `battery_chem.xml` and specific websites. Save detailed insights using `save_insights` action."
*   **Modified:** "Research battery chemistry based on `battery_chem.xml` and specific websites. Save detailed insights using `save_insights` action. **After saving the insights, provide a concise summary paragraph of the key findings.**"

Adding the summarization requirement directly to the task description is sufficient if the underlying LLM is capable enough. It performs the research, calls `save_insights`, and then generates the summary as its final output.

**2. Adding a New Custom Action:**

If simply modifying the task isn't reliable, or if you want more control over the summarization process (e.g., summarizing specific parts of the saved data), you could add a new action:

```python
# In the Controller definition within do-research.py or browser_use library

@controller.action(
    "summarize_findings",
    params={"findings_text": "Text containing the research findings to be summarized"}
)
def summarize_findings(findings_text: str):
    """Generates a concise summary paragraph of the provided text."""
    # Option 1: Call the LLM again specifically for summarization
    summary_prompt = f"Summarize the following research findings into a single concise paragraph:\n\n{findings_text}"
    # Assume 'llm' is accessible here or passed in
    summary = llm.invoke(summary_prompt) # Or use the agent's LLM instance
    logger.info(f"Generated summary: {summary}")
    # This action returns the summary text, which the agent 
    # includes in its final response, or it logs it.
    return ActionResult(extracted_content=summary, include_in_memory=True) 

    # Option 2: Use a dedicated summarization library (less common needed here)
```

**Integration:**
*   The LLM, guided by the modified task description, would need to decide to call `summarize_findings` *after* gathering and saving the research data.
*   It would need to retrieve the gathered text (from the `ActionResult` of previous steps or by reading the saved JSON file via another tool) to pass as input to `summarize_findings`.

**Which approach is better?**
*   Modifying the task description is simpler if the LLM can handle the sequential requirement (research -> save -> summarize).
*   Adding a dedicated tool gives more explicit control and is necessary if the summarization needs specific logic or needs to operate on structured data retrieved from the saved file.
