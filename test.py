import openai
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Optional
from langchain.schema import Document
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Set up Azure OpenAI credentials
AZURE_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_MODEL_NAME = os.getenv('AZURE_MODEL_NAME')  # e.g., "gpt-35-turbo" or "gpt-4o"

# Initialize OpenAI API
openai.api_type = "azure"
openai.api_base = AZURE_ENDPOINT
openai.api_version = AZURE_API_VERSION
openai.api_key = AZURE_API_KEY

file_path = r"C:\Python\HealthBuddy\Attachments\Manideep_HealthBuddy.pdf"

# Configure logging
logging.basicConfig(level=logging.INFO)

def load_and_chunk(file_path: str) -> Optional[List[Document]]:
    # Check if the file exists
    if not os.path.exists(file_path):
        logging.error(f"File not found at: {file_path}")
        return None
    
    # Check if the file is a PDF
    _, ext = os.path.splitext(file_path)
    if ext.lower() != ".pdf":
        logging.error("Uploaded document is not a PDF")
        return None
    
    try:
        # Load the PDF file
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Split the content into chunks
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
    
def get_openai_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        response = openai.Embedding.create(
            input=chunk,
            engine="text-embedding-ada-002"  # Specify the model
        )
        embeddings = embeddings.append(response['data'][0]['embedding'])
    return np.array(embeddings)
def gen_embedding(chunked_docs: List[Document]) -> Optional[FAISS]:
    if not chunked_docs:
        logging.warning("No chunks provided for embeddings.")
        return None
    try:
        embeddings = []
        response = openai.Embedding.create(
            engine="text-embedding-ada-002",
            api_key=AZURE_API_KEY
        )
        embeddings.append(response['data'][0]['embedding'])
        vectorstore = FAISS.from_documents(chunked_docs, embeddings)
        logging.info(f"Embeddings created for {len(chunked_docs)} chunks.")
        return vectorstore
    except Exception as e:
        logging.error(f"Failed to create embeddings: {e}")
        return None



# Load your chunks (assuming you have a list of text chunks)
chunks = ["This is the first chunk.", "This is the second chunk.", "This is the third chunk."]
# Generate embeddings for each chunk
chunk_embeddings = get_openai_embeddings(chunks)
# Print the shape of the embeddings
print(f"Generated embeddings shape: {chunk_embeddings.shape}")
print(chunk_embeddings)

# Example usage
if __name__ == "__main__":

    # Call the function to load and chunk the PDF
    documents = load_and_chunk(file_path)
    
    if documents:
        # Print the chunked documents
        for idx, doc in enumerate(documents):
            print(f"Chunk {idx + 1}:\n{doc.page_content}\n")
