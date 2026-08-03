from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import json
import os

load_dotenv()   



def get_openai_llm():
    return init_chat_model("openai:gpt-4o-mini", temperature=0, stream_usage=True)

