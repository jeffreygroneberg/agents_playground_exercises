# Day 2 - Module 4: Solving Complex Problems with Tools & DSLs

**Objective:** Understand how agents can tackle complex, multi-step problems by leveraging external tools, browser automation, and structured thinking patterns like Domain Specific Languages (DSLs).

**Source Code:** `/home/ubuntu/agentic-playground/src/04-complex-problems/`

---

## Introduction

Day 1 focused on basic interactions and handling different data types. Day 2 moves towards more autonomous behavior. Real-world problems often require agents to go beyond simple Q&A or single-tool use. They might need to:

*   Interact with web interfaces (browsing, filling forms).
*   Follow specific, domain-bound procedures.
*   Break down complex goals into sequential steps.
*   Conduct research across multiple sources.

This module explores techniques shown in the `04-complex-problems` folder:

1.  **Domain Specific Languages (DSLs):** Guiding the LLM's planning and execution using a custom, restricted set of commands tailored to a specific task (e.g., logistics planning).
2.  **Combining DSLs with Tools:** Enhancing DSL-based plans by allowing the LLM to call external functions (tools) for validation or information gathering during execution.
3.  **Process Frameworks:** Using libraries like Semantic Kernel's process framework to define and manage sequential workflows.
4.  **Browser Automation:** Enabling agents to interact with websites to perform tasks like research, data extraction, or form submission.

## 1. Domain Specific Languages (DSLs) for Structured Thinking

**Files:**
*   `src/04-complex-problems/trucking-plan.py`
*   `src/04-complex-problems/trucking-execute.py`

Instead of letting the LLM generate free-form plans, we can constrain its output to a specific set of commands (a DSL) that represent valid actions within a particular domain. This makes the agent's behavior more predictable and easier to integrate with existing systems.

**Concept (Trucking Example):**

The goal is to plan the logistics of loading boxes onto trucks and driving them.

*   **Define the DSL:** The system prompt in `trucking-plan.py` explicitly defines a set of commands:
    *   `prepare_truck(truck_id)`
    *   `load_box_on_truck(truck_id, box_id, weight)`
    *   `calculate_weight_of_truck(truck_id)`
    *   `drive_truck_to_location(truck_id, weight, distance)`
    *   `unload_box_from_truck(truck_id, box_id, weight)`
*   **Provide Context:** The prompt also gives rules (max weight/boxes, loading time, box weights) and examples of how user requests map to DSL commands.
*   **LLM Generates DSL Plan:** When given a user request (e.g., "I have a red box and 3 blue boxes... load the boxes... travel 100 km"), the LLM's task is *not* to answer directly, but to generate a sequence of these DSL commands.

**Code Breakdown (`trucking-plan.py`):**

*   **`commandprompt`:** Contains the DSL definition, rules, examples, and instructions for the LLM.
*   **API Call:** Sends the `commandprompt` as the system message and the user's logistics request.
*   **Output:** The script simply prints the LLM's response, which should be a sequence of DSL commands.

```python
# commandprompt defines the DSL and rules
messages=[
    {"role": "system", "content": commandprompt},
    {"role": "user", "content": "I have a red box and 3 blue boxes..."},
]
response = client.chat.completions.create(
    messages=messages,
    model=model_name,
)
print(f"{response.choices[0].message.content}")
```

**To Run (`trucking-plan.py`):**

```bash
cd /home/ubuntu/agentic-playground/src/04-complex-problems
python trucking-plan.py
```

Observe the output: it should be a series of `prepare_truck`, `load_box_on_truck`, etc., commands representing the plan.

**Code Breakdown (`trucking-execute.py`):**

This script takes the DSL concept further by combining it with **tool calling**.

*   **DSL Definition:** The `commandprompt` is similar but now also instructs the LLM it can use tools like `get_current_time` and `calculate_travel_time`.
*   **Tool Definitions:**
    *   Python functions (`get_current_time`, `calculate_travel_time`) are defined.
    *   Corresponding tool schemas (`functions`) are created for the LLM.
*   **Conversation Loop (`run_conversation`):** This function manages the interaction:
    1.  Sends the user query, DSL prompt, and available tools to the LLM.
    2.  Checks if the LLM response includes `tool_calls`.
    3.  If yes: Executes the requested Python function, appends the result to the message history (with `role: "tool"`), and calls the LLM *again* with the updated history.
    4.  If no tool call (or after a tool call response), returns the LLM's final message (which might be DSL commands or a natural language answer incorporating tool results).

**To Run (`trucking-execute.py`):**

```bash
cd /home/ubuntu/agentic-playground/src/04-complex-problems
# Install pytz if needed: pip install pytz
python trucking-execute.py
```

Observe the output. You should see the LLM potentially calling `get_current_time` or `calculate_travel_time` and then generating the DSL plan or a final answer incorporating the calculated times.

**Benefits of DSLs:**
*   More reliable and predictable agent behavior.
*   Easier integration with existing code (parse the DSL commands and execute corresponding actions).
*   Forces the LLM to think step-by-step within defined constraints.

## 2. Process Frameworks (Semantic Kernel Example)

**File:** `src/04-complex-problems/process-step.py`

For tasks that involve a clear sequence of steps, process frameworks provide a structured way to define and manage the flow.

**Concept (Semantic Kernel Process):**

This example uses Semantic Kernel's experimental process framework to create a simple two-step process: get the user's name, then display a greeting.

*   **Events:** Define events that trigger transitions between steps (e.g., `NameReceived`, `ProcessComplete`).
*   **State:** Define a data structure (`HelloWorldState`) to hold information shared between steps (e.g., the user's name).
*   **Steps:** Define classes (`GetNameStep`, `DisplayGreetingStep`) inheriting from `KernelProcessStep`. Each step:
    *   Can have an `activate` method for initialization.
    *   Contains kernel functions (`@kernel_function`) that perform the step's logic.
    *   Can access and modify the shared `state`.
    *   Emits events (`context.emit_event`) to signal completion or trigger the next step.
*   **Process Builder:** Use `ProcessBuilder` to:
    *   Add the steps.
    *   Define the flow by linking events from one step to the activation of another (`process.on_input_event`, `step.on_event`).
    *   Define start and stop conditions.
*   **Run Process:** Use `start` to initiate the process with an initial event.

**Code Breakdown:**

*   Imports relevant Semantic Kernel process components.
*   Defines `HelloWorldEvents` (Enum) and `HelloWorldState` (Pydantic model).
*   Implements `GetNameStep` (gets input, updates state, emits `NameReceived`).
*   Implements `DisplayGreetingStep` (receives state via event, generates greeting, prints, emits `ProcessComplete`).
*   `run_hello_world_process` function sets up the `ProcessBuilder`, links events to steps, builds, and starts the process.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/04-complex-problems
# Ensure semantic-kernel is installed: pip install semantic-kernel
python process-step.py
```

The script will prompt you for your name and then print the greeting, demonstrating the sequential execution managed by the framework.

**Benefits of Process Frameworks:**
*   Clear definition of complex workflows.
*   Manages state transitions between steps.
*   Facilitates error handling and retries (though not shown in this simple example).

## 3. Browser Automation for Web Interaction

**Files:**
*   `src/04-complex-problems/browser-use.py`
*   `src/04-complex-problems/do-research.py`
*   `src/04-complex-problems/apply-for-job.py`
*   `src/04-complex-problems/find-contract.py`
*   (Uses library from `src/browser_use/`) - Note: This seems to be a custom library within the repo.

Many tasks require interacting with websites. Agents can use browser automation tools (like Playwright, Selenium, or the custom `browser_use` library here) to perform actions like:

*   Navigating to URLs.
*   Extracting text content.
*   Clicking buttons or links.
*   Filling input fields.
*   Uploading files.

**Concept (`browser_use` Library):**

This repository includes a custom `browser_use` library (likely wrapping a tool like Playwright) that provides:

*   `Browser`: Manages the browser instance.
*   `Agent`: An agent class that takes a task, an LLM, a `Controller`, and a `Browser`.
*   `Controller`: Defines custom actions (`@controller.action`) that the agent can use. These actions often interact with the browser or local files.
*   `BrowserContext`: Passed to actions, allowing them to interact with the current browser page.
*   `ActionResult`: A standard return type for actions, potentially including extracted content or error messages.

The `Agent` likely works by:
1.  Receiving the current page state (HTML, visible elements).
2.  Sending the page state, task description, and available actions (from the `Controller`) to the LLM.
3.  The LLM decides the next action (e.g., `click`, `input`, `scroll`, or a custom action like `read_cv` or `save_jobs`).
4.  The `Agent` executes the action via the `Browser` or `Controller`.
5.  Repeats until the task is complete.

**Code Examples:**

*   **`browser-use.py`:** A very simple example tasking the agent to compare prices by likely browsing the web.
*   **`do-research.py`:**
    *   Task: Research battery chemistry based on a taxonomy file and specific websites.
    *   Custom Actions: `read_taxonomy`, `save_insights` (saves findings to JSON).
    *   Demonstrates reading local files (`battery_chem.xml`) and saving structured output.
*   **`apply-for-job.py`:**
    *   Task: Find job offers, evaluate against a CV, potentially apply.
    *   Custom Actions: `read_cv` (reads PDF), `save_jobs` (saves to CSV), `upload_cv` (interacts with file input elements on a webpage).
    *   Shows PDF reading and file upload interaction.
*   **`find-contract.py`:**
    *   Task: Find electricity contracts based on usage data.
    *   Custom Actions: `read_file` (reads usage data/location), `save_results` (saves contracts to CSV).
    *   Illustrates using predefined user data within the browsing task.

**To Run (Example: `do-research.py`):**

```bash
cd /home/ubuntu/agentic-playground/src/04-complex-problems
# Ensure dependencies are installed (likely requires browser_use setup, potentially playwright, langchain, openai, pydantic)
# May require specific browser setup (e.g., Chrome path in BrowserConfig)
# Ensure battery_chem.xml exists
python do-research.py
```

Running these might be complex due to the custom library and potential browser setup needs. Focus on understanding the pattern: **LLM decides -> Action executed -> Page state updated -> LLM decides again.**

**Key Concepts for Browser Automation:**
*   Agents can perceive web pages (DOM structure, visible elements).
*   Agents can act on web pages (click, type, scroll, upload).
*   Custom actions allow agents to interact with local files or external APIs during browsing.
*   Essential for tasks involving information gathering from the web or interacting with web applications.

---

## Hands-on Exercise Ideas (Module 4)

1.  **Modify `trucking-plan.py`:** Change the user query to include different numbers/types of boxes or a different distance. Observe how the generated DSL plan changes.
2.  **Modify `trucking-execute.py`:** Change the user query to ask for the arrival time explicitly after loading and driving. See if the agent uses the `calculate_travel_time` tool.
3.  **(Conceptual)** How would you define a DSL for making a simple cup of tea (e.g., `boil_water`, `add_tea_bag`, `pour_water`, `add_milk`, `wait`)? Write down the commands and a sample plan.
4.  **(Conceptual, based on `do-research.py`)** If you wanted the research agent to *summarize* the findings instead of just saving them, how might you modify the task description or add a new custom action?

---

This module demonstrated how agents can tackle more complex problems using structured approaches like DSLs, process frameworks, and browser automation. The next module will focus on implementing single, autonomous agents using patterns like ReAct.
