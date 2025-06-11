import os
from dotenv import load_dotenv
from typing import List, Optional
 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
 
# Load environment variables
load_dotenv()
 
# Config
AZURE_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')  # model/deployment name
 
# Get LLM (Chat completion model)
def get_llm():
    return AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME,
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_API_VERSION,
        temperature=0
    )
 
# Load and chunk PDF
def load_and_chunk(file_path: str) -> Optional[List[Document]]:
    if not os.path.exists(file_path):
        print(f"[ERROR] file not found at: {file_path}")
        return None
   
    _, ext = os.path.splitext(file_path)
    if ext.lower() != ".pdf":
        print("[ERROR] Uploaded file is not a PDF.")
        return None
 
    try:
        print("Loading PDF file")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
 
        print("Splitting pages into chunks")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )
        chunked_docs = splitter.split_documents(pages)
        print(f"[INFO] Chunked into {len(chunked_docs)} documents.")
        return chunked_docs
 
    except Exception as e:
        print(f"[ERROR] During PDF loading/chunking: {e}")
        return None
 
# Generate embeddings
def gen_embedding(chunked_docs: List[Document]) -> Optional[FAISS]:
    try:
        if not chunked_docs:
            print("[WARNING] No chunks provided for embeddings.")
            return None
 
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment="text-embedding-ada-002",
            api_key=AZURE_API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            api_version=AZURE_API_VERSION
        )
 
        vectorstore = FAISS.from_documents(chunked_docs, embeddings)
        print(f"[INFO] Embeddings created for {len(chunked_docs)} chunks.")
        return vectorstore
 
    except Exception as e:
        print(f"[ERROR] Failed to create embeddings: {e}")
        return None
 
# RAG response
def rag_response(user_query: str, vectorstore: Optional[FAISS]) -> str:
    try:
        if not user_query:
            print("[WARNING] Empty user query received.")
            return "Please enter your query"
        if not vectorstore:
            print("[ERROR] No vectorstore available for RAG")
            return "RAG is not available due to missing vectorstore"
 
        llm = get_llm()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
            return_source_documents=True
        )
 
        result = qa_chain.invoke({"query": user_query})
        response = result["result"]  # 👈 This is the answer
        print("[INFO] Successfully retrieved RAG response.")
 
        # 🔍 Optional: Log retrieved documents for debugging
        for i, doc in enumerate(result["source_documents"]):
            print(f"\n🔎 Chunk {i+1} Preview:\n{doc.page_content[:300]}...\n---")
 
        return response
 
    except Exception as e:
        print(f"[ERROR] RAG failed: {e}")
        return "Could not process due to internal error."