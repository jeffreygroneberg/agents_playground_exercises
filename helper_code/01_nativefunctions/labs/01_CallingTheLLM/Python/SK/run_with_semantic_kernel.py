import asyncio
import logging
import openai
import os
from dotenv import load_dotenv

import semantic_kernel.connectors.ai.open_ai
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging

load_dotenv()
# Set the logging level for  semantic_kernel.kernel to DEBUG.
setup_logging()
logging.getLogger("kernel").setLevel(logging.DEBUG)

kernel = Kernel()

token = os.environ["GITHUB_TOKEN"]
model_name = "openai/gpt-4o"

chat_client = openai.AsyncOpenAI(
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.inference.ai.azure.com")

chat = semantic_kernel.connectors.ai.open_ai.OpenAIChatCompletion(
    ai_model_id="gpt-4o",
    async_client=chat_client)

prompt = "What is the capital of France?"
kernel.add_service(
    chat
)

async def main():
    response = await kernel.invoke_prompt(prompt)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
