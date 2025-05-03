# Day 1 - Module 2: Exercises

These exercises are based on the concepts and code presented in Module 2: Working with Multimodal Models (`src/02-multimodal-models/`).

## Exercise 2.1: Describing a Different Image

**Goal:** Practice using the vision model to analyze a new image and answer a specific question.

1.  Find an image online (e.g., a picture of a cat, a landscape, a famous landmark). Save it to the `src/02-multimodal-models/` directory (e.g., as `my_image.jpg`).
2.  Open the `src/02-multimodal-models/inspect-image.py` script.
3.  Modify the script to use your new image file:
    *   Update the filename in the `get_image_data_url` call (e.g., `get_image_data_url("my_image.jpg", "jpg")`). Make sure the format ("jpg", "png", etc.) matches your image.
4.  Modify the `text` part of the user prompt to ask a specific question about your image (e.g., "What is the main animal in this image?", "What time of day does it look like in this picture?", "Describe the building in this image.").
5.  Run the script (`python inspect-image.py`) and observe the model's description based on your question and image.

## Exercise 2.2: Comparing Different Images for Similarities

**Goal:** Practice using the vision model to compare two different images, focusing on similarities.

1.  Find two images online that have some similarities but also differences (e.g., two different types of dogs, two different models of cars, two different chairs). Save them to the `src/02-multimodal-models/` directory (e.g., `image_A.png`, `image_B.png`).
2.  Open the `src/02-multimodal-models/compare-images.py` script.
3.  Modify the script to use your two new images:
    *   Update the filenames and formats in the two `get_image_data_url` calls.
4.  Modify the `text` part of the user prompt to ask the model to focus on the *similarities* between the two images (e.g., "Look at these two images. What features do they have in common?").
5.  Run the script (`python compare-images.py`) and analyze the model's response highlighting the similarities.

## Exercise 2.3 (Conceptual): Image Input as a "Tool"

**Goal:** Think about how multimodal input relates to the concept of tool calling.

Multimodal models can process different types of input, like text and images, simultaneously. This capability can be conceptually compared to having built-in tools for understanding different data modalities, as illustrated below:

![Multimodal Concept](../../assets/images/concepts_multimodal.png)

1.  Review the `tool-calling.py` script from Module 1, where an external `get_current_time` function was defined and called.
2.  Review the `inspect-image.py` script from Module 2, where an image is provided directly in the prompt using `image_url`.
3.  Discuss: In the context of `inspect-image.py`, could you consider the ability to process the `image_url` as a built-in "tool" of the multimodal model itself? Why or why not?
4.  How does providing the image directly differ from defining an external function like `describe_image_from_url(url: str)` that the LLM would have to explicitly call?
