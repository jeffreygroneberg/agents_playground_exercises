import os
import asyncio
import requests
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Plugin definition


class CurrencyPlugin:
    @kernel_function
    def get_exchange_rate(self, currency: str) -> str:
        """
        Fetches the current exchange rate for a given currency against USD."""

        print("In exchange rate function")
        url = "https://open.er-api.com/v6/latest/USD"
        print(f"Fetching exchange rate for {currency.upper()}...")
        response = requests.get(url)
        data = response.json()
        rate = data["rates"].get(currency.upper())
        if rate:
            return f"1 USD is equal to {rate} {currency.upper()} right now."
        return f"Currency '{currency}' not found."


# Kernel and service initialization
def create_kernel() -> Kernel:
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o"

    chat_client = AsyncOpenAI(api_key=token, base_url=endpoint)
    chat_service = OpenAIChatCompletion(
        ai_model_id=model_name,
        async_client=chat_client, api_key=token, service_id="chatgpt",
    )

    kernel = Kernel()
    kernel.add_service(chat_service)
    kernel.add_plugin(CurrencyPlugin(), plugin_name="CurrencyPlugin")

    return kernel

# Main execution logic


async def main():
    kernel = create_kernel()

    arguments = KernelArguments(
        settings=PromptExecutionSettings(

            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )
    )

    query = "What is the current exchange rate for Russian Currency?"

    response = await kernel.invoke_prompt(query, arguments=arguments)
    print("Assistant response:", response)

if __name__ == "__main__":
    asyncio.run(main())