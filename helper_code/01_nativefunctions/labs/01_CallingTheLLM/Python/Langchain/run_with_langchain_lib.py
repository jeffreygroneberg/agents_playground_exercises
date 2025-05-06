import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o"

chat = ChatOpenAI(
    openai_api_key=token,
    openai_api_base=endpoint,
    model=model_name,
    temperature=1.0,
    max_tokens=1000
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is the capital of Germany?")
]

response = chat.invoke(messages)

print(response.content)