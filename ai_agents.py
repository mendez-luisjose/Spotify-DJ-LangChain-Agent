import os
from typing import List
from langchain.memory import ConversationBufferMemory 
from langchain_groq import ChatGroq
from langchain import hub
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import SYSTEM_MESSAGE
import streamlit as st

# LLM Initialization
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

#llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY, max_retries=5)
#llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0, google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)
def initialize_agent(tools: List, is_agent_verbose: bool = True, max_iterations: int = 5, return_thought_process: bool = False):
    system_message = SystemMessage(content=SYSTEM_MESSAGE)
    MEMORY_KEY = "chat_history"
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)],
        "system_message": system_message
    }
    memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)
    prompt = hub.pull("hwchase17/structured-chat-agent")
    agent=create_structured_chat_agent(llm, tools, prompt)

    # Initialize agent
    agent_executor=AgentExecutor(agent=agent, tools=tools, verbose=is_agent_verbose, 
                                 handle_parsing_errors=True, max_iterations=max_iterations,
                                 return_intermediate_steps=return_thought_process, memory=memory,
                                 agent_kwargs=agent_kwargs)

    return agent_executor

