import openai
from dotenv import load_dotenv
import os

#Loading the .env file here
load_dotenv()

#Setting up the Azure OpenAI key and endpoints 
AZURE_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')

#Initialising a client to interact with API effectively
openai.api_key = AZURE_API_KEY
openai.api_version = AZURE_API_VERSION
openai.api_type = "azure"
openai.api_base = AZURE_ENDPOINT


def get_openai_response(user_query):
    """
    Function to get a response from the Azure OpenAI based on the user query.

    Args:
        user_query (_type_): This should be the question or query of the user that should be sent to the Open AI model.
        
    Returns: 
        str: The Response from the Open AI model.
        
    """
    try:
        
        #sending request to openai
        response = openai.ChatCompletion.create(
            engine = AZURE_DEPLOYMENT_NAME,
            messages = 
            [
                {"role": "user", "content": user_query},
                {"role": "system", "content": "The Assistant is mainly focused to help the users on Medicines and Health" }
            ]
            
        )
        
        #Extracting response text
        response_text = response['choices'][0]['message']['content']
        return response_text
    
    except Exception as e:
        return f"An Error Occured: {str(e)}"
    
    
if __name__ == '__main__':
    query = input("You: ")
    response = get_openai_response(query)