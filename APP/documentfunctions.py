import os
import logging
from typing import List, Optional
from fastapi import FastAPI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import openai, faiss, numpy as np
 
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

def gen_embedding(chunked_docs):
    embeddings = []
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    try:
        for chunk in chunked_docs:
            response = openai.Embedding.create(
                input= chunk,
                engine="text-embedding-ada-002"  # Specify the model
            )
        embeddings.append(response['data'][0]['embedding'])
        logging.info("Embeddings has been created and need to be stored in the vector store.")
        return embeddings
    except Exception as e:
        logging.error(f"Failed to create embeddings manually: {e}")
        return None
    
def store_embeddings(embeddings):
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    logging.info("Embeddings stored in Index")
    return index

 
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
 