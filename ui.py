import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import getpass
import os
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import create_retrieval_chain 
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_huggingface import HuggingFaceEmbeddings
import requests
import json
import pandas as pd
from monday import MondayClient
import re
import time

from graphqlclient import GraphQLClient

def get_Ers_doc_based_on_topic(topic_list_string):
   if topic_list_string!="":
      if "Search" in topic_list_string:
            API_KEY = st.secrets['apiKey']
            query=  """ {
                         boards (ids: 6633501571){
                           items_page (limit: 500) {
                       
                             items {
                               id 
                               name
                               column_values {
                                    id 
                                    text
                                    value
                               }
                             }
                           }
                         }
                       }"""
            client = GraphQLClient('https://api.monday.com/v2')
            client.inject_token(API_KEY)
            col="{ boards(ids: 6633501571) {columns { id title}}}"# Execute the query
            data_response = client.execute(query)
            colname=client.execute(col)
            data=json.loads(data_response)
            col_names=json.loads(colname)
            col_dict=col_names['data']['boards'][0]['columns']
            output_dict = {item['id']: item['title'] for item in col_dict}
            columns_to_keep = ['status', 'bpm96', 'dropdown4', 'dropdown3','priority3','numbers13','description__1']
            documents = [
                   Document(
                       page_content=f"{item['name']}\n" + "\n".join(f"{output_dict.get(cv['id'], cv['id'])}: {cv['text'] or cv['value']}" for cv in item['column_values'] if cv['id'] in columns_to_keep),
                       metadata={cv['id']: cv['text'] for cv in item['column_values'] if cv['id'] in columns_to_keep})for item in data['data']['boards'][0]['items_page']['items']]
      elif "Filters" in topic_list_string:
            API_KEY = st.secrets['apiKey']
            query=  """ {
                         boards (ids: 6633501571){
                           items_page (limit: 500) {
                       
                             items {
                               id 
                               name
                               column_values {
                                    id 
                                    text
                                    value
                               }
                             }
                           }
                         }
                       }"""
            client = GraphQLClient('https://api.monday.com/v2')
            client.inject_token(API_KEY)
            col="{ boards(ids: 6633501571) {columns { id title}}}"# Execute the query
            data_response = client.execute(query)
            colname=client.execute(col)
            data=json.loads(data_response)
            col_names=json.loads(colname)
            col_dict=col_names['data']['boards'][0]['columns']
            output_dict = {item['id']: item['title'] for item in col_dict}
            columns_to_keep = ['status', 'bpm96', 'dropdown4', 'dropdown3','priority3','numbers13','description__1']
            documents = [
                   Document(
                       page_content=f"{item['name']}\n" + "\n".join(f"{output_dict.get(cv['id'], cv['id'])}: {cv['text'] or cv['value']}" for cv in item['column_values'] if cv['id'] in columns_to_keep),
                       metadata={cv['id']: cv['text'] for cv in item['column_values'] if cv['id'] in columns_to_keep})for item in data['data']['boards'][0]['items_page']['items']]
      elif "Locate" in topic_list_string :
            API_KEY = st.secrets['apiKey']
               
            query=  """ {
                      boards (ids: 6800094599){
                        items_page (limit: 500) {
                    
                          items {
                            id 
                            name
                            column_values {
                                 id 
                                 text
                                 value
                            }
                          }
                        }
                      }
                    }"""
            
            client = GraphQLClient('https://api.monday.com/v2')
            client.inject_token(API_KEY)
            col="{ boards(ids: 6800094599) {columns { id title}}}"
            # Execute the query
            data_response = client.execute(query)
            colname=client.execute(col)
            data=json.loads(data_response)
            col_names=json.loads(colname)
            col_dict=col_names['data']['boards'][0]['columns']
            output_dict = {item['id']: item['title'] for item in col_dict}
            columns_to_keep = ['status', 'bpm96', 'dropdown4', 'dropdown3','priority3','numbers13','description__1']
            documents = [
                Document(
                    page_content=f"{item['name']}\n" + "\n".join(f"{output_dict.get(cv['id'], cv['id'])}: {cv['text'] or cv['value']}" for cv in item['column_values'] if cv['id'] in columns_to_keep),
                    metadata={cv['id']: cv['text'] for cv in item['column_values'] if cv['id'] in columns_to_keep}
                )
                
                for item in data['data']['boards'][0]['items_page']['items']]
      else: 
               API_KEY = st.secrets['apiKey']
               query = f"""{{
               items_page_by_column_values (limit: 500, board_id: 5893852581, columns: {{column_id:"parent_topic9", column_values:[{topic_list_string}]}})
                   {{ items{{
                   id
                   name
                   column_values{{
                       id 
                       text
                       value
                   }}
                   }}
                   }}
               }}"""
               client = GraphQLClient('https://api.monday.com/v2')
               client.inject_token(API_KEY)
               col="{ boards(ids: 5893852581) {columns { id title}}}"
               # Execute the query
               data_response = client.execute(query)
               colname=client.execute(col)
               data=json.loads(data_response)
               col_names=json.loads(colname)
               col_dict=col_names['data']['boards'][0]['columns']
               output_dict = {item['id']: item['title'] for item in col_dict}
           
               columns_to_keep = ['status', 'bpm96', 'dropdown4', 'dropdown3','priority3','numbers13','description__1']
               documents = [
                   Document(
                       page_content=f"{item['name']}\n" + "\n".join(f"{output_dict.get(cv['id'], cv['id'])}: {cv['text'] or cv['value']}" for cv in item['column_values'] if cv['id'] in columns_to_keep),
                       metadata={cv['id']: cv['text'] for cv in item['column_values'] if cv['id'] in columns_to_keep}) for item in data['data']['items_page_by_column_values']['items']]
   else:
        documents=''
        st.write('Please select your topics in step 1')
   return documents


def creat_rag(doc):
    if er_doc is None:
        raise ValueError("er_doc is None. Please provide valid documents.")
    if doc!='':

        os.environ["OPENAI_API_KEY"] = st.secrets['openaikey']
        model = ChatOpenAI(model="gpt-4")
        embeddings = HuggingFaceEmbeddings()
        faiss_index = FAISS.from_documents(doc, embeddings)
        retriever = faiss_index.as_retriever(search_kwargs={"k":7})
        system_prompt = (
            "You are an assistant for question-answering tasks. Be sure to present the ER Number as you reference them "
            "Use the following pieces of retrieved context to answer. Also, let me know how many context do you have"
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer with a bit more detail."
            "\n\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(model, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        st.write("AI is ready")
    else:
        st.write("Please follow step 1&2")
    return rag_chain




# Ui
st.set_page_config(
        page_title="Enhancement Request AI Assitent",


        
    )
st.header("Ask about GPT about ERs",divider='rainbow')

st.write('Step 1: Select the topics you are interested')
if 'option' not in st.session_state:
    st.session_state['option'] = ""
options=0
optionlist=['AI',
 'Citation',
 'API_endpoints',
 'Recommendation',
 'Authentication',
 'Dashboard',
 'Internationalization',
 'RTAC',
 'Customization ',
 'Custom_link',
 'Fulltext',
 'Result_list',
 'Search',
 'Integration',
 'Filters',
 'Export',
 'Folder',
 'UX','Locate']

optionlist.sort()

options = st.multiselect(
    "What topics do you want to ask about, up to 3",
    optionlist,max_selections=3)
# Initialize session state if not already set
formatted_topic_list=0

if options!=0:
    formatted_topic_list = ', '.join(f'"{item}"' for item in options)

if formatted_topic_list:  # Update only if there's a new selection
    st.session_state.option = f'"{formatted_topic_list}"'
    


st.write('Step 2: Gather Er based on your topic')




def get_er_doc(topic_string):
    if clicked == True:
      document=get_Ers_doc_based_on_topic(topic_string)
      clicked == False
      return document
        




    
clicked=st.button("Gather ER based on Selected Topic")
if 'got_er_doc' not in st.session_state:
    st.session_state['got_er_doc'] = False 

if 'getrag' not in st.session_state:
    st.session_state['getrag'] = False 

if st.session_state['option'] != "":
    with st.spinner('Downloading ERs from Monday.Com'):
        er_doc=get_er_doc(st.session_state.option)

    
    if er_doc:  # Update only if there's a new selection
        st.session_state.got_er_doc = er_doc
        st.session_state['getrag'] = False 
        


    with st.sidebar:
        st.write('The ERs that AI is going to read')
        st.write(st.session_state.got_er_doc)
        


# Initialize session state if not already set

if 'errag' not in st.session_state:
    st.session_state['errag'] = False 

if 'getrag' not in st.session_state:
    st.session_state['getrag'] = False 



if st.session_state['got_er_doc']!=False:
    if st.session_state['getrag'] == False:
        if formatted_topic_list!=0:
            with st.spinner('AI is reading the ERs now'):
                rag_chain=creat_rag(er_doc)
                if rag_chain:  # Update only if there's a new selection
                    st.session_state.getrag =rag_chain



# Initialize session state if not already set

def response_generator(question):
    response=st.session_state.getrag.invoke({"input": question})['answer']
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

if st.session_state.getrag !=False:
    st.write("the AI is ready,please ask your question know:")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What features does customer wants about AI Ers?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(prompt))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
