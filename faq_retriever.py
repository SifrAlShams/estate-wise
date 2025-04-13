import json
import time
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from utils.embedding_model import hf_embeddings


# load locally saved FAISS
faiss_vectordb = FAISS.load_local(
    "faq_vector_db", hf_embeddings, allow_dangerous_deserialization=True
)

faq_vdb_retriever = faiss_vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 3,"score_threshold": 0.8})


# if __name__ == "__main__":
#     # -----------------------------------------------------#

#     query = "where is your head office?"
#     # # vectordb similarity search
#     start_time = time.time()
    
#     results = faiss_vectordb.similarity_search(
#         query,
#         k=2,
#     )
    
#     end_time = time.time()
    
#     print(f"Time taken for retrieval: {end_time - start_time}")
    
#     for res in results:
#         print("Page Content: ")
#         print(res.page_content)
#         print("Metadata: ")
#         print(res.metadata)
    
    
    # vectordb as retriever
    # response = faq_vdb_retriever.invoke(query)
    # print(response, type(response))
    # for retrieved_doc in response:
    #     print(retrieved_doc.metadata)
    #     print(retrieved_doc.page_content)