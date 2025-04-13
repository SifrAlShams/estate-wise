from langchain_huggingface import HuggingFaceEmbeddings


model_name = "all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
hf_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)


# if __name__ == "__main__":
#     embedding_vector_len = len(hf_embeddings.embed_query("test string"))
#     print(f"Embedding Model: {model_name}")
#     print(f"Embedding dimension: {embedding_vector_len}")