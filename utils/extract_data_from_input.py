import json

from langchain_core.output_parsers import StrOutputParser

from prompts.agent_prompts import extract_prompt
from utils.models.import_llm import llm


def extract(user_input):
    prompt = extract_prompt
    model = llm
    extract_email_chain = prompt | model | StrOutputParser()

    agent_response = extract_email_chain.invoke({"input_string": user_input})

    if agent_response.startswith("```json") and agent_response.endswith("```"):
        agent_response = agent_response[7:-3].strip()

    try:
        agent_response = json.loads(agent_response)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Invalid JSON:", repr(agent_response))

    return agent_response
