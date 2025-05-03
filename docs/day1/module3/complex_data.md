# Day 1 - Module 3: Handling Complex Data Structures

**Objective:** Learn how agents can process, generate, and utilize structured data formats like knowledge graphs and ontologies to represent and reason about complex information.

**Source Code:** [`src/03-complex-data/`](https://github.com/denniszielke/agentic-playground/tree/main/src/03-complex-data){target="_blank"}

---

## Introduction

While LLMs excel at processing natural language, many real-world tasks involve structured information. Agents become more powerful when they can understand and work with data formats that explicitly define relationships and constraints. This module explores how agents can leverage:

1.  **Knowledge Graphs:** Representing entities and their relationships as nodes and edges.
2.  **Ontologies:** Formal specifications of a domain's concepts and relationships (often using standards like OWL).
3.  **Structured Document Parsing:** Extracting specific information from documents (like invoices) based on a predefined schema.

!!! info "Structured Data vs. Unstructured Data"
    LLMs are inherently good at unstructured text. However, combining them with structured data representations like knowledge graphs or ontologies allows for more accurate, consistent, and verifiable reasoning, especially in complex domains.

## 1. Generating Knowledge Graphs

**File:** [`src/03-complex-data/knowledge-graphs.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/03-complex-data/knowledge-graphs.py){target="_blank"}

This script demonstrates using an LLM to generate a knowledge graph from a natural language query, representing the answer as structured data.

**Concept:** Instead of just a text answer, we ask the model to structure its response according to a predefined Python class structure (`KnowledgeGraph`, `Node`, `Edge`) using the `client.beta.chat.completions.parse` feature (a feature allowing direct parsing into Pydantic models).

**Code Breakdown:**

*   **Import Libraries:** `OpenAI`, `pydantic` for data modeling, `graphviz` for visualization.
*   **Define Data Models (Pydantic):**
    *   `Node`: Represents an entity with an ID, label, and color.
    *   `Edge`: Represents a relationship between two nodes (source, target) with a label and color.
    *   `KnowledgeGraph`: Contains lists of nodes and edges, and includes a `visualize` method using `graphviz` to generate an SVG image.

```python
from pydantic import BaseModel, Field
from typing import List
import graphviz

class Node(BaseModel):
    id: int
    label: str
    color: str

class Edge(BaseModel):
    source: int
    target: int
    label: str
    color: str

class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    description: str = None

    def visualize(self):
        # ... (graphviz code to generate SVG from nodes/edges) ...
        dot.render("knowledge_graph", view=False)
```

!!! tip "Pydantic for Structured Output"
    Using Pydantic models along with features like `client.beta.chat.completions.parse` (or similar structured output mechanisms in other libraries) enables the reliable retrieval of JSON or Python objects from the LLM, matching your desired schema.

*   **Define Generation Function (`generate_graph`):**
    *   Takes user input text.
    *   Uses `client.beta.chat.completions.parse`:
        *   Provides the input text within a prompt asking for a knowledge graph representation.
        *   Specifies `response_format = KnowledgeGraph`, instructing the API (or SDK) to return the response directly as a populated `KnowledgeGraph` object.
    *   Returns the parsed `KnowledgeGraph` object.

```python
def generate_graph(input) -> KnowledgeGraph:
    completion = client.beta.chat.completions.parse(
        model=model_name,
        messages = [{"role" : "assistant", "content" : f""" Help me understand the following by describing as a detailed knowledge graph:  {input}"""}],
        response_format = KnowledgeGraph # Key part for structured output
    )
    return completion.choices[0].message.parsed
```

*   **Main Execution:**
    *   Calls `generate_graph` with a complex query about cars, wheels, trains, speed, and friction.
    *   Calls the `visualize()` method on the returned graph object to save the graph as `knowledge_graph.svg`.

```python
graph = generate_graph("What is the relationship between cars, wheels and trains...")
graph.visualize()
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/03-complex-data
# Install pydantic and graphviz if needed: pip install pydantic graphviz
# Ensure graphviz binaries are installed: sudo apt-get update && sudo apt-get install -y graphviz
python knowledge-graphs.py
```

After running, inspect the generated `knowledge_graph.svg` file (you will need to download it or use a browser within the environment if available) to see the visual representation of the model's understanding.

## 2. Creating and Using Ontologies

Ontologies provide a formal way to define the concepts, properties, and relationships within a specific domain. They allow for more rigorous and consistent reasoning.

!!! success "Ontologies vs. Knowledge Graphs"
    While related, ontologies focus on defining the *schema* and rules of a domain (the TBox), while knowledge graphs represent the actual *instances* and relationships (the ABox). Ontologies provide the structure that knowledge graphs can populate.

### Creating an Ontology from Images

**File:** [`src/03-complex-data/create_onthologies.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/03-complex-data/create_onthologies.py){target="_blank"}

This script uses a multimodal model to generate an ontology in the Web Ontology Language (OWL) format based on analyzing images (screenshots of screw types in this case).

**Code Breakdown:**

*   **Client Setup & Image Prep:** Standard client, uses `get_image_data_url` for multiple images (`screen_1.png` to `screen_4.png`).
*   **Detailed System Prompt:** This is crucial. It instructs the model:
    *   To act as an expert in ontology engineering.
    *   To generate an OWL ontology based on the provided images.
    *   To define classes, properties (data/object), terms, descriptions, domains, ranges, and hierarchies based on visual details and numerical values present in the images.
    *   To output *only* the OWL (XML) format.

```python
system_prompt = """
Look at the images below and use them as input. Generate a response based on the images.
You are an expert in ontology engineering. Generate an OWL ontology based on the following domain description:
Define classes, data properties, and object properties...
Provide the output in OWL (XML) format and only output the ontology and nothing else"""
```

*   **API Call:** Sends the system prompt and the multiple image URLs to the model.

```python
response = client.chat.completions.create(
    messages=[
        {
            "role": "user", # Note: Prompt is complex, put in user role content list
            "content": [
                {
                    "type": "text",
                    "text": system_prompt, # The detailed instructions
                },
                # ... multiple image_url parts ...
            ],
        },
    ],
    model=model_name,
)
```

*   **Save Output:** Extracts the OWL content from the response and saves it to `screws.xml`, removing potential markdown formatting.

```python
content_owl = response.choices[0].message.content
with open("screws.xml", "w") as file:
    new_ontology = content_owl.replace("```xml", "").replace("```", "")
    file.write(new_ontology)
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/03-complex-data
# Ensure screen_1.png to screen_4.png exist
python create_onthologies.py
```

Inspect the generated `screws.xml` file. It should contain OWL definitions for different screw types based on the images.

### Using an Ontology to Describe an Image

**File:** [`src/03-complex-data/use-onthology.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/03-complex-data/use-onthology.py){target="_blank"}

This script demonstrates how providing an existing ontology as context can help the model describe an image using the specific terminology and structure defined in that ontology.

**Code Breakdown:**

*   **Client Setup & Image Prep:** Standard client, uses `get_image_data_url` for `reference.png`.
*   **Load Ontology:** Reads the content of the previously generated `screws.xml` file.
*   **Construct Prompt:**
    *   `system` message: Tells the model to use the provided ontology to describe the image.
    *   `user` message content list:
        *   A `text` part containing the *entire content* of the `screws.xml` ontology.
        *   An `image_url` part for `reference.png`.

```python
# Read ontology_content from screws.xml

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that describes images in details. Make use of the onology provided to describe the image.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": ontology_content, # Provide the ontology as context
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("reference.png", "png"),
                    },
                },
            ],
        },
    ],
    model=model_name, # Note: Uses gpt-4o, which is recommended for better ontology understanding
)

print(response.choices[0].message.content)
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/03-complex-data
# Ensure screws.xml and reference.png exist
python use-onthology.py
```

The output should be a description of `reference.png` that attempts to use the classes and properties defined in `screws.xml`.

## 3. Parsing Structured Documents (Invoice Example)

**File:** [`src/03-complex-data/parse_invoice.py`](https://github.com/denniszielke/agentic-playground/blob/main/src/03-complex-data/parse_invoice.py){target="_blank"}

This script uses a multimodal model to extract information from an image of an invoice and populate a predefined XML template (XRechnung format).

**Code Breakdown:**

*   **Download Invoice:** Downloads a sample invoice image (`rechnungsvorlage.jpg`) if it doesn't exist locally.
*   **Client Setup & Image Prep:** Standard client, uses `get_image_data_url` for the downloaded `invoice.jpg`.
*   **Load Template & Explanation:** Reads the target XML structure from `invoice_template.xml` and additional context/instructions from `invoice_explaination.txt`.
*   **Construct System Prompt:** Combines instructions ("extract invoice information... create a XRechnung Beispiel XML...") with the content of the template XML file. This gives the model the target schema.

```python
system_prompt = """
Look at the image attached as input to extract all the invoice information... create a XRechnung Beispiel XML filled with all known values...
"""
# Read invoice_xml_content from invoice_template.xml
system_prompt = system_prompt + invoice_xml_content
# Optionally add content from invoice_explaination.txt
```

*   **API Call:** Sends the combined system prompt and the invoice image URL.

```python
response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract all invoice data from this image.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("invoice.jpg", "jpg"),
                    },
                },
            ],
        },
    ],
    model=model_name,
)
```

*   **Save Output:** Extracts the generated XML from the response and saves it to `invoice_parsed.xml`.

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/03-complex-data
# Install requests if needed: pip install requests
python parse_invoice.py
```

Inspect `invoice_parsed.xml`. Compare it with `invoice_template.xml` and the original `invoice.jpg` to see how well the model extracted the data and filled the structure.

---

!!! abstract "Further Reading & Resources (Knowledge Graphs, Ontologies & LLMs)"

    Dive deeper into using LLMs with structured data:

    *   **Knowledge Graph Construction & Use:**
        *   [How to Build Knowledge Graphs With LLMs (python tutorial) (YouTube)](https://www.youtube.com/watch?v=tcHIDCGu6Yw){target="_blank"}
        *   [Constructing Knowledge Graphs From Unstructured Text Using LLMs (Neo4j Blog)](https://neo4j.com/blog/developer/construct-knowledge-graphs-unstructured-text/){target="_blank"}
        *   [Building Knowledge Graphs Using Python (Medium)](https://medium.com/@zulqarnain.shahid.iqbal/building-knowledge-graphs-using-python-821a71254aed){target="_blank"}
        *   [Automated Knowledge Graph Construction with Large Language Models (Medium)](https://medium.com/@researchgraph/automated-knowledge-graph-construction-with-large-language-models-150512d1bc22){target="_blank"}
        *   [llmgraph: Create knowledge graphs with LLMs (GitHub)](https://github.com/dylanhogg/llmgraph){target="_blank"}
    *   **Integrating KGs/Ontologies with LLMs:**
        *   [Unifying LLMs & Knowledge Graphs for GenAI: Use Cases & Best Practices (Neo4j Blog)](https://neo4j.com/blog/genai/unifying-llm-knowledge-graph/){target="_blank"}
        *   [How to Implement Knowledge Graphs and Large Language Models (LLMs) Together (Towards Data Science)](https://towardsdatascience.com/how-to-implement-knowledge-graphs-and-large-language-models-llms-together-at-the-enterprise-level-cf2835475c47/){target="_blank"}
        *   [Grounding Large Language Models with Knowledge Graphs (DataWalk)](https://datawalk.com/grounding-large-language-models-with-knowledge-graphs/){target="_blank"}
        *   [Using a Knowledge Graph to Implement a RAG Application (DataCamp Tutorial)](https://www.datacamp.com/tutorial/knowledge-graph-rag){target="_blank"}
        *   [Integrating Large Language Models and Knowledge Graphs (PDF Tutorial - Academic)](https://www.cs.emory.edu/~jyang71/files/klm-tutorial.pdf){target="_blank"}
    *   **Resource Collections:**
        *   [Knowledge Graph Tutorials and Papers (LLM Section) (GitHub)](https://github.com/heathersherry/Knowledge-Graph-Tutorials-and-Papers/blob/master/topics/Knowledge%20Graph%20and%20LLMs.md){target="_blank"}

---

This concludes Day 1, covering foundational interactions, multimodal inputs, and handling structured data. Day 2 will build on this by exploring how to give agents tools to solve more complex problems and implement basic autonomous agent patterns.

