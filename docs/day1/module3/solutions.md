# Day 1 - Module 3: Solutions

These are the solutions or discussion points for the exercises in Module 3.

## Solution 3.1: Generating a Different Knowledge Graph

Modify `src/03-complex-data/knowledge-graphs.py`:

```python
# ... (imports, class definitions, generate_graph function remain the same) ...

if __name__ == "__main__":
    # --- Modified Input Query --- 
    input_text = "Explain the main components of a simple web application: browser, web server, database, and how they interact."
    # --------------------------
    
    graph = generate_graph(input_text)
    graph.visualize()
    print("Knowledge graph generated and saved as knowledge_graph.svg")

```

**Expected Output:**
*   The script should run without errors (assuming `graphviz` is installed).
*   A file named `knowledge_graph.svg` will be created in the `src/03-complex-data/` directory.
*   Opening `knowledge_graph.svg` should display a graph with nodes representing "Browser", "Web Server", "Database" (and related concepts like "HTTP Request", "SQL Query", "HTML/CSS/JS") and edges showing the interactions (e.g., Browser sends Request to Web Server, Web Server queries Database, Database returns data to Web Server, Web Server sends Response to Browser).

## Solution 3.2: Using the Ontology with an Irrelevant Image

Modify `src/03-complex-data/use-onthology.py`:

```python
# ... (imports, get_image_data_url, client setup remain the same) ...

# Load ontology
ontology_file = "screws.xml"
if not os.path.exists(ontology_file):
    raise FileNotFoundError(f"Ontology file not found: {ontology_file}. Run create_onthologies.py first.")
with open(ontology_file, "r") as file:
    ontology_content = file.read()

# --- Modified Image --- 
image_filename = "battery_1.png" # Changed image
image_format = "png"
# ----------------------

image_data_url = get_image_data_url(image_filename, image_format)

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
                    "text": ontology_content,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url, # Use variable
                    },
                },
            ],
        },
    ],
    model="gpt-4o", # Using gpt-4o as in the original script
)

print(response.choices[0].message.content)

```

**Expected Output:**
The model's output can vary depending on its interpretation. Possible outcomes include:
*   Correctly identify the image as a battery but then awkwardly try to apply screw-related terms from the ontology (e.g., "This battery has a cylindrical head type...").
*   Ignore the ontology entirely and just describe the battery.
*   Explicitly state that the provided ontology is not relevant to the image content.

**Discussion Point:** This demonstrates that while providing context (like an ontology) can guide the LLM, the context *must be relevant* to the task and input. Providing irrelevant context can confuse the model or lead to incorrect/nonsensical outputs. The LLM doesn't inherently *know* the ontology only applies to screws; it tries to follow instructions, even if the combination doesn't logically fit.

## Solution 3.3: Evaluating Invoice Parsing Accuracy

This exercise requires manual comparison and discussion. There is no single code solution.

**Steps for Evaluation:**

1.  **Open `invoice.jpg`:** Use an image viewer.
2.  **Open `invoice_parsed.xml`:** Use a text editor or XML viewer.
3.  **Compare Field by Field:** Go through the XML structure and find the corresponding information on the image.

**Example Findings (Hypothetical - actual results may vary):**

*   **Examples of Correct Extraction:** Fields like Invoice Number, Issue Date, Sender Name/Address, Recipient Name/Address, and Total Amount are generally extracted correctly.
*   **Incorrect:** A specific line item quantity is misread (e.g., '1' read as 'l'), a date format is misinterpreted, or a complex address line is split incorrectly.
*   **Missed:** A secondary contact person or a specific payment term mentioned in small print can be missed.
*   **Hallucinated:** The model invents a field value if it's unsure or if the template expects a field not clearly present (this is less common).

**Discussion Points:**
*   **Image Quality:** Was the `invoice.jpg` clear? OCR (Optical Character Recognition), which the multimodal model performs internally, is sensitive to image resolution, rotation, lighting, and font type.
*   **Layout Complexity:** Was the invoice layout standard or unusual? Non-standard layouts make it harder for the model to associate labels with values.
*   **Template Matching:** How well did the model map the visual information to the specific XML structure of the XRechnung template? Did it understand the semantic meaning of each XML tag?
*   **Model Limitations:** Even advanced models aren't perfect. Complex tables, overlapping text, or ambiguous fields can lead to errors.
*   **Confidence:** The model doesn't usually provide a confidence score for each extracted field, making it hard to know which values are reliable without manual verification.
*   **Improvement:** How could accuracy be improved? (e.g., Higher resolution image, pre-processing the image, providing more detailed instructions/examples in the prompt, using a model specifically fine-tuned for document extraction, using zonal OCR if field locations are fixed).
