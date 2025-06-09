import os
import logging
from typing import List, Optional
from fastapi import FastAPI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import openai
 
load_dotenv()
 
AZURE_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_MODEL_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
 
app = FastAPI()
 
# Track processing status and store vectorstores keyed by file_id
processing_status = {}
vectorstores = {}
 
def get_llm():
    if os.getenv("USE_AZURE") == "1":
        return ChatOpenAI(
            deployment_name=AZURE_MODEL_NAME,
            openai_api_key=AZURE_API_KEY,
            openai_api_base=AZURE_ENDPOINT,
            openai_api_version=AZURE_API_VERSION,
            temperature=0
        )
    else:
        raise ValueError("OpenAI configuration is not enabled.")
 
def load_and_chunk(file_path: str) -> Optional[List[Document]]:
    if not os.path.exists(file_path):
        logging.error(f"File not found at: {file_path}")
        return None
    _, ext = os.path.splitext(file_path)
    if ext.lower() != ".pdf":
        logging.error("Uploaded document is not a PDF")
        return None
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )
        chunked_docs = splitter.split_documents(pages)
        logging.info(f"Chunked into {len(chunked_docs)} documents.")
        return chunked_docs
    except Exception as e:
        logging.error(f"Error during PDF loading or chunking: {e}")
        return None
 
def gen_embedding(chunked_docs: List[Document]) -> Optional[FAISS]:
    embeddings = []
    if not chunked_docs:
        logging.warning("No chunks provided for embeddings.")
        return None
    try:
        response = openai.Embedding.create(
            input=[doc.content for doc in chunked_docs],
            engine="text-embedding-ada-002"
        )
        embeddings.append(response['data'][0]['embedding'])
        logging.info("Embeddings created")
        vectorstore = FAISS.from_documents(chunked_docs, embeddings)
        logging.info(f"Embeddings created for {len(chunked_docs)} chunks.")
        return vectorstore
    except Exception as e:
        logging.error(f"Failed to create embeddings: {e}")
        return None
 
def rag_response(user_query: str, vectorstore: Optional[FAISS]) -> str:
    if not user_query:
        logging.warning("Empty user query received.")
        return "Please enter your query"
    if not vectorstore:
        logging.error("No vectorstore available for RAG")
        return "RAG is not available due to missing vectorstore"
    try:
        llm = get_llm()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
            return_source_documents=True
        )
        response = qa_chain.run(user_query)
        logging.info("Successfully retrieved RAG response.")
        return response
    except Exception as e:
        logging.error(f"RAG failed: {e}")
        return "Could not process due to internal error."
 