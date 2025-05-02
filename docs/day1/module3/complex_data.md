# Day 1 - Module 3: Handling Complex Data Structures

**Objective:** Learn how agents can process, generate, and utilize structured data formats like knowledge graphs and ontologies to represent and reason about complex information.

**Source Code:** `/home/ubuntu/agentic-playground/src/03-complex-data/`

---

## Introduction

While LLMs excel at processing natural language, many real-world tasks involve structured information. Agents become more powerful when they can understand and work with data formats that explicitly define relationships and constraints. This module explores how agents can leverage:

1.  **Knowledge Graphs:** Representing entities and their relationships as nodes and edges.
2.  **Ontologies:** Formal specifications of a domain's concepts and relationships (often using standards like OWL).
3.  **Structured Document Parsing:** Extracting specific information from documents (like invoices) based on a predefined schema.

## 1. Generating Knowledge Graphs

**File:** `src/03-complex-data/knowledge-graphs.py`

This script demonstrates using an LLM to generate a knowledge graph from a natural language query, representing the answer as structured data.

**Concept:** Instead of just a text answer, we ask the model to structure its response according to a predefined Python class structure (`KnowledgeGraph`, `Node`, `Edge`) using the `client.beta.chat.completions.parse` feature (which seems specific to this SDK version or a helper library, allowing direct parsing into Pydantic models).

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

After running, inspect the generated `knowledge_graph.svg` file (you might need to download it or use a browser within the environment if available) to see the visual representation of the model's understanding.

## 2. Creating and Using Ontologies

Ontologies provide a formal way to define the concepts, properties, and relationships within a specific domain. They allow for more rigorous and consistent reasoning.

### Creating an Ontology from Images

**File:** `src/03-complex-data/create_onthologies.py`

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

**File:** `src/03-complex-data/use-onthology.py`

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
    model=model_name, # Note: Uses gpt-4o, might be needed for better ontology understanding
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

**File:** `src/03-complex-data/parse_invoice.py`

This script uses a multimodal model to extract information from an image of an invoice and populate a predefined XML template (XRechnung format).

**Code Breakdown:**

*   **Download Invoice:** Downloads a sample invoice image (`rechnungsvorlage.jpg`) if it doesn't exist locally.
*   **Client Setup & Image Prep:** Standard client, uses `get_image_data_url` for the downloaded `invoice.jpg`.
*   **Load Template & Explanation:** Reads the target XML structure from `invoice_template.xml` and potentially additional context/instructions from `invoice_explaination.txt`.
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

## Hands-on Exercise Ideas (Module 3)

1.  **Modify `knowledge-graphs.py`:** Change the input query to generate a graph about a different topic (e.g., "Explain the components of a simple web application: browser, web server, database"). Visualize the result.
2.  **Modify `use-onthology.py`:** Provide a different image (e.g., `battery_1.png` or `battery_2.png` from the same folder) and see how the model describes it using the `screws.xml` ontology (it might struggle if the image isn't a screw, highlighting the importance of relevant context).
3.  **Examine `invoice_parsed.xml`:** Carefully compare the extracted data in `invoice_parsed.xml` against the original `invoice.jpg`. Identify any fields the model missed or extracted incorrectly. Discuss why this might happen (e.g., image quality, complex layout, ambiguity).

---

This concludes Day 1, covering foundational interactions, multimodal inputs, and handling structured data. Day 2 will build on this by exploring how to give agents tools to solve more complex problems and implement basic autonomous agent patterns.
