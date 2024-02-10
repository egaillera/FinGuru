
import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import HuggingFaceHub
from pathlib import Path


def create_vectorstore(text_chunks, embeddings,vectorstore_path):
    print("Creating and saving vectorstore ...")
    vectorstore = FAISS.from_texts(texts = text_chunks, embedding=embeddings)
    vectorstore.save_local(vectorstore_path)

    return vectorstore

def get_vectorstore(embeddings,vectorstore_path):
    if os.path.exists(vectorstore_path):
        print("Loading vectorstore ... ")
        vectorstore = FAISS.load_local(vectorstore_path, embeddings)
    
    return vectorstore

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len)
    chunks = text_splitter.split_text(text)

    return chunks

def get_pdf_chunks(filename):
    
    print("Analyzing " +  Path(filename).stem  + " ...",end="")
    pdf_reader = PdfReader(filename)

    # Just analyze contents of the first page
    text = pdf_reader.pages[0].extract_text()
    chunks = get_text_chunks(text)
    print("... " +  str(len(chunks)) + " chunks extracted")

    # Add the name of the fund to each chunk
    id_chunks = ["Información sobre el fondo " + Path(filename).stem + ": " + c for c in chunks]

    return id_chunks
            
def get_docs_chunks(path):    
    chunks = []
    n_docs = 0
    for filename in os.listdir(path):
        if filename.endswith('.pdf'):
            chunks = chunks + get_pdf_chunks(path+filename)
            n_docs += 1
    print("Generated " + str(len(chunks)) + " chunks from " + str(n_docs) + " documents") 
    
    return chunks

def prepare_setup():
    load_dotenv()
   
    # Settings
    docs_path = os.getenv('DOCS_PATH')
    vectorstore_path = os.getenv('VECTORSTORE_PATH')
   
    print("Preparing data ... ")
    embeddings = OpenAIEmbeddings()
    #embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")

    if os.path.exists(vectorstore_path):
         vectorstore = get_vectorstore(embeddings,vectorstore_path)
    else:
        text_chunks = get_docs_chunks(docs_path)
        vectorstore = create_vectorstore(text_chunks, embeddings, vectorstore_path)

    template = """You are a financial assistant for question-answering tasks related to investment funds. 
                Use the following pieces of retrieved context to answer the question. 
                The answer should be always in Spanish.
                If you found a fund, explain its features t a bit
                If you don't know the answer, just say that you don't know. 
                Use six sentences maximum and keep the answer concise.
                Question: {question} 
                Context: {context} 
                Answer:
                """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI()
    #llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":2048})
    
    rag_chain = (
    {"context": vectorstore.as_retriever(),  "question": RunnablePassthrough()} 
    | prompt 
    | llm
    | StrOutputParser() 
)
    
    return rag_chain


def main():
    rag_chain = prepare_setup()

    while True:
        user_question = input("Describe las caracteristicas de tu fondo: ")
        #docs_and_scores = vectorstore.similarity_search_with_score(user_question)
        response = rag_chain.invoke(user_question)
        print(response)
            

if __name__ == '__main__':
    main()