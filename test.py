import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import datetime
import pyttsx3
import time

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDgsUUAeA9sBwKBzz20cAxCyI0dY-g_CPU"

engine = pyttsx3.init()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def check_medicine_time(vectorstore):
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_output_tokens=2048,
    )
    
    retriever = vectorstore.as_retriever()
    
    prompt = ChatPromptTemplate.from_template("""
    Check if any medicine needs to be taken at {current_time}.
    If yes, create a reminder message. If no, respond with "No medicines scheduled for now."
    
    Context: {context}
    """)
    
    chain = (
        {"context": retriever | format_docs, "current_time": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(current_time)

def main():
    st.header("Medicine Reminder 💊")
    
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    
    pdf = st.file_uploader("Upload prescription PDF", type='pdf')
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=20,
        )
        chunks = text_splitter.split_text(text=text)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        st.session_state.vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
        st.success("Prescription uploaded successfully!")

    if st.session_state.vectorstore:
        st.subheader("Current Time: " + datetime.datetime.now().strftime("%I:%M %p"))
        
        if st.button("Check Medicine Schedule"):
            with st.spinner("Checking schedule..."):
                try:
                    reminder = check_medicine_time(st.session_state.vectorstore)
                    st.write(reminder)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        auto_check = st.checkbox("Enable automatic checking (every minute)")
        if auto_check:
            while True:
                reminder = check_medicine_time(st.session_state.vectorstore)
                st.write(reminder)
                engine.say(reminder)
                engine.runAndWait()
                time.sleep(60)

if __name__ == '__main__':
    main()