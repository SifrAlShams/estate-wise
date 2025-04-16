import json
import time
from uuid import uuid4

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from langchain_core.documents import Document

from utils.embedding_model import hf_embeddings, model_name



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


with open('../datafiles/listings.json', 'r', encoding='utf-8') as f:
    listings = json.load(f)

print(f"Total No. of listings: {len(listings)}")


documents = []
for listing in listings:
    listing_doc = Document(
        page_content=str(listing),
        metadata={"type": listing["type"], "city": listing["city"]}
    )
    documents.append(listing_doc)

print(f"No. of Docs in Listings: {len(documents)}")
# for doc in documents:
#     print(doc.page_content)
#     print(doc.metadata)
#     print(" ")

# # make vector_db
start_time = time.time()
uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store.add_documents(documents=documents, ids=uuids)

# # save locally
vector_store.save_local("../listings_vector_db")
end_time = time.time()

print(f"Time to create FAISS vectordb for Listings: {end_time - start_time}")
