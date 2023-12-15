import streamlit as st
import os 
import requests
from dotenv import load_dotenv
import time
from PIL import Image
load_dotenv()

BASE_URL = os.getenv("BASE_URL")

# Load favicon
favicon = Image.open("assets/Occult.png")

# Page configurations
st.set_page_config(
    page_title="Occult",
    page_icon=favicon,
)

# Page title
st.title("Chat with Occult! 🕵️")

# Sidebar menu
with st.sidebar:
    st.header("Chat with Occult! 🕵️‍♂️")

    # API 🔑 
    api_key = st.text_input(label="API Key", placeholder="Enter your API key here...", type="password")
    if api_key:
        st.success("API key accepted! 🎉")

    # Model settings
    temperature = st.slider(label="Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="temperature")
    top_p = st.slider(label="Top P", min_value=0.0, max_value=1.0, value=0.9, step=0.01, key="top_p")

    # Send API requests to FastAPI server
    if temperature or top_p:
        # Initialise settings JSON for API request
        settings = {
            "temperature": temperature,
            "top_p": top_p
        }

        # Send settings to FastAPI server
        try:
            response = requests.post(BASE_URL + "chat/settings", json=settings)
            if response.status_code == 200:
                st.toast("Settings updated! 🎉")
            else:
                st.toast("Failed to send settings to Occult! 😢")
        except requests.exceptions.RequestException as e:
            st.toast("Failed to send settings to Occult! 😢")
            st.toast(e)

    # Clear chat history button
    def clear_chat(): 
        st.session_state.messages = [
            {
                "role": "assistant", 
                "message": "Ask away and let Occult help you!"
            }
        ]
        # Display "Reset" toast message
        st.toast("Chat history has been cleared! 🗑️")
    st.button(label="Clear my chat history! 🗑️", on_click=clear_chat)

    # Reset Occult button
    def reset_occult():
        # Clear uploads and data folder
        for file in os.listdir("../server/uploads"):
            os.remove(os.path.join("../server/uploads", file))
        for file in os.listdir("../server/data"):
            os.remove(os.path.join("../server/data", file))
    st.markdown("> To clear Occult's memory, click the button below. This will clear all the files in the uploads and data folder.")
    st.button(label="Reset Occult! 🔄", on_click=reset_occult)

# Instructions
with st.expander("Instructions 📜"):
    st.markdown("""
        - Upload your PCAP files to the conversation. 📁
        - Occult will then process your PCAP files and start asking you questions about your network logs. 🤔
        - Chat history becoming too long? Click the "Clear my chat history!" button to clear your chat history. 🗑️
        - If you want to upload new PCAP files or give Occult some new context, click the "Reset Occult!" button to clear Occult's memory. 🔄
    """)

# File upload
uploaded_files = st.file_uploader("Upload your PCAP files here...", type=["pcap", "pcapng"], accept_multiple_files=True)


# Upload file to the server
if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner("Occult is cooking your PCAP files now... (This may take a while!)"):
            file= {"file": uploaded_file}
            try:
                response = requests.post(BASE_URL + "uploads/pcap", files=file)
                filename = response.json()["filename"]
                if response.status_code == 200:
                    st.toast(f"File {filename} uploaded successfully! 🎉")
                else:
                    st.toast(f"File {filename} failed to upload! 😢")
            except requests.exceptions.RequestException as e:
                st.toast(e)

# Chat (Starting message)
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "assistant", 
        "message": "Ask away and let Occult help you!"
    }]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["message"])

# Chat input
prompt = st.chat_input("Ask away! 🤓")

# Accpeting user inputs when API key is provided
# if prompt := st.chat_input(disabled=not api_key):
if prompt := st.chat_input():
    # Append user input to chat history
    st.session_state.messages.append({
        "role": "user", 
        "message": prompt
    })

    # Display user input
    with st.chat_message("user"):
        st.write(prompt)

# Generate LLM response by checking if last message was sent by AI
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Let Occult Cook..."):
            if not uploaded_files:
                response = "Please upload your PCAP files first!"
                st.markdown(response)
            else:
                try:    
                    response = requests.post(BASE_URL + "chat/prompt/send", json={
                        "role": "user", 
                        "message": prompt
                    })
                    
                    if response.status_code == 200:
                        response = response.json()["message"]
                        st.markdown(response)
                    else:
                        st.toast("Occult failed to respond! 😢")
                except requests.exceptions.RequestException as e:
                    st.toast(e)
            st.session_state.messages.append({
                "role": "assistant", 
                "message": response
            })