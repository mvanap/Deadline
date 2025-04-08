import streamlit as st
import os
from DocumentQnA import DocumentQnA
from pathlib import Path
import shutil
import time
import yaml
import streamlit_authenticator as stauth



@st.cache_resource
def generate_object(filedata):
    print("generated")
    documentQnA = DocumentQnA()
    return documentQnA

def generate_response(filepath, message):
    obj = generate_object(uploaded_file.getvalue())
    print("Isvec", obj.vectorized)
    response = obj.final(filepath, message)
    return response

def stream_data(data):
    for char in [x for x in data]:
        time.sleep(0.007)
        yield char
try:
    st.set_page_config(page_title='🦜🔗 Ask the Doc App', layout='wide')
    st.markdown(
        """
        <style>
            .stApp {
                background-image: url("app/static/bg.png");
                background-repeat: no-repeat;
                background-size: cover;
                z-index: 5
            }
            .stBottom > div{
                background-color: rgba(0,0,0,0.4);
            }
            .stAppHeader{
                background: rgba(0,0,0,0.4);
                z-index: 10;
            }
            .stSidebar {
                background-color: rgba(0,0,0,0.4);
                z-index: 50
            }
        </style>
        """,
        unsafe_allow_html=True
    )


    st.title('🦜🔗 Ask the Doc App')

    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=yaml.loader.SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    if st.session_state['authentication_status']:
        with st.sidebar:
            st.subheader(f'Welcome *{st.session_state["name"]}*!')
            authenticator.logout()
            st.divider()

    data = authenticator.login()

    if(data):
        name, st.session_state.authentication_status, username = data


    if st.session_state['authentication_status']:
        uploaded_file = st.sidebar.file_uploader('Upload an article', type='pdf', key='file')
        file_name = ""

        if uploaded_file:
            print("parsing!")
            loc = Path('tmp')
            loc.mkdir(exist_ok=True)
            loc = os.path.join(loc, uploaded_file.name)

            with open(loc, "wb") as file:
                file.write(uploaded_file.getvalue())
                file_name = uploaded_file.name

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message['content'])

        query_text = st.chat_input(placeholder = 'Ask a question', disabled=not uploaded_file)

        result = []
        if query_text:
            with st.chat_message("user"):
                st.markdown(f"You: {query_text}")

            st.session_state.messages.append({"role": "user", "content": f"You: {query_text}"})

            with st.spinner('Calculating...'):
                response = generate_response(os.path.join(os.getcwd(),'tmp', file_name), query_text)
                result.append(response)
                with st.chat_message("assistant"):
                    # st.markdown(response)
                    # time.sleep(10000)
                    st.write_stream(stream_data(response))

                st.session_state.messages.append({"role": "assistant", "content": response})

        if len(result):
            st.info(response)
    elif st.session_state['authentication_status'] is False:
        st.error("Username or password is incorrect")

    elif st.session_state['authentication_status'] is None:
        st.warning("Please enter your username and password")
except Exception as e:
    st.error(e)

@st.fragment
def clear():
    print("Clearing...")
    if(not st.session_state.get("file")):
        print('exiting session')
        shutil.rmtree('./tmp', ignore_errors=True)
        st.stop()

clear()