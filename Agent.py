import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

LLM = ChatOpenAI(
    model=os.getenv("KAIZEN_MODEL"),
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=1,
    top_p=1,
    max_completion_tokens=16384,
)

if __name__ == "__main__":
    print(LLM.invoke("hi"))
