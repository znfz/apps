# client.py (diagnostic only)
import os
from openai import OpenAI
import httpx

def get_client():
    insecure_client = httpx.Client(verify=False, timeout=30.0, trust_env=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key, http_client=insecure_client)