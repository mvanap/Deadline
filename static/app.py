from openai import AzureOpenAI
import pandas as pd
import os
from dotenv import load_dotenv 
from IPython.display import display, HTML
from flask import Flask, redirect, url_for, render_template, request
from functions import *

load_dotenv()
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION") 

#For app user: you need to pass the version configured by the admin 
 
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") #Eg: {BASE_URL}/api/azureai 

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") 


#For App User: use the app-registration key along with the app configuration unique key name eg. app123key-configName, For Api User: Substitute the key generated from Key Config Panel 
 
client = AzureOpenAI() 

app = Flask(__name__)

conversation_bot = []

conversation = initialize_conversation()
introduction = get_chat_completions(conversation)
conversation_bot.append({'bot': introduction})
top_places = None


@app.route("/")
def default_func():
    global conversation_bot, conversation, top_places
    return render_template("index.html", name_xyz = conversation_bot)

@app.route("/end_conv", methods = ['POST', 'GET'])
def end_conv():
    global conversation_bot, conversation, top_places
    conversation_bot = []
    conversation = initialize_conversation()
    introduction = get_chat_completions(conversation)
    conversation_bot.append({'bot': introduction})
    return redirect(url_for('default_func'))

@app.route("/invite", methods = ['POST'])
def invite():
    global conversation_bot, conversation, conversation_reco,top_places
    user_input = request.form["user_input_message"]
    prompt = f"""
    You are an intelligent travel planner expert and your goal is to help users plan the best trip based on their preferences.
    You need to ask relevant questions and understand the user profile by analyzing their responses.
    Your final objective is to fill the values for the different keys ('Destination', 'Accommodation type', 'Travel duration', 'Activities', 'Meal preference', 'Budget') in the python dictionary and be confident of the values.
    These key-value pairs define the user's travel preferences."""
    
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        display("Sorry, this message has been flagged. Please restart your conversation.")
        return redirect(url_for('end_conv'))
    
    if top_places is None:

        conversation.append({"role": "user", "content": user_input + prompt})
        conversation_bot.append({'user': user_input})

        response_assistant = get_chat_completions(conversation)
        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            display("Sorry, this message has been flagged. Please restart your conversation.")
            return redirect(url_for('end_conv'))    


        confirmation = intent_confirmation_layer(response_assistant)

        print("Intent Confirmation Yes/No:",confirmation.get('result'))

        if "No" in confirmation.get('result'):
            conversation.append({"role": "assistant", "content": str(response_assistant)})
            conversation_bot.append({'bot': response_assistant})

        else:
            response = dictionary_present(response_assistant)
            print("WAIT")
            conversation_bot.append({'bot': "Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})

            top_places = compare_travel_options_with_user(response)

            print("top places are", top_places)

            validated_reco = recommendation_validation(top_places)
            if len(validated_reco) == 0:
                conversation_bot.append({'bot': "Sorry, we do not have laptops that match your requirements."})

            conversation_reco = initialize_conv_reco(validated_reco)
            conversation_reco.append({"role": "user", "content": "This is my user profile" + str(validated_reco)})
            recommendation = get_chat_completions(conversation_reco)

            moderation = moderation_check(recommendation)
            if moderation == 'Flagged':
                display("Sorry, this message has been flagged. Please restart your conversation.")
                return redirect(url_for('end_conv'))

            conversation_reco.append({"role": "assistant", "content": str(recommendation)})
            conversation_bot.append({'bot': recommendation})

    else:
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({'user': user_input})

        response_asst_reco = get_chat_completions(conversation_reco)

        moderation = moderation_check(response_asst_reco)
        if moderation == 'Flagged':
            print("Sorry, this message has been flagged. Please restart your conversation.")
            return redirect(url_for('end_conv'))

        conversation.append({"role": "assistant", "content": response_asst_reco})
        conversation_bot.append({'bot': response_asst_reco})

    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

