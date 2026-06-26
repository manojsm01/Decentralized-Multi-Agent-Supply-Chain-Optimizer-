import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable not set")
    
    return ChatNVIDIA(
        model="meta/llama-3.1-70b-instruct",
        nvidia_api_key=api_key,
        temperature=0.2,
        max_retries=0,
        timeout=10
    )
