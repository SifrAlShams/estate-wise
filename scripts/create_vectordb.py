import sys
import os

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path)) 

# Add project root to sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import json
import time
from uuid import uuid4

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from langchain_core.documents import Document

from utils.embedding_model import hf_embeddings, model_name
from utils.chunking import text_splitter



embedding_vector_len = len(hf_embeddings.embed_query("test string"))
print(f"Embedding Model: {model_name}")
print(f"Embedding length: {embedding_vector_len}")

index = faiss.IndexFlatL2(embedding_vector_len)
print(f"FAISS Index Created: {index}")


vector_store = FAISS(
    embedding_function=hf_embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


# read documents from json
with open("../datafiles/cleaned_output.json", "r") as json_file:
    faqs_list = json.load(json_file)

print(f"Data file read.")


documents = []

for page in faqs_list:
    page_chunks_as_doc = text_splitter.create_documents([page['content']])
    page_chunks_as_txt = [chunk.page_content for chunk in page_chunks_as_doc]
    for page_chunk in page_chunks_as_txt:
        page_chunk_doc = Document(
            page_content=page_chunk,
            metadata={"title": page['title'], "description": page['description'], "source": page['url']}
        )
        documents.append(page_chunk_doc)



print(f"No. of Docs in FAQs: {len(documents)}")
# for doc in documents:
#     print(doc.page_content)
#     print(doc.metadata)
#     print(" ")

# # make vector_db
start_time = time.time()
uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store.add_documents(documents=documents, ids=uuids)

# # save locally
vector_store.save_local("../faq_vector_db")
end_time = time.time()

print(f"Time to create FAISS vectordb for FAQs: {end_time - start_time}")
