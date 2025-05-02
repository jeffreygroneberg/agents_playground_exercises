# Day 1 - Module 2: Working with Multimodal Models

**Objective:** Understand how AI agents can perceive and reason about non-textual data like images and voice, using multimodal LLMs.

**Source Code:** `/home/ubuntu/agentic-playground/src/02-multimodal-models/`

---

## Introduction

Humans perceive the world through multiple senses: sight, sound, touch, etc. To create truly intelligent agents, we need models that can also process information beyond just text. Multimodal models are designed to handle various input types, such as images and audio, alongside text.

In this module, we will explore:

1.  **Vision Capabilities:** How to provide images to an LLM and ask questions about them (e.g., describing content, comparing images).
2.  **Voice Interaction (Conceptual):** Understanding the components involved in creating a voice-based agent that can listen and speak in real-time (using the provided `voice-agent.py` and `voice-interaction` app as examples).

**Note:** The voice interaction examples might require specific Azure credentials or setup beyond the basic GitHub PAT, as indicated in the `voice-agent.py` code (referencing Azure OpenAI endpoints and deployments). We will focus on the concepts and code structure.

## 1. Vision: Inspecting and Comparing Images

Modern LLMs like GPT-4o (and its mini version used here) can directly process images provided within the prompt.

**Helper Function (`get_image_data_url`):**
Both `inspect-image.py` and `compare-images.py` use a helper function (defined in the scripts, but conceptually similar to one potentially in `utils.py` or `imagelibrary.py`) to convert local image files into base64-encoded data URLs. This format allows embedding the image directly into the API request.

```python
import base64

def get_image_data_url(image_file: str, image_format: str) -> str:
    # ... (opens file, reads bytes, encodes to base64) ...
    return f"data:image/{image_format};base64,{image_data}"
```

**(Optional) Image Library:** The code also imports `imagelibrary.VectorDatabase` and calls `database.download_images()`. This seems related to fetching example images (`f1_car_url_1.jpg`, `f1_car_url_2.jpg`) used in the scripts, potentially from an online source if they don't exist locally. For the workshop, ensure these images are available in the execution directory.

### Inspecting a Single Image

**File:** `src/02-multimodal-models/inspect-image.py`

This script sends a single image to the model and asks it to describe the content.

**Code Breakdown:**

*   **Client Setup:** Standard OpenAI client initialization.
*   **Prepare Image:** Get the data URL for the image (`f1_car_url_1.jpg`).
*   **Construct the Prompt:**
    *   The `user` message content is now a *list* containing multiple parts:
        *   A `text` part with the question ("What's in this image?").
        *   An `image_url` part containing the image data URL. The `detail` parameter can be used to control quality vs. cost/latency (not applicable to `gpt-4o-mini` as per current GitHub Models docs, but good practice).

```python
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
                    "text": "What's in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("f1_car_url_1.jpg", "jpg"),
                        # "detail": "low" # Optional detail parameter
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/02-multimodal-models
# Ensure f1_car_url_1.jpg exists (may be downloaded by imagelibrary.py)
python inspect-image.py
```

The output will be the model's textual description of the F1 car image.

### Comparing Multiple Images

**File:** `src/02-multimodal-models/compare-images.py`

This script sends *two* images to the model and asks it to compare them.

**Code Breakdown:**

*   **Client Setup & Image Prep:** Similar to inspecting, but get data URLs for both images (`f1_car_url_1.jpg`, `f1_car_url_2.jpg`).
*   **Construct the Prompt:**
    *   The `user` message content list now includes the text prompt and *two* `image_url` parts.
    *   The text prompt explicitly asks the model to compare the images and list differences.

```python
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
                    "text": "Look at these two pictures. Image 1 and Image 2. Are they similar List all the differences according to category, color, position and size.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("f1_car_url_1.jpg", "jpg"),
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("f1_car_url_2.jpg", "jpg"),
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)
```

**To Run:**

```bash
cd /home/ubuntu/agentic-playground/src/02-multimodal-models
# Ensure f1_car_url_1.jpg and f1_car_url_2.jpg exist
python compare-images.py
```

The output will be the model's comparison of the two F1 car images, highlighting their differences.

## 2. Voice Interaction (Conceptual Overview)

**Files:**
*   `src/02-multimodal-models/voice-agent.py`
*   `src/02-multimodal-models/voice-interaction/` (Flask app)

These examples demonstrate a more complex scenario: a real-time voice conversation with an agent. This involves several components working together:

1.  **Audio Input:** Capturing audio from the user's microphone.
2.  **Speech-to-Text (STT):** Converting the user's speech into text.
3.  **LLM Processing:** Sending the text (and potentially conversation history) to the LLM, possibly using tools.
4.  **Text-to-Speech (TTS):** Converting the LLM's text response back into audio.
5.  **Audio Output:** Playing the generated audio back to the user.
6.  **Turn Detection:** Determining when the user has finished speaking and when the agent should respond (Voice Activity Detection - VAD).

**Code Structure (`voice-agent.py`):**

*   **Dependencies:** Uses `semantic-kernel[realtime]`, `pyaudio`, `sounddevice`, `pydub`, indicating reliance on Semantic Kernel's real-time capabilities and audio libraries.
*   **Audio Handling:** Uses `AudioPlayerWebRTC` and `AudioRecorderWebRTC` (from `utils.py`) likely for handling audio input/output streams, potentially via WebRTC for web applications.
*   **Realtime Agent:** Leverages `OpenAIRealtimeWebRTC` from Semantic Kernel, which seems to orchestrate the STT, LLM interaction, and TTS pipeline, likely using a specialized real-time API endpoint (indicated by the Azure endpoint/deployment variables).
*   **Settings:** Configures `OpenAIRealtimeExecutionSettings` including:
    *   `instructions`: The system prompt for the agent.
    *   `voice`: Specifies the TTS voice.
    *   `turn_detection`: Configures server-side VAD to automatically manage conversation turns.
    *   `function_choice_behavior`: Enables tool calling within the voice conversation.
*   **Tools:** Defines helper functions (`get_weather`, `get_date_time`, `goodbye`) using `@kernel_function` decorator, making them available as tools to the voice agent.
*   **Asynchronous Flow:** Uses `asyncio` to manage the concurrent tasks of recording, processing, and playing audio.
*   **Event Loop:** The main loop (`async for event in realtime_agent.receive(...)`) processes events from the real-time service, including transcribed text (`RealtimeTextEvent`) and other service events (`ListenEvents`).

**Flask App (`voice-interaction/app.py`):**
This appears to be a web interface (likely using Flask and WebSockets) that interacts with the backend logic (potentially `voice-agent.py` concepts or the `rtmt.py` module mentioned in the file structure) to provide a web-based voice chat experience.

**Key Concepts for Workshop:**

*   Explain the pipeline: Mic -> STT -> LLM -> TTS -> Speaker.
*   Discuss the importance of low latency for a natural conversation.
*   Highlight the role of VAD/Turn Detection.
*   Show how tools can be integrated into a voice conversation.
*   Mention that real-time voice often requires specialized APIs and infrastructure (like the Azure endpoint referenced).

**Running the Voice Demo (Caution):**
Running `python voice-interaction/app.py` might require:
*   Specific Azure credentials set as environment variables (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_VOICE_COMPLETION_DEPLOYMENT_NAME`, `AZURE_VOICE_COMPLETION_MODEL`).
*   Installation of additional audio dependencies (`pip install pyaudio sounddevice pydub semantic-kernel[realtime]`).
*   Correct audio device configuration.

Due to these complexities, it might be best to treat this as a code walkthrough and conceptual explanation unless the workshop environment is specifically prepared for Azure voice services.

---

## Hands-on Exercise Ideas (Module 2)

1.  **Modify `inspect-image.py`:**
    *   Use a different image (find one online, save it, and update the filename).
    *   Change the text prompt to ask a different question about the image (e.g., "What is the main color in this image?", "Are there any people in this picture?").
2.  **Modify `compare-images.py`:**
    *   Use two different images.
    *   Change the prompt to focus on similarities instead of differences.
3.  **(Conceptual)** Discuss how you would modify the `tool-calling.py` example from Module 1 to *describe* an image instead of getting the time. What would the tool definition look like? (Hint: The "tool" is now built into the model itself via the `image_url` input).

---

This module explored how agents can interact with visual and auditory information. The next module will delve into handling complex, structured data formats like knowledge graphs and ontologies.
