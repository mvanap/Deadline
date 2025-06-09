import openai
from dotenv import load_dotenv
import os

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

prompt= f"""
    You are an intelligent medical assistant designed to help users with health-related inquiries and provide guidance based on their symptoms and medical history.
    Your goal is to ask relevant questions to understand the user's health profile and provide appropriate advice or next steps.
    You can also process uploaded images or PDFs containing medical reports or prescriptions to extract relevant information.
    Additionally, you can help users understand their prescriptions and health conditions based on the reports they upload.
    """


def get_response(prompt):
    # Create a chat completion request
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # Use the deployment name
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides clear and concise summaries."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=0.6,
        frequency_penalty=0.7
    )
    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    print("Chat with Azure OpenAI! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        reply = get_response(user_input)
        print(f"Bot: {reply}")