import openai
from dotenv import load_dotenv 
from openai import AzureOpenAI
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt
import pandas as pd
from IPython.display import display, HTML
from openai import OpenAI
import json

load_dotenv()
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION") 

#For app user: you need to pass the version configured by the admin 
 
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") #Eg: {BASE_URL}/api/azureai 

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") 


#For App User: use the app-registration key along with the app configuration unique key name eg. app123key-configName, For Api User: Substitute the key generated from Key Config Panel 
 
client = AzureOpenAI() 


def initialize_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''

    delimiter = "####"

    example_user_dict = {'Destination': 'Kashmir',
                         'Travel dates': '10-Oct to 17-Oct',
                        'Accommodation type': 'Delux',
                        'Budget': 200000,
                        'Activities': 'Food-Dining',
                        'Travel companions': 4}

    example_user_req = {'Destination': 'Mumbai',
                        'Travel dates': '10-Nov to 17-Nov',
                        'Accommodation type': 'Delux',
                        'Budget': 20000,
                        'Activities': 'Food-Dining',
                        'Travel companions': 4}
    
    system_message = f"""
    You are an intelligent travel planner expert and your goal is to help users plan the best trip based on their preferences.
    You need to ask relevant questions and understand the user profile by analyzing their responses.
    Your final objective is to fill the values for the different keys ('Destination', 'Accommodation type', 'Travel duration', 'Activities', 'Meal preference', 'Budget') in the python dictionary and be confident of the values.
    These key-value pairs define the user's travel preferences.
    The python dictionary looks like this:
    {{'Destination': 'values','Accommodation type': 'hotel_type','Travel duration': 'number','Activities': 'activity_type','Budget': 'number','Meal preference': 'meal'}}
    The number for 'Budget' should be a numerical value extracted from the user's response.
    The values for all other keys should be inferred based on the user's responses and context.
    The hotel_type for all other keys should be inferred based on the user's responses and context.
    The activity_type for all other keys should be inferred based on the user's responses and context.
    The meal for all other keys should be inferred based on the user's responses and context.
    All the values in the example dictionary are only representative values.
    {delimiter}
    Here are some instructions around the values for the different keys. If you do not follow this, you'll be heavily penalized:
    - The hotel_type for 'Accommodation type' should be either 'luxury', 'mid-range', or 'budget' based on user preferences.
    - The number for 'Travel duration' should be a specific number of days based on the user's input.
    - 'Activities' should reflect the type of activity_type the user wants to do, like 'sightseeing', 'adventure', 'relaxation', etc.
    - The number for 'Budget' should be a numerical value extracted from the user's response and should align with their accommodation and travel type.
    - Do not randomly assign values to any of the keys.
    - The values need to be inferred from the user's response.
    {delimiter}

    To fill the dictionary, you need to have the following chain of thoughts:
    Follow the chain-of-thoughts below and only output the final updated python dictionary for the keys as described in {example_user_req}. \n
    {delimiter}
    Thought 1: Ask questions to understand the user's travel preferences. \n
    If their primary travel purpose is unclear, ask follow-up questions to clarify.
    You are trying to fill the values of all the keys {{'Destination', 'Accommodation type', 'Travel duration', 'Activities', 'Meal preference', 'Budget'}} in the python dictionary by understanding the user’s requirements.
    Identify the keys for which you can fill the values confidently using the understanding. \n
    Remember the instructions around the values for the different keys.
    If the necessary information has been extracted, only then proceed to the next step. \n
    Otherwise, rephrase the question to capture their profile clearly. \n

    {delimiter}
    Thought 2: Now, you are trying to fill the values for the rest of the keys which you couldn't in the previous step.
    Ask relevant questions to gather the remaining information you need to complete the user's profile. \n
    For example, inquire about their meal preferences or specific activities they'd like to do.
    Remember the instructions around the values for the different keys.
    {delimiter}

    {delimiter}
    Thought 3: Check if you have correctly updated the values for the different keys in the python dictionary.
    If you are not confident about any of the values, ask clarifying questions.
    {delimiter}

    {delimiter}
    Here is a sample conversation between the user and assistant:
    User: "Hi, I want to plan a vacation."
    Assistant: "Great! Where would you like to go for your vacation? Knowing your destination will help me tailor my recommendations to your preferences."
    User: "I’m thinking of going to Paris."
    Assistant: "Fantastic choice! Paris has a lot to offer. How long are you planning to stay, and what kind of accommodation do you prefer? Would you prefer something luxurious, mid-range, or budget-friendly?"
    User: "I will stay for 7 days, and I prefer luxury accommodation."
    Assistant: "Wonderful. What kind of activities are you interested in? Are you looking for sightseeing, adventure, or maybe relaxation? Additionally, could you share your meal preferences and your travel budget?"
    User: "I’d like to focus on sightseeing and I prefer vegetarian meals. My budget is around 2000 EUR."
    Assistant: "{example_user_dict}"
    {delimiter}

    Start with a short welcome message and encourage the user to share their requirements.
    """
    conversation = [{"role": "system", "content": system_message}]
    return conversation

def get_chat_completions(input, json_format=False):
    MODEL = 'gpt-4o-mini'
    system_message_json_output = """<<. Return output in JSON format to the key output.>>"""
    
    if json_format:
        input[0]['content'] += system_message_json_output

        try:
            chat_completion_json = client.chat.completions.create(
                model=MODEL,
                messages=input
            )
            output = json.loads(chat_completion_json.choices[0].message.content)
        except Exception as e:
            print(f"Error in API call: {e}")
            return None

    else:
        try:
            chat_completion = client.chat.completions.create(
                model=MODEL,
                messages=input
            )
            output = chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error in API call: {e}")
            return None

    return output


def iterate_llm_response(funct, debug_response, num=10):
    """
    Calls a specified function repeatedly and prints the results.
    This function is designed to test the consistency of a response from a given function.
    It calls the function multiple times (default is 10) and prints out the iteration count,
    the function's response(s).
    
    Args:
        funct (function): The function to be tested. This function should accept a single argument
                          and return the response value(s).
        debug_response (dict): The input argument to be passed to 'funct' on each call.
        num (int, optional): The number of times 'funct' will be called. Defaults to 10.
    
    Returns:
        This function only returns the results to the console.
    """
    i = 0  # Initialize counter

    while i < num:  # Loop to call the function 'num' times
        response = funct(debug_response)  # Call the function with the debug response

        # Print the iteration number, result, and reason from the response
        print("Iteration: {0}".format(i))
        print(response)
        print('-' * 50)  # Print a separator line for readability
        i += 1  # Increment the counter

# Example usage: test the consistency of responses from 'intent_confirmation_layer'
#return iterate_llm_response(get_chat_completions, messages)

# Define a function called moderation_check that takes user_input as a parameter.

def moderation_check(user_input):
    # Call the OpenAI API to perform moderation on the user's input.
    response = openai.moderations.create(input=user_input)
    response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages= [{'role' : 'user', 'content' : str(user_input)}],
                temperature=0,
                max_tokens=900
            )
    response = response.prompt_filter_results[0]['content_filter_results']
    if not response['hate']['severity'] == 'safe':
         return 'Flagged'
    if not response['jailbreak']['detected'] == False:
         return 'Flagged'
    if not response['self_harm']['severity'] == 'safe':
         return 'Flagged'
    if not response['sexual']['severity'] == 'safe':
         return 'Flagged'
    if not response['violence']['severity'] == 'safe':
         return 'Flagged'
    return 'Not Flagged'

    
def intent_confirmation_layer (response_assistant):
    delimiter = "####"

    #allowed_values = {'low', 'medium', 'high'}
    Allowed_hotel_type = {'luxury','mid-range','budget'}
    Allowed_Activity_Type = {'Sightseeing','adventure','relaxation'}
    meal_type = {'Vegetarian','Non Vegetarian'}
    

    prompt = f"""
    You are a senior travel planner who has an eye for detail. The input text will contain a user requirement captured through 6 keys.
    You are provided an input. You need to evaluate if the input text has the following keys:
    {{
    'Destination': 'string',
    'Travel dates': 'date range',
    'Accommodation type': 'Allowed_hotel_type',
    'Budget': 'number',
    'Activities': 'Allowed_Activity_Type',
    'Meal preference': 'meal'}}

    
    The hotel_type for the keys should only be from the allowed hotel type: {Allowed_hotel_type}.
    The activity_type for the keys should only be from the allowed Activity type: {Allowed_Activity_Type}.
    The number for 'Budget' should be a numerical value extracted from the user's response.
    The hotel_type for all other keys should be inferred based on the user's responses and context.
    The activity_type for all other keys should be inferred based on the user's responses and context.
    The meal for all other keys should be inferred based on the user's responses and context: {meal_type}.
    Next you need to evaluate if the keys have the values filled correctly.
    Only output a one-word string in JSON format at the key 'result' - Yes/No.
    Thought 1 - Output a string 'Yes' if the values are correctly filled for all keys, otherwise output 'No'.
    Thought 2 - If the answer is No, mention the reason in the key 'reason'.
    Thought 3 - Think carefully before answering.
    """

    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": f"""Here is the input: {response_assistant}"""}]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},
        seed=1234
        # n = 5
    )

    json_output = json.loads(response.choices[0].message.content)

    return json_output

def dictionary_present(response):
    delimiter = "####"

    user_req = {
        'Budget': '50000',
        'Destination Type': 'beach/mountain/city',
        'Travel Style': 'luxury/budget/adventure',
        'Activities': 'cultural/sightseeing/adventure',
        'Duration': 'short/medium/long'
    }

    prompt = f"""You are a python expert. You are provided an input.
    You have to check if there is a python dictionary present in the string.
    It will have the following format {user_req}.
    Your task is to just extract the relevant values from the input and return only the python dictionary in JSON format.
    The output should match the format as {user_req}.

    {delimiter}
    Make sure that the value of budget is also present in the user input. ###
    The output should contain the exact keys and values as present in the input.
    Ensure the keys and values are in the given format:
    {{
    'Budget': 'numerical value',
    'Destination Type': 'beach/mountain/city',
    'Travel Style': 'luxury/budget/adventure',
    'Activities': 'cultural/sightseeing/adventure',
    'Duration': 'short/medium/long'
    }}
    Here are some sample input output pairs for better understanding:
    {delimiter}
    input 1: - Budget: 50,000 INR - Destination Type: beach - Travel Style: budget - Activities: cultural - Duration: short
    output 1: {{'Budget': '50000', 'Destination Type': 'beach', 'Travel Style': 'budget', 'Activities': 'cultural', 'Duration': 'short'}}

    input 2: {{'Budget': '90,000', 'Destination Type': 'mountain', 'Travel Style': 'luxury', 'Activities': 'sightseeing', 'Duration': 'medium'}}
    output 2: {{'Budget': '90000', 'Destination Type': 'mountain', 'Travel Style': 'luxury', 'Activities': 'sightseeing', 'Duration': 'medium'}}

    input 3: Here is your travel profile 'Budget': '200000 INR', 'Destination Type': 'city', 'Travel Style': 'adventure', 'Activities': 'adventure', 'Duration': 'long'
    output 3: {{'Budget': '200000', 'Destination Type': 'city', 'Travel Style': 'adventure', 'Activities': 'adventure', 'Duration': 'long'}}
    {delimiter}
    """
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": f"""Here is the user input: {response}""" }]

    confirmation = get_chat_completions(messages, json_format=True)

    return confirmation

def product_map_layer(travel_description):
    delimiter = "#####"

    travel_spec = {
        "Destination Type": "(Type of destination: beach, mountain, city)",
        "Travel Style": "(Style of travel: luxury, budget, adventure)",
        "Activities": "(Type of activities: cultural, sightseeing, adventure)",
        "Duration": "(Trip duration: short, medium, long)"
    }

    values = {'beach', 'mountain', 'city', 'luxury', 'budget', 'adventure', 'cultural', 'sightseeing', 'short', 'medium', 'long'}

    prompt = f"""
    You are a Travel Specification Classifier whose job is to extract the key features of travel plans and classify them as per user requirements.
    To analyze each travel description, perform the following steps:
    Step 1: Extract the travel's primary features from the description {travel_description}
    Step 2: Store the extracted features in {travel_spec}
    Step 3: Classify each of the items in {travel_spec} into {values} based on the following rules:
    {delimiter}
    Destination Type:
    - beach: <<< if the destination is a coastal area or a beach resort >>>,
    - mountain: <<< if the destination includes mountainous regions or hills >>>,
    - city: <<< if the destination is an urban area or city center >>>.

    Travel Style:
    - luxury: <<< if the travel plan includes high-end accommodations and services >>>,
    - budget: <<< if the travel plan is cost-effective and economical >>>,
    - adventure: <<< if the travel plan includes adventurous activities like hiking or trekking >>>.

    Activities:
    - cultural: <<< if the plan includes visiting historical sites or engaging in local culture >>>,
    - sightseeing: <<< if the plan includes visiting popular tourist attractions >>>,
    - adventure: <<< if the plan includes activities like trekking, diving, or extreme sports >>>.

    Duration:
    - short: <<< if the trip is planned for a weekend or a few days >>>,
    - medium: <<< if the trip lasts for a week >>>,
    - long: <<< if the trip is planned for two weeks or more >>>.
    {delimiter}

    {delimiter}
    Here is input output pair for few-shot learning:
    input 1: "I want to go to a beach destination for a short trip with cultural activities on a budget."
    output 1: {{'Destination Type': 'beach', 'Travel Style': 'budget', 'Activities': 'cultural', 'Duration': 'short'}}

    {delimiter}
    ### Strictly don't keep any other text in the values of the JSON dictionary other than defined types ###
    """
    input = f"""Follow the above instructions step-by-step and output the dictionary in JSON format {travel_spec} for the following travel description {travel_description}."""
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": input}]

    response = get_chat_completions(messages, json_format=True)

    return response

def compare_travel_options_with_user(user_req_string):
    travel_df = pd.read_csv('updated_travel_options.csv')

    response_dict_n = dictionary_present(user_req_string)
    user_requirements = response_dict_n

    # Extracting user requirements from the input string (assuming it's a dictionary)
    budget = int(user_requirements.get('Budget', '0').replace(',', '').split()[0])

    # Creating a copy of the DataFrame and filtering travel options based on the budget
    filtered_travel_options = travel_df.copy()
    filtered_travel_options['Price'] = filtered_travel_options['Price'].str.replace(',', '').astype(int)
    filtered_travel_options = filtered_travel_options[filtered_travel_options['Price'] <= budget].copy()

    # Mapping string values to numerical scores
    mappings = {
        'beach': 0, 'mountain': 1, 'city': 2,
        'luxury': 0, 'budget': 1, 'adventure': 2,
        'cultural': 0, 'sightseeing': 1,
        'short': 0, 'medium': 1, 'long': 2
    }

    # Creating a new column 'Score' in the filtered DataFrame and initializing it to 0
    filtered_travel_options['Score'] = 0

    # Iterating over each travel option in the filtered DataFrame to calculate scores based on user requirements
    for index, row in filtered_travel_options.iterrows():
        user_product_match_str = row['travel_feature']
        travel_values = user_product_match_str
        travel_values = dictionary_present(user_product_match_str)
        score = 0

        # Comparing user requirements with travel features and updating scores
        for key, user_value in user_requirements.items():
            if key == 'Budget':
                continue  # Skipping budget comparison
            travel_value = travel_values.get(key, None)
            travel_mapping = mappings.get(travel_value, -1)
            user_mapping = mappings.get(user_value, -1)
            if travel_mapping >= user_mapping:
                score += 1  # Incrementing score if travel option meets or exceeds user value

        filtered_travel_options.loc[index, 'Score'] = score  # Updating the 'Score' column in the DataFrame

    # Sorting travel options by score in descending order and selecting the top 3 products
    top_travel_options = filtered_travel_options.drop('travel_feature', axis=1)
    top_travel_options = top_travel_options.sort_values('Score', ascending=False).head(3)
    top_travel_options_json = top_travel_options.to_json(orient='records')  # Converting the top travel options DataFrame to JSON format

    return top_travel_options_json

def recommendation_validation(travel_recommendation):
    data = json.loads(travel_recommendation)
    data1 = []
    for i in range(len(data)):
        if data[i]['Score'] > 2:
            data1.append(data[i])

    return data1

def initialize_conv_reco(travel_options):
    system_message = f"""
    You are an intelligent travel advisor and you are tasked with the objective to \
    solve the user queries about any travel options in the user message. \
    You should keep the user profile in mind while answering the questions.\

    Start with a brief summary of each travel option in the following format, in decreasing order of price:
    1. <Destination Name> : <Major specifications of the travel option>, <Price in INR>, <Rating>  
    2. <Destination Name> : <Major specifications of the travel option>, <Price in INR>, <Rating>  
    3. <Destination Name> : <Major specifications of the travel option>, <Price in INR>, <Rating>
    """
    
    # Setting the travel options to system messages for processing
    travel_options_json = json.loads(travel_options)

    travel_options_message = ""
    for option in travel_options_json:
        travel_options_message += f"{option['Destination Name']}: {option['Description']}, {option['Price']} INR, {option['Rating']}\n"

    return travel_options_message