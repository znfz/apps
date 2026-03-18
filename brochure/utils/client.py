import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

def get_client():
    env_path = find_dotenv()
    if not env_path:
        raise FileNotFoundError("Could not find a .env file. Check your working directory.")
    load_dotenv(override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Export it before running.")
    return OpenAI(api_key=api_key)