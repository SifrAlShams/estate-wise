from typing import Annotated, Sequence

from langchain_core.output_parsers import StrOutputParser
from langgraph.errors import GraphRecursionError
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode

from langgraph.checkpoint.memory import MemorySaver

import time

from utils.extract_data_from_input import extract
from utils.model import llm
from prompts.agent_prompts import intent_system_msg, chatbot_system_msg, generate_system_msg, general_system_msg, \
    client_detail_gathering
from utils.custom_tools import faq_retriever_tool, listings_retriever_tool, datetime_tool

from utils.custom_tools import is_date_available, add_meeting_to_calender
from utils.google_calender_utils.get_service import service


datetime_tools = [datetime_tool]
tools = [faq_retriever_tool, listings_retriever_tool]

# user_input = []
user_name = []
user_email = []
meeting_date = []
connect_called = []


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
    print(agent_response)
    return {"messages": [agent_response]}


def generate(state: AgentState):
    print(f'---GENERATE--- docs len {len(state["messages"])}')
    print(f"USE CASE: {state['use_case']}")

    messages = state["messages"]

    # print(messages)

    if state['use_case'][-1] == 'general':
        agent_response = llm.invoke([general_system_msg] + list(messages))
        return {"messages": [agent_response]}

    if isinstance(state['messages'][-1], AIMessage):
        return {'messages': [state['messages'][-1]]}

    elif isinstance(state['messages'][-1], ToolMessage):
        user_inp = state['user_input'][-1]

        prompt = generate_system_msg
        model = llm

        rag_chain = prompt | model | StrOutputParser()

        agent_response = rag_chain.invoke({"knowledge": messages[-1].content, "question": user_inp})

        return {"messages": [agent_response]}



def schedule_meeting(state: AgentState):
    global user_name, user_email, meeting_date, connect_called
    print("---SCHEDULE MEETING NODE---")

    connect_called.append("True")
    if len(connect_called) > 1:
        print("Extracting Information")
        user_input = state["user_input"][-1]
        data = extract(user_input)

        for k, v in data.items():
            if v is not None:
                if k == 'name':
                    user_name.append(v)
                elif k == 'email':
                    user_email.append(v)
                elif k == 'date':
                    meeting_date.append(v)
    if len(user_name) > 0 and len(user_email) > 0 and len(meeting_date) > 0:
        print("ALL DATA GATHERED!")
        print(user_email, user_name, meeting_date)

        client_data = {
            "name": user_name[-1],
            "email": user_email[-1],
            "date": meeting_date[-1]
        }

        if is_date_available(client_data, service):
            scheduling_response = add_meeting_to_calender(client_data, service)
            return {"messages": state["messages"] + [scheduling_response]}

        else:
            return {"messages": state["messages"] + ["Sorry, we are not available on this date."]}

    messages = state["messages"]

    system_message = client_detail_gathering
    model = llm.bind_tools(datetime_tools)
    agent_response = model.invoke([system_message] + list(messages))

    return {"messages": agent_response}

#### Graph Compilation
workflow = StateGraph(AgentState)

# add nodes
tool_node_object = ToolNode(tools)
workflow.add_node("tools-node", tool_node_object)
workflow.add_node("agent-node", agent)
workflow.add_node("generate-node", generate)
workflow.add_node("scheduling-node", schedule_meeting)

# add edges
workflow.add_conditional_edges(
    START,
    intent_classification,
    {
        "connect": "scheduling-node",
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


# if __name__ == "__main__":
#     config = {"configurable": {"thread_id": "test_user_1"}}
#     while True:
#         user_query = input("User Input: ")
#
#         response, res_time = get_response(user_query, config)
#         print("Final Response from Agent: ")
#         print(response)
