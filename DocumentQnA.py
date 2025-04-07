from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
 
from dotenv import load_dotenv
import os
 
load_dotenv("./.env")
 
class DocumentQnA:
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('OPENAI_API_VERSION')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    llm = AzureChatOpenAI()
    embeddings = AzureOpenAIEmbeddings()
    vector_store = InMemoryVectorStore(embeddings)
    text_splitter = RecursiveCharacterTextSplitter()
    memory = MemorySaver()
   
    vectorized = False;
    def __init__(self):
        if not self.api_key:
            raise ValueError("API key is not set. Please set the AZURE_OPENAI_API_KEY environment variable.")
 
        self.llm = AzureChatOpenAI(api_key=self.api_key, azure_endpoint=self.endpoint, azure_deployment="gpt-4o-mini", openai_api_version=self.api_version)
 
        self.embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-ada-002",
            azure_endpoint=self.endpoint,
            openai_api_version=self.api_version
        )
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.memory = MemorySaver()
        self.vectorized = False;
 
    def load_doc_and_process(self, path):
        print("loading and processing")
        loader = PyPDFLoader(path)
        docs = loader.load()
 
        all_splits = self.text_splitter.split_documents(docs)
       
        _ = self.vector_store.add_documents(documents=all_splits)
        self.vectorized = True
 
    def generate_output(self, input_message):
       
        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve information related to a query."""
            retrieved_docs = self.vector_store.similarity_search(query, k=2)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs
       
 
        config = {"configurable": {"thread_id": "abc123"}}
 
        agent_executor = create_react_agent(self.llm, [retrieve], checkpointer=self.memory)
        response = []
        for event in agent_executor.stream(
            {"messages": [{"role": "user", "content": input_message}]},
            stream_mode="values",
            config=config,
        ):
            print(event)
            response.append(event["messages"][-1])
 
        return response[-1].content
 
    def final(self, file_path, input_message):
        if(not self.vectorized): self.load_doc_and_process(file_path)
       
        response = self.generate_output(input_message)
        return response