from langchain.tools import Tool

from datetime import datetime, timedelta

import pytz

from faq_retriever import faq_vdb_retriever



def custom_retriever_tool(query: str):
    retrieved_docs = faq_vdb_retriever.invoke(query)

    if not retrieved_docs:
        return {"documents": [], "metadata": "No relevant documents found."}

    metadata_list = []
    docs_list = []

    for doc in retrieved_docs:
        text = doc.page_content
        source = doc.metadata
        docs_list.append(text)
        metadata_list.append(source)

    return {"documents": docs_list, "metadata": metadata_list}



faq_retriever_tool = Tool(
    name="faq_retriever",
    description="Retrieve FAQ chunks.",
    func=custom_retriever_tool
)

