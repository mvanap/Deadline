from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from documentfunctions import*
from conversation import*
import openai
 
# Load environment variables from .env file
load_dotenv()
 
# Set up Azure OpenAI credentials
AZURE_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
AZURE_MODEL_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')  # e.g., "gpt-35-turbo" or "gpt-4o"
 
# Initialize OpenAI API
openai.api_type = "azure"
openai.api_base = AZURE_ENDPOINT
openai.api_version = AZURE_API_VERSION
openai.api_key = AZURE_API_KEY
openai.api_model = AZURE_MODEL_NAME
 
# Initialize the conversation
conversation = initialize_conversation()
introduction = get_response(conversation)
 
# Initialize FastAPI app
app = FastAPI()
 
# Enable CORS for React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your React app's domain
    allow_credentials=True,
    allow_methods=["*"],  # Ensure all methods, including OPTIONS, are allowed
    allow_headers=["*"],
)
 
UPLOAD_DIR = "C:/Python/HealthBuddy/Attachments"
os.makedirs(UPLOAD_DIR, exist_ok=True)
 
# Global variable to store the FAISS vectorstore
file_vectorstores = {}
 
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
 
        # Log the saved file path
        print(f"File saved to: {file_location}")
 
        # Load, chunk, and create embeddings
        chunked_docs = load_and_chunk(file_location)
        if not chunked_docs:
            return JSONResponse(status_code=400, content={"message": "Failed to chunk document."})
 
        # Log chunking result
        print(f"Number of chunks created: {len(chunked_docs)}")
 
        global vectorstore
        vectorstore = gen_embedding(chunked_docs)
        # After successfully generating the vectorstore
        if not vectorstore:
            return JSONResponse(status_code=500, content={"message": "Failed to create embeddings."})
        # Log vectorstore status
        print(f"Vectorstore populated: {vectorstore is not None}")
        # ✅ Store vectorstore using filename
        file_vectorstores[file.filename] = vectorstore
        return {"message": "File uploaded and processed successfully."}
 
 
    except Exception as e:
        print(f"Error during file upload: {e}")
        return JSONResponse(status_code=500, content={"message": f"Upload failed: {e}"})
 
 
# Define the request schema
class ChatRequest(BaseModel):
    message: str  # The user's message
 
# Define the response schema
class ChatResponse(BaseModel):
    You: str
    HealthBuddy: str
 
# Define the chat route for POST requests
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_input = request.message
    print(f"Received message: {user_input}")
 
    global vectorstore
    if vectorstore:
        response = rag_response(user_input, vectorstore)
        return {
            "You": user_input,
            "HealthBuddy": response
        }
 
    # If vectorstore is not available, fallback to GPT chat
    conversation.append({"role": "user", "content": user_input})
    try:
        response = get_response(conversation)
        conversation.append({"role": "assistant", "content": response})
        return {
            "You": user_input,
            "HealthBuddy": response
        }
    except Exception as e:
        print(f"Error generating response: {e}")
        return {
            "You": user_input,
            "HealthBuddy": "Sorry, something went wrong at backend."
        }
 
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)