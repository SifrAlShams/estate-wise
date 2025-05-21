from dotenv import load_dotenv
load_dotenv()
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
import time



# mistral_model = 'nv-mistralai/mistral-nemo-12b-instruct'

# llama_model = 'meta/llama-3.3-70b-instruct'

# llm = ChatNVIDIA(model=llama_model)

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key, max_tokens=16000)

# ---------------------------------------------------------
# tool_models = [
#     model for model in ChatNVIDIA.get_available_models() if model.supports_tools
# ]
# print("Tool calling models: ")
# for model in tool_models:
#     print(model.id)
#     print(" ")

#
# start_time = time.time()

# # model = llm.bind_tools([faq_retriever_tool, listings_retriever_tool])
# model = llm
# result = model.invoke("Suggest me a townhouse in Charleston.")

# end_time = time.time()

# print(result.content)
# print(f"Inference Time: {end_time - start_time}")
