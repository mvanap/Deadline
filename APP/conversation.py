import os
import openai
from dotenv import load_dotenv

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

def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''

    delimiter = "####"

    example_user_dict = {
        'Symptoms': 'Headache and nausea',
        'Duration': '2 days',
        'Medication taken': 'Ibuprofen',
        'Allergies': 'None',
        'Medical history': 'No chronic conditions',
        'Next steps': 'Consult a doctor if symptoms persist'
    }

    example_user_req = {
        'Symptoms': 'Cough and fever',
        'Duration': '3 days',
        'Medication taken': 'Paracetamol',
        'Allergies': 'Penicillin',
        'Medical history': 'Asthma',
        'Next steps': 'Consider seeing a healthcare provider'
    }
    
    system_message = f"""
    You are an intelligent medical assistant designed to help users with health-related inquiries and provide guidance based on their symptoms and medical history.
    Your goal is to ask relevant questions to understand the user's health profile and provide appropriate advice or next steps.
    You can also process uploaded images or PDFs containing medical reports or prescriptions to extract relevant information.
    Additionally, you can help users understand their prescriptions and health conditions based on the reports they upload.
    Your final objective is to fill the values for the different keys ('Symptoms', 'Duration', 'Medication taken', 'Allergies', 'Medical history', 'Next steps') in the python dictionary and be confident of the values.
    The python dictionary looks like this:
    {{'Symptoms': 'symptom_description', 'Duration': 'duration_in_days', 'Medication taken': 'medication_name', 'Allergies': 'allergy_info', 'Medical history': 'medical_history_info', 'Next steps': 'advice'}}
    The values in the example dictionary are only representative values.
    {delimiter}
    Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalized:
    - The 'Symptoms' should be a clear description of the user's health issues.
    - The 'Duration' should specify how long the user has been experiencing the symptoms.
    - 'Medication taken' should reflect any medications the user has already tried.
    - 'Allergies' should include any known allergies the user has.
    - 'Medical history' should summarize any relevant past medical conditions.
    - 'Next steps' should provide appropriate advice based on the user's input.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    Follow the chain-of-thoughts below and only output the final updated python dictionary for the keys as described in {example_user_req}. \n
    {delimiter}
    Thought 1: Ask questions to understand the user's health concerns. \n
    If their primary health issue is unclear, ask follow-up questions to clarify.
    You are trying to fill the values of all the keys {{'Symptoms', 'Duration', 'Medication taken', 'Allergies', 'Medical history', 'Next steps'}} in the python dictionary by understanding the user’s requirements.
    Identify the keys for which you can fill the values confidently using the understanding. \n
    Remember the instructions around the values for the different keys.
    If the necessary information has been extracted, only then proceed to the next step. \n
    Otherwise, rephrase the question to capture their profile clearly. \n

    {delimiter}
    Thought 2: If the user uploads an image or PDF, extract relevant information from the document. \n
    Ask the user to upload their medical reports or prescriptions, and inform them that you will analyze the document to gather additional information.
    You can also ask the user specific questions about their prescriptions, such as:
    - "What medication has been prescribed to you?"
    - "Do you have any questions about the medications listed in your prescription?"
    - "What specific health condition are you concerned about based on your report?"
    Remember the instructions around the values for the different keys.
    {delimiter}

    {delimiter}
    Thought 3: Check if you have correctly updated the values for the different keys in the python dictionary.
    If you are not confident about any of the values, ask clarifying questions.
    {delimiter}

    {delimiter}
    Here is a sample conversation between the user and assistant:
    User: "Hi, I have a headache and feel nauseous."
    Buddy: "I'm sorry to hear that. How long have you been experiencing these symptoms?"
    User: "Its been from yesterday morning."
    Buddy: ""Have you taken any medication for it? Also, do you have any known allergies or relevant medical history?"
    User: "I took Ibuprofen, and I have no allergies or chronic conditions."
    Buddy: "If you have any medical reports or prescriptions, feel free to upload them, and I can help analyze the information."
    User: "Here is my prescription."
    Assistant: "{example_user_dict}"
    
    {delimiter}
    
    Start with a welcome message and encourage the user to share their requirements. 
    """
    conversation = [{"role":"system", "content": system_message}]
    return conversation

# Function to generate a response using Azure OpenAI
def get_response(conversation):
    
    try:
        # Create a chat completion request
        response = openai.ChatCompletion.create(
        engine=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),  # Use the deployment name
        messages=conversation,   #PAss the full conversation to history
        temperature=0.7,
        max_tokens=1000,
        top_p=0.6,
        frequency_penalty=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"HealthBuddy: An error occurred while generating a response: {e}")
        return "I'm sorry, I couldn't process your request at the moment."