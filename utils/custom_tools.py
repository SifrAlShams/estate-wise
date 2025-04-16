from langchain.tools import Tool
from faq_retriever import faq_vdb_retriever
from listings_retriever import listings_retriever



def faq_retriever_tool(query: str):
    """This tool is called when user query is about FAQs."""
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


def listings_retriever_tool(query: str):
    """This is a tool called when user query is about property."""
    retrieved_docs = listings_retriever.invoke(query)

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
    func=faq_retriever_tool
)

property_listings_retriever_tool = Tool(
    name="listings_retriever",
    description="Retrieve property listings.",
    func=listings_retriever_tool
)