from typing import Annotated, Sequence

from langgraph.errors import GraphRecursionError
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode

from langgraph.checkpoint.memory import MemorySaver

import time

from utils.model import llm
from prompts.agent_prompts import intent_system_msg, chatbot_system_msg
from utils.custom_tools import faq_retriever_tool, listings_retriever_tool


tools = [faq_retriever_tool, listings_retriever_tool]


#### Agent Class
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_input: Annotated[list[str], add_messages]
    use_case: Annotated[list[str], add_messages]

#### Nodes
def intent_classification(state: AgentState):
    print("---EXTRACT INTENT---")
    system_message = intent_system_msg
    messages = state["messages"]
    state["user_input"].append(messages[-1].content)

    model = llm
    model_response = model.invoke([system_message] + list(messages))

    # Clean and normalize the model response
    intent_response = model_response.content.strip().lower().strip("''").strip('"')

    valid_intents = ["general", "listings", "faq"]
    intent = intent_response if intent_response in valid_intents else "general"
    print(f"Extracted intent: {intent}")
    state['use_case'].append(intent)

    return intent


def agent(state: AgentState):
    print(f"---AGENT Called for USE CASE: {state['use_case']}---")

    agent_system_msg = chatbot_system_msg

    messages = state["messages"]
    model = llm.bind_tools(tools)

    agent_response = model.invoke([agent_system_msg] + list(messages))

    return {"messages": [agent_response]}


def generate(state: AgentState):
    pass



#### Graph Compilation
workflow = StateGraph(AgentState)

# add nodes
tool_node_object = ToolNode(tools)
workflow.add_node("tools-node", tool_node_object)
workflow.add_node("agent-node", agent)
workflow.add_node("generate-node", generate)

# add edges
workflow.add_conditional_edges(
    START,
    intent_classification,
    {
        "general": "generate-node",
        "listings": "agent-node",
        "faq": "agent-node",
    }
)

workflow.add_conditional_edges(
    "agent-node",
    tools_condition,
    {
        "tools": "tools-node",
        END: "generate-node"
    }
)
workflow.add_edge("generate-node", END)
workflow.add_edge("tools-node", "agent-node")


checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)


try:
    image_bytes = graph.get_graph().draw_mermaid_png()
    with open("media/agent_diagram.png", "wb") as file:
        file.write(image_bytes)
    print("Graph saved!")
except Exception as e:
    print("Error saving the graph structure image.", e)
    pass


def get_response(query, agent_config):
    inputs = {
        "messages": [HumanMessage(content=query)]
    }
    start_time = time.time()
    try:
        final_response = graph.invoke(inputs, agent_config)
        end_time = time.time()
        return final_response["messages"][-1].content, f"{end_time - start_time:.2f} seconds"
    except GraphRecursionError:
        final_response = "Recursion Depth Error"
        print("Recursion Error")
        return final_response, f"10 seconds"


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "test_user_1"}}
    while True:
        user_query = input("User Input: ")

        response, res_time = get_response(user_query, config)
        print("Final Response from Agent: ")
        print(response)
