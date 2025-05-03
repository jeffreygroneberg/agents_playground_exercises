# Day 2 - Module 4: Solving Complex Problems with Tools & DSLs

**Objective:** Understand how agents can tackle complex, multi-step problems by leveraging external tools, browser automation, and structured thinking patterns like Domain Specific Languages (DSLs).

**Source Code:** [`src/04-complex-problems/`](https://github.com/denniszielke/agentic-playground/tree/main/src/04-complex-problems){target="_blank"}

---

## Introduction

Day 1 focused on basic interactions and handling different data types. Day 2 moves towards more autonomous behavior. Real-world problems require agents to go beyond simple Q&A or single-tool use. They need to:

*   Interact with web interfaces (browsing, filling forms).
*   Follow specific, domain-bound procedures.
*   Break down complex goals into sequential steps.
*   Conduct research across multiple sources.

This module explores techniques shown in the `04-complex-problems` folder:

1.  **Domain Specific Languages (DSLs):** Guiding the LLM's planning and execution using a custom, restricted set of commands tailored to a specific task (e.g., logistics planning).
2.  **Combining DSLs with Tools:** Enhancing DSL-based plans by allowing the LLM to call external functions (tools) for validation or information gathering during execution.
3.  **Process Frameworks:** Using libraries like Semantic Kernel's process framework to define and manage sequential workflows.
4.  **Browser Automation:** Enabling agents to interact with websites to perform tasks like research, data extraction, or form submission.

!!! info "Moving Beyond Simple Tools"
    This module marks a shift towards more sophisticated agent capabilities. By combining LLMs with structured planning (DSLs), process management, and the ability to interact with the web, we can build agents capable of handling significantly more complex tasks.

## 1. Domain Specific Languages (DSLs) for Structured Thinking

**File:** [`src/04-complex-problems/trucking-plan.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/trucking-plan.py){target="_blank"}
*   [`src/04-complex-problems/trucking-execute.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/trucking-execute.py){target="_blank"}

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
    4.  If no tool call (or after a tool call response), returns the LLM's final message (which can be DSL commands or a natural language answer incorporating tool results).

**To Run (`trucking-execute.py`):**

```bash
cd /home/ubuntu/agentic-playground/src/04-complex-problems
# Install pytz if needed: pip install pytz
python trucking-execute.py
```

Observe the output. You should see the LLM calling `get_current_time` or `calculate_travel_time` and then generating the DSL plan or a final answer incorporating the calculated times.

!!! success "Benefits of DSLs"
    *   **Predictability:** Constrains LLM output to valid, expected actions.
    *   **Reliability:** Reduces chances of hallucinated or nonsensical plans.
    *   **Integration:** Makes it easier to connect LLM plans to existing code or APIs that understand the DSL.
    *   **Structured Thinking:** Forces the LLM to break down problems into domain-specific steps.

## 2. Process Frameworks (Semantic Kernel Example)

**File:** [`src/04-complex-problems/process-step.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/process-step.py){target="_blank"}

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

!!! tip "Benefits of Process Frameworks"
    *   **Clarity:** Explicitly defines the steps and transitions in a complex workflow.
    *   **State Management:** Provides a structured way to pass information between steps.
    *   **Modularity:** Encapsulates logic within individual steps.
    *   **Extensibility:** Can support more complex features like error handling, retries, and conditional branching (though not shown here).

## 3. Browser Automation for Web Interaction

Relevant files for this section include:

*   [`src/04-complex-problems/browser-use.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/browser-use.py){target="_blank"}
*   [`src/04-complex-problems/do-research.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/do-research.py){target="_blank"}
*   [`src/04-complex-problems/apply-for-job.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/apply-for-job.py){target="_blank"}
*   [`src/04-complex-problems/find-contract.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/04-complex-problems/find-contract.py){target="_blank"}
*   The custom library used by these scripts: [`src/browser_use/`](https://github.com/denniszielke/agentic-playground/tree/main/src/browser_use){target="_blank"}

Many tasks require interacting with websites. Agents can use browser automation tools (like Playwright, Selenium, or the custom `browser_use` library here) to perform actions like:

*   Navigating to URLs.
*   Extracting text content.
*   Clicking buttons or links.
*   Filling input fields.
*   Uploading files.

**Concept (`browser_use` Library):**

This repository includes a custom `browser_use` library (which wraps a tool like Playwright) that provides:

*   `Browser`: Manages the browser instance.
*   `Agent`: An agent class that takes a task, an LLM, a `Controller`, and a `Browser`.
*   `Controller`: Defines custom actions (`@controller.action`) that the agent can use. These actions often interact with the browser or local files.
*   `BrowserContext`: Passed to actions, allowing them to interact with the current browser page.
*   `ActionResult`: A standard return type for actions, including extracted content or error messages.

The `Agent` works in a loop:
1.  **Perceive:** Get the current page state (HTML, visible elements, URL).
2.  **Plan:** Send the page state, task description, and available actions (from the `Controller`) to the LLM.
3.  **Act:** The LLM decides the next action (e.g., `click`, `input`, `scroll`, or a custom action like `read_cv` or `save_jobs`). The `Agent` executes the action via the `Browser` or `Controller`.
4.  Repeat until the task is complete or an error occurs.

!!! info "The Perception-Planning-Action Loop"
    This iterative cycle is fundamental to many autonomous agents. The agent perceives its environment (the webpage), plans its next move based on its goal and capabilities (available actions), and then executes that action, changing the environment and starting the loop again.

**Code Examples:**

*   **`browser-use.py`:** A very simple example tasking the agent to compare prices by browsing the web.
*   **`do-research.py`:**
    *   Task: Research battery chemistry based on a taxonomy file and specific websites.
    *   Custom Actions: `read_taxonomy`, `save_insights` (saves findings to JSON).
    *   Demonstrates reading local files (`battery_chem.xml`) and saving structured output.
*   **`apply-for-job.py`:**
    *   Task: Find job offers, evaluate against a CV, apply.
    *   Custom Actions: `read_cv` (reads PDF), `save_jobs` (saves to CSV), `upload_cv` (interacts with file input elements on a webpage).
    *   Shows PDF reading and file upload interaction.
*   **`find-contract.py`:**
    *   Task: Find electricity contracts based on usage data.
    *   Custom Actions: `read_file` (reads usage data/location), `save_results` (saves contracts to CSV).
    *   Illustrates using predefined user data within the browsing task.

**To Run (Example: `do-research.py`):**

```bash
cd /home/ubuntu/agentic-playground/src/04-complex-problems
# Ensure dependencies are installed (requires browser_use setup, playwright, langchain, openai, pydantic)
# Requires specific browser setup (e.g., Chrome path in BrowserConfig)
# Ensure battery_chem.xml exists
python do-research.py
```

!!! warning "Running Browser Automation"
    Running these examples can be complex due to the custom `browser_use` library and specific browser setup needs (installing browsers, drivers, handling paths). Focus on understanding the pattern: **LLM decides -> Action executed -> Page state updated -> LLM decides again.**

---

!!! abstract "Further Reading & Resources"

    Explore these topics further:

    *   **Domain Specific Languages (DSLs) & LLMs:**
        *   [Large Language Models for Domain-Specific Language Generation (Medium - Part 1)](https://medium.com/@andreasmuelder/large-language-models-for-domain-specific-language-generation-how-to-train-your-dragon-0b5360e8ed76){target="_blank"}
        *   [Large Language Models for Domain-Specific Language Generation (Medium - Part 2: Constraints)](https://medium.com/@andreasmuelder/large-language-models-for-domain-specific-language-generation-part-2-how-to-constrain-your-dragon-e0e2439b6a53){target="_blank"}
        *   [Building Domain-Specific LLMs: Examples and Techniques (Kili Technology)](https://kili-technology.com/large-language-models-llms/building-domain-specific-llms-examples-and-techniques){target="_blank"}
        *   [What is a Domain-Specific LLM? Examples and Benefits (Aisera)](https://aisera.com/blog/domain-specific-llm/){target="_blank"}
    *   **Browser Automation & Web Agents:**
        *   [Playwright Documentation](https://playwright.dev/python/docs/intro){target="_blank"} (Popular browser automation library)
        *   [Selenium Documentation](https://www.selenium.dev/documentation/){target="_blank"} (Another popular browser automation library)
        *   [LangChain Browser Integration](https://python.langchain.com/docs/integrations/tools/browserbase/){target="_blank"} (Example of integrating browsing tools with agents)
        *   [Building Autonomous Agents that Browse the Web (YouTube - AssemblyAI)](https://www.youtube.com/watch?v=Ij99P3GUQzA){target="_blank"}
    *   **Process Frameworks / Orchestration:**
        *   [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/overview/){target="_blank"} (Explore planners and orchestration features)
        *   [LangChain Agents: Introduction](https://python.langchain.com/docs/modules/agents/){target="_blank"} (Covers different agent types and execution loops)

---

This module demonstrated how agents can tackle more complex problems using structured approaches like DSLs, process frameworks, and browser automation. The next module will focus on implementing single, autonomous agents using patterns like ReAct.

