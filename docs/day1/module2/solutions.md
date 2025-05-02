# Day 1 - Module 2: Solutions

These are the solutions or discussion points for the exercises in Module 2.

## Solution 2.1: Describing a Different Image

Assuming you saved an image as `my_image.jpg` in the `src/02-multimodal-models/` directory and wanted to ask "What is the main animal in this image?", you would modify `src/02-multimodal-models/inspect-image.py` like this:

```python
import os
from openai import OpenAI
from dotenv import load_dotenv
import base64

# Assuming imagelibrary.py or similar is not strictly needed if image exists
# from imagelibrary import VectorDatabase

load_dotenv()

# Helper function (include if not imported)
def get_image_data_url(image_file: str, image_format: str) -> str:
    if not os.path.exists(image_file):
        # Attempt to download if using imagelibrary, otherwise raise error
        # database = VectorDatabase()
        # database.download_images()
        # if not os.path.exists(image_file):
        raise FileNotFoundError(f"Image file not found: {image_file}")

    with open(image_file, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{image_format};base64,{image_data}"

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

model_name = "gpt-4o-mini"

# --- Modified Section --- 
image_filename = "my_image.jpg" # Your image filename
image_format = "jpg" # Your image format
user_question = "What is the main animal in this image?" # Your question
# ----------------------

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that describes images in details.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_question, # Use the variable
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url(image_filename, image_format), # Use variables
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)

```

**Expected Output:** The model should provide a textual answer specifically addressing your question about the content of `my_image.jpg`.

## Solution 2.2: Comparing Different Images for Similarities

Assuming you saved two images as `image_A.png` and `image_B.png` in the `src/02-multimodal-models/` directory, you would modify `src/02-multimodal-models/compare-images.py` like this:

```python
import os
from openai import OpenAI
from dotenv import load_dotenv
import base64

# Assuming imagelibrary.py or similar is not strictly needed if images exist
# from imagelibrary import VectorDatabase

load_dotenv()

# Helper function (include if not imported)
def get_image_data_url(image_file: str, image_format: str) -> str:
    if not os.path.exists(image_file):
        # Attempt to download if using imagelibrary, otherwise raise error
        # database = VectorDatabase()
        # database.download_images()
        # if not os.path.exists(image_file):
        raise FileNotFoundError(f"Image file not found: {image_file}")

    with open(image_file, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{image_format};base64,{image_data}"

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

model_name = "gpt-4o-mini"

# --- Modified Section --- 
image_1_filename = "image_A.png" # Your first image
image_1_format = "png"
image_2_filename = "image_B.png" # Your second image
image_2_format = "png"
user_question = "Look at these two images. What features do they have in common?" # Focus on similarities
# ----------------------

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that describes and compares images in detail.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_question, # Use the variable
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url(image_1_filename, image_1_format), # Use variables
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url(image_2_filename, image_2_format), # Use variables
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)

```

**Expected Output:** The model should provide a textual response focusing on the common features or characteristics shared by `image_A.png` and `image_B.png`.

## Solution 2.3 (Conceptual): Image Input as a "Tool"

This is a discussion point rather than a coding solution.

*   **Is image processing a built-in "tool"?**
    *   Yes, in a conceptual sense. For multimodal models like GPT-4o, the ability to process image data provided via `image_url` is an inherent capability, much like processing text. You don't need to define an external function for it; the model handles it internally.
    *   It functions *like* a tool because it extends the model's capabilities beyond pure text, allowing it to access and reason about visual information to answer the user's query.

*   **How does it differ from an external function call?**
    *   **Integration:** Image processing via `image_url` is deeply integrated into the model's architecture. An external function (`describe_image_from_url(url: str)`) requires an explicit multi-step process (LLM requests tool -> Code executes tool -> Code sends result back -> LLM uses result), similar to the `get_current_time` example.
    *   **Data Transfer:** Providing the image via `image_url` (especially as a base64 data URL) sends the image data directly to the model endpoint in the *same* API call as the text prompt. An external function would likely involve the code fetching the image from the URL, processing it (perhaps with a separate vision model or library), and sending only the resulting *text description* back to the LLM in a *subsequent* API call.
    *   **Richness of Information:** The built-in capability allows the LLM to directly access the rich visual features of the image. An external tool returning only a text description might lose nuances that the LLM could have perceived if it processed the image directly.

In essence, multimodal input is a more tightly integrated form of capability extension compared to the explicit request-execute-respond cycle of external tool calling.
