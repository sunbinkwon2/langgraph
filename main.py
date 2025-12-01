from langchain_teddynote import logging
logging.langsmith("CH17-LangGraph-Use-Cases")

from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict
from typing import List
from langchain_teddynote.models import LLMs, get_model_name
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from langchain_teddynote.graphs import visualize_graph
from langchain_core.runnables import RunnableConfig
from langchain_teddynote.messages import stream_graph, random_uuid

MODEL_NAME = get_model_name(LLMs.GPT4)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_chatbot(messages: List[BaseMessage]) -> dict:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a customer support agent for an airline. Answer in Korean."),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    model = ChatOpenAI(model=MODEL_NAME, temperature=0.6)
    chain = prompt | model | StrOutputParser()
    return chain.invoke({"messages": messages})

def create_scenario(name: str, instructions: str):
    system_prompt_template = """You are a customer of an airline company. \
You are interacting with a user who is a customer support person. \
Your name is {name}.

# Instructions:
{instructions}

[IMPORTANT] 
- When you are finished with the conversation, respond with a single word 'FINISHED'
- You must speak in Korean."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_template),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(name=name, instructions=instructions)
    return prompt

instructions = """You are trying to get a refund for the trip you took to Jeju Island. \
You want them to give you ALL the money back. This trip happened last year."""
name = "Teddy"
simulated_user = create_scenario(name, instructions)
model = ChatOpenAI(model=MODEL_NAME, temperature=0.6)
simulated_user = simulated_user | model | StrOutputParser()

def _swap_roles(messages):
    new_messages = []
    for m in messages:
        if isinstance(m, AIMessage):
            new_messages.append(HumanMessage(content=m.content))
        else:
            new_messages.append(AIMessage(content=m.content))
    return new_messages

def ai_assistant_node(state: State):
    ai_response = call_chatbot(state["messages"])
    return {"messages": [("assistant", ai_response)]}

def simulated_user_node(state: State):
    new_messages = _swap_roles(state["messages"])
    response = simulated_user.invoke({"messages": new_messages})
    return {"messages": [("user", response)]}

def should_continue(state: State):
    if len(state["messages"]) > 6:
        return "end"
    elif state["messages"][-1].content == "FINISHED":
        return "end"
    else:
        return "continue"

graph_builder = StateGraph(State)
graph_builder.add_node("simulated_user", simulated_user_node)
graph_builder.add_node("ai_assistant", ai_assistant_node)
graph_builder.add_edge("ai_assistant", "simulated_user")
graph_builder.add_conditional_edges(
    "simulated_user",
    should_continue,
    {
        "end": END,
        "continue": "ai_assistant",
    },
)
graph_builder.set_entry_point("ai_assistant")
simulation = graph_builder.compile()
visualize_graph(simulation)

config = RunnableConfig(recursion_limit=10, configurable={"thread_id": random_uuid()})
inputs = {"messages": [HumanMessage(content="안녕하세요? 저 지금 좀 화가 많이 났습니다^^")]}
stream_graph(simulation, inputs, config, node_names=["simulated_user", "ai_assistant"])
