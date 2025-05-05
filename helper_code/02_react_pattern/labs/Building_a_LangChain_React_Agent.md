# LangChain ReAct Agent Lab: Building an Automotive Assistant

**Goal:** Build a simple conversational agent using Python, LangChain, and the ReAct pattern to answer automotive-related questions.

**Time:** Approximately 1 hour

**Level:** Beginner

## Introduction (Est. 5 mins)

Welcome! In this lab, you'll create a basic AI agent that can reason and act (ReAct) to answer questions about cars. We'll use LangChain, a powerful framework for building applications with Large Language Models (LLMs), and OpenAI's models.

### What is LangChain?

LangChain is a framework designed to simplify the creation of applications using large language models (LLMs). It provides modular components and tools for managing prompts, chains, memory, agents, and more, allowing developers to build sophisticated AI applications like chatbots, question-answering systems, and autonomous agents.

### What is the ReAct Pattern?

The ReAct (Reasoning and Acting) pattern, introduced by Yao et al. (2022), is a powerful paradigm for enabling Large Language Models (LLMs) to solve complex tasks by synergizing reasoning and acting. Instead of just generating text, a ReAct agent interleaves verbal reasoning steps (like chain-of-thought prompting) with actions taken in an external environment (like using a tool or searching a database).

The core idea is that the model explicitly plans and reasons about the task (`Thought`), decides which action to take (`Action`), executes that action using a defined tool (`Action Input`), and then incorporates the result of that action (`Observation`) back into its reasoning process. This cycle repeats until the agent determines it has enough information to provide a `Final Answer`.

This approach allows the LLM to:
*   **Dynamically retrieve external information:** Overcome knowledge limitations by using tools to look up current or specific data.
*   **Improve grounding and factuality:** Base responses on observed information rather than just internal knowledge, reducing hallucination.
*   **Enhance interpretability:** The explicit `Thought` process makes it easier to understand how the agent arrived at its conclusion or why it took certain actions.
*   **Handle complex, multi-step tasks:** Break down problems and iteratively gather information or perform sub-tasks.

### Prerequisites

!!! note "Prerequisites"
    *   Basic Python knowledge (variables, functions, lists).
    *   Python 3.8+ and pip installed.
    *   An OpenAI API key.
    *   Familiarity with using a terminal or command prompt.

### Setup

!!! info "Environment Setup"
    1.  **Install Libraries:** Open your terminal and run:
        ```bash
        pip install langchain langchain-openai langchain-core python-dotenv
        ```
    2.  **Set API Key:** Create a file named `.env` in your project directory and add your OpenAI API key:
        ```
        OPENAI_API_KEY="your-api-key-here"
        ```
        We'll load this key in our Python script.

---

## Part 1: Basic ReAct Agent (No Tools, No Memory) (Est. 15 mins)

Let's start with the core ReAct logic using an LLM but without external tools or conversation history.

### 1.1 Imports

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain import hub

print("Imports successful!")
```

### 1.2 Load Environment Variables & Define LLM

```python
# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI chat model
# temperature=0 for more deterministic outputs
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

print(f"OpenAI API Key configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
print(f"Model initialized: {llm.model_name}")
```

### 1.3 Define the Prompt

We need a prompt that instructs the LLM on how to use the ReAct pattern. LangChain Hub provides pre-built prompts.

```python
# Pull the default ReAct prompt from LangChain Hub
react_prompt = hub.pull("hwchase17/react")

# Print the first 500 characters of the template to see its structure
print(f"Prompt template preview: {react_prompt.template[:500]}...")
```

!!! tip "Prompt Structure"
    Notice the placeholders like `{input}`, `{agent_scratchpad}`, and `{tools}` in the prompt template. These are crucial for the agent to function.

### 1.4 Create the Agent

The `create_react_agent` function combines the LLM and the prompt.

```python
# Create the ReAct agent
# We pass an empty list for tools initially
agent = create_react_agent(llm, [], react_prompt)

print("Agent created successfully.")
```

### 1.5 Create the Agent Executor

The `AgentExecutor` runs the agent loop (Thought -> Action -> Observation -> ...).

```python
# Create the AgentExecutor
# verbose=True allows us to see the agent's thought process
agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)

print("AgentExecutor created successfully.")
```

### 1.6 Run the Agent

Let's ask a simple automotive question.

```python
# Run the agent with a simple automotive question
response = agent_executor.invoke({"input": "What is the main function of a car's radiator?"})

# Print the final answer
print("\nFinal Answer:")
print(response['output'])
```

### 1.7 Understanding the Output

Observe the `verbose=True` output. You'll see the agent's `Thought`, its decision that it doesn't need a tool (`Action: Final Answer`), and the `Final Answer`.

---

## Part 2: Adding a Simple Local Tool (Est. 15 mins)

Now, let's empower the agent with a custom tool to look up specific information.

### 2.1 Define a Tool

A tool is just a Python function decorated with `@tool` from `langchain_core.tools`.

```python
from langchain_core.tools import tool

@tool
def get_vehicle_specs(model_name: str) -> str:
    """Looks up specifications for a given vehicle model name. Use this tool when asked about specific car specs like engine, horsepower, or fuel economy. Returns specs as a string or 'Model not found'."""
    # Simple hardcoded data for the lab
    specs = {
        "2024 honda civic": "Engine: 1.5L Turbocharged I4, Horsepower: 180 hp @ 6000 rpm, Fuel Economy: 33 MPG combined (EPA estimate)",
        "2023 toyota rav4": "Engine: 2.5L Dynamic Force 4-Cylinder, Horsepower: 203 hp @ 6600 rpm, Fuel Economy: 30 MPG combined (EPA estimate)",
        "2024 ford mustang mach-e": "Battery: 70-91 kWh options, Horsepower: 266-480 hp, Range: 226-310 miles (EPA estimate)",
        "volkswagen id.4 2023": "Battery: 82 kWh, Horsepower: 201 hp (RWD) / 295 hp (AWD), Range: 209-275 miles (EPA estimate)"
    }
    # Basic normalization
    search_key = model_name.lower().strip()
    print(f"Tool 'get_vehicle_specs' called with: {search_key}")
    result = specs.get(search_key, f"Model '{model_name}' not found in our database.")
    print(f"Tool 'get_vehicle_specs' returning: {result}")
    return result

print("Tool 'get_vehicle_specs' defined successfully.")
```

!!! warning "Tool Descriptions"
    The docstring within the tool function is crucial! The agent uses this description to decide *when* to use the tool.

### 2.2 Create the Tools List

```python
# Create a list containing our defined tool(s)
tools = [get_vehicle_specs]

print(f"Tools list created with {len(tools)} tool(s).")
```

### 2.3 Re-create Agent and Executor with Tools

We need to recreate the agent and executor, this time providing the tools.

```python
# Re-create the agent, this time passing the tools list
agent_with_tools = create_react_agent(llm, tools, react_prompt)

# Re-create the AgentExecutor, passing the new agent and the tools list
agent_executor_with_tools = AgentExecutor(agent=agent_with_tools, tools=tools, verbose=True)

print("Agent and AgentExecutor recreated with tools.")
```

### 2.4 Run the Agent with a Tool-Requiring Question

Ask a question that should trigger the tool.

```python
# Ask a question that requires the tool
# Try asking about one of the models in the tool's 'database'
input_question = "What is the horsepower of the 2024 Ford Mustang Mach-E?"
# input_question = "What are the specs for the Volkswagen ID.4 2023?"
# input_question = "Tell me about the engine in the 2024 Honda Civic."

print(f"\nInvoking agent with question: {input_question}")
response = agent_executor_with_tools.invoke({"input": input_question})

# Print the final answer
print("\nFinal Answer:")
print(response["output"])
```

Observe the output. You should see the agent think, decide to use `get_vehicle_specs` (`Action`), receive the specs (`Observation`), and then provide the `Final Answer`.

---

## Part 3: Adding Memory (Enhancement) (Est. 15 mins)

Let's give the agent context by adding conversation memory.

### 3.1 Import Memory & Update Prompt

We need a memory module and a prompt that handles `chat_history`.

```python
# Import memory components
from langchain.memory import ConversationBufferMemory

# Pull a conversational ReAct prompt from the Hub
# This prompt includes placeholders for 'chat_history'
conversational_react_prompt = hub.pull("hwchase17/react-chat")

# Print the first 500 characters of the template to see its structure
print(f"Conversational prompt template preview: {conversational_react_prompt.template[:500]}...")
```

### 3.2 Instantiate Memory

```python
# Create an instance of ConversationBufferMemory
# memory_key must match the input variable in the prompt ('chat_history')
# return_messages=True ensures the memory is stored as message objects, suitable for chat models
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

print("ConversationBufferMemory instantiated.")
```

### 3.3 Update Agent and Executor for Memory

Recreate the agent with the new conversational prompt and the executor with the memory object.

```python
# Re-create the agent using the conversational prompt and the tools
agent_with_memory = create_react_agent(llm, tools, conversational_react_prompt)

# Re-create the AgentExecutor with the new agent, tools, and memory
# handle_parsing_errors=True can help with robustness if the LLM output isn't perfectly formatted
agent_executor_with_memory = AgentExecutor(
    agent=agent_with_memory,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

print("Agent and AgentExecutor recreated with memory.")
```

### 3.4 Run a Conversation

Interact multiple times to see the memory in action.

```python
# First interaction
input1 = "Suggest a reliable SUV model available in your tool's data."
print(f"\nUser: {input1}")
response1 = agent_executor_with_memory.invoke({"input": input1})
print(f"Agent: {response1['output']}")

# Second interaction - agent should remember the context (the SUV model suggested)
input2 = "What is the fuel efficiency of that model?"
print(f"\nUser: {input2}")
response2 = agent_executor_with_memory.invoke({"input": input2})
print(f"Agent: {response2['output']}")

# Third interaction - ask about a different model to show tool use within conversation
input3 = "How about the range of the 2024 Ford Mustang Mach-E?"
print(f"\nUser: {input3}")
response3 = agent_executor_with_memory.invoke({"input": input3})
print(f"Agent: {response3['output']}")

# Check the memory content
print("\n--- Memory Check ---")
print(memory.load_memory_variables({}))
print("--- End Memory Check ---")
```

Notice how the agent uses the context from the first question (`chat_history`) to answer the second.

---

## Part 4: Advanced Challenges (Optional) (Est. 5 mins)

!!! success "Optional Challenges"
    Want to explore further? Try these:
    
    *   **More Complex Tools:** Create a tool that simulates looking up a vehicle part number based on a description.
    ```python
    @tool
    def get_part_number(description: str) -> str:
        """Looks up a part number based on a description. Use this for finding automotive part numbers."""
        parts_database = {
            "brake pad": "BP-4422-H",
            "oil filter": "OF-1337-T",
            "spark plug": "SP-9988-I",
            "air filter": "AF-2255-C",
            "timing belt": "TB-7766-F"
        }
        
        # Simple keyword matching
        for part_name, part_number in parts_database.items():
            if part_name.lower() in description.lower():
                return f"Part Number for '{part_name}': {part_number}"
        
        return f"No part number found for '{description}'. Try a different description."
    ```
    
    *   **Error Handling:** Modify your tool to sometimes raise an error and see how the agent handles it.
    ```python
    @tool
    def get_vehicle_specs_with_errors(model_name: str) -> str:
        """Looks up specifications for a given vehicle model. May occasionally have database errors."""
        # Simulate a database error for certain queries
        if "error" in model_name.lower() or "fail" in model_name.lower():
            raise ValueError("Database connection error! Try again or use a different model name.")
            
        # Rest of the function remains the same as get_vehicle_specs
        specs = {
            "2024 honda civic": "Engine: 1.5L Turbocharged I4, Horsepower: 180 hp @ 6000 rpm",
            # ... other models
        }
        return specs.get(model_name.lower(), f"Model '{model_name}' not found in our database.")
    ```
    
    *   **Custom Prompts:** Write your own ReAct prompt from scratch instead of using the Hub version.
    ```python
    # Create a custom prompt with an automotive mechanic personality
    custom_prompt_template = """You are AutoMechanic, an AI assistant with extensive knowledge of vehicles.
    
    TOOLS:
    {tools}
    
    CHAT HISTORY:
    {chat_history}
    
    When responding, first think about what the user is asking and whether you need to use a tool.
    If you need to use a tool, format your response as:
    
    Thought: I need to figure out what tool to use for this question.
    Action: tool_name
    Action Input: the input to the tool
    
    After you get the tool result, continue thinking and using tools if needed.
    When you have the final answer, respond as:
    
    Thought: I now know the answer.
    Final Answer: Your detailed and helpful response here.
    
    Begin!
    
    Question: {input}
    {agent_scratchpad}
    """
    
    from langchain_core.prompts import PromptTemplate
    custom_prompt = PromptTemplate.from_template(custom_prompt_template)
    ```
    
    *   **Different Memory:** Replace `ConversationBufferMemory` with `ConversationSummaryMemory`.
    ```python
    from langchain.memory import ConversationSummaryMemory
    
    # This memory type uses the LLM to create summaries of the conversation
    summary_memory = ConversationSummaryMemory(
        llm=llm,  # Uses the same LLM we defined earlier
        memory_key="chat_history",
        return_messages=True
    )
    
    # Then recreate your agent executor with this new memory type
    agent_executor_with_summary = AgentExecutor(
        agent=agent_with_memory,
        tools=tools,
        memory=summary_memory,
        verbose=True
    )
    ```

---

## Conclusion & Next Steps (Est. 5 mins)

Congratulations! You've successfully built a conversational ReAct agent using LangChain, complete with custom tools and memory, all within an automotive context.

**Key Learnings:**
*   Setting up LangChain with OpenAI.
*   Understanding the ReAct agent flow (Thought, Action, Observation).
*   Using `create_react_agent` and `AgentExecutor`.
*   Defining and integrating custom tools (`@tool`).
*   Adding conversational memory (`ConversationBufferMemory`).

**Further Exploration:**
*   Dive deeper into the [LangChain documentation](https://python.langchain.com/).
*   Explore other agent types like [Self-ask with search](https://python.langchain.com/docs/modules/agents/agent_types/self_ask_with_search/) or [Plan and Execute](https://python.langchain.com/docs/modules/agents/agent_types/plan_and_execute/).
*   Connect your agent to real APIs (e.g., a weather API, a real vehicle database).

### Using with MKDocs

This markdown file is ready to be used with [MKDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. Simply add it to the `docs` directory of your MKDocs project and reference it in your `mkdocs.yml` configuration file under the `nav` section.

```yaml
# Example mkdocs.yml snippet
nav:
  - Home: index.md
  - LangChain Lab: langchain_lab.md # Assuming you save this file as docs/langchain_lab.md
```

---




---

## References & Further Reading

*   **Original ReAct Paper:** Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
*   **ReAct Project Page:** [https://react-lm.github.io/](https://react-lm.github.io/)
*   **Google Research Blog Post:** [ReAct: Synergizing Reasoning and Acting in Language Models](https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/)
*   **Prompting Guide (ReAct):**[https://www.promptingguide.ai/techniques/react](https://www.promptingguide.ai/techniques/react)
*   **LangChain Documentation (Agents):** [https://python.langchain.com/docs/modules/agents/](https://python.langchain.com/docs/modules/agents/)

---

