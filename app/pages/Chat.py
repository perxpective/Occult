import streamlit as st
import os 
import requests
from dotenv import load_dotenv
import time
from PIL import Image
load_dotenv()

# Base URL
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

# Instructions
with st.expander("Instructions 📜"):
    st.markdown("""
        - Upload your PCAP files to the conversation. 📁
        - Occult will then process your PCAP files and start asking you questions about your network logs. 🤔
        - Chat history becoming too long? Click the "Clear my chat history!" button to clear your chat history. 🗑️
        - If you want to upload new PCAP files or give Occult some new context, click the "Reset Occult!" button to clear Occult's memory. 🔄
    """)

with st.expander("PCAP Files in Memory 🧠"):
    # Iterate through all CSV files in uploads folder
    response = requests.get(BASE_URL + "uploads")
    file_uploads = response.json()["uploads"]
    if len(file_uploads) == 0:
        st.markdown("`No files uploaded yet! 📁`")
    else:
        for file in file_uploads:
            st.markdown(f"- {file}")

    # Reset Occult button
    reset_button = st.button(label="Reset Occult's Memory! 🔄", help="This will clear all the files in the uploads and data folder. Ensure that all files in the file upload input are removed before clicking this button!")

    if reset_button:
        try:    
            response = requests.delete(BASE_URL + "uploads/clear")
            if response.status_code == 200:
                uploaded_files = None
                st.toast("Occult has been reset! 🔄")
                st.rerun()
        except requests.exceptions.RequestException as e:
            st.toast("Failed to delete uploads to Occult! 😢")
            st.toast(e)

# Chat input
prompt = st.chat_input("Ask away!")

# File upload form
with st.expander("Upload PCAP Files 📁"):
    with st.form("FileUpload"):
        uploaded_files = st.file_uploader("Upload your PCAP files here...", type=["pcap", "pcapng"], accept_multiple_files=True)
        submit_button = st.form_submit_button(label="Submit files to Occult! 📁", help="This is where you can upload your PCAP files. You can upload multiple files at once!")

# Upload file to the server
if submit_button:
    if len(uploaded_files) == 0:
        st.error("Please upload your PCAP files first!")
    else:
        for uploaded_file in uploaded_files:
            file = {"file": uploaded_file}
            with st.spinner("Uploading file..."):
                try:
                    response = requests.post(BASE_URL + "uploads/pcap", files=file)
                    filename = response.json()["filename"]
                    if response.status_code == 200:
                        st.toast(f"File {filename} uploaded successfully! 🎉")
                        st.rerun()
                    else:
                        st.toast(f"File {filename} failed to upload! 😢")
                except requests.exceptions.RequestException as e:
                    st.toast(e)

# Sidebar menu
with st.sidebar:
    st.header("Chat with Occult! 🕵️‍♂️")

    # API 🔑 
    # api_key = st.text_input(label="API Key", placeholder="Enter your API key here...", type="password")
    # if api_key:
    #     st.success("API key accepted! 🎉")

    # Model settings
    temperature = st.slider(label="Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="temperature")
    top_p = st.slider(label="Top P", min_value=0.0, max_value=1.0, value=0.9, step=0.01, key="top_p")

    update_button = st.button(label="Update settings! 🎛️")

    # Send API requests to FastAPI server
    if update_button:
        # Initialise settings JSON for API request
        settings = {
            "temperature": temperature,
            "top_p": top_p
        }

        # Send settings to FastAPI server
        try:
            response = requests.put(BASE_URL + "chat/settings", json=settings)
            if response.status_code == 200:
                st.toast("Settings updated! 🎉")
                temperature = response.json()["temperature"]
                top_p = response.json()["top_p"]
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

# Accpeting user inputs when API key is provided
# if prompt := st.chat_input(disabled=not api_key):
if prompt := st.chat_input():
    # Display user input
    with st.chat_message("user"):
        st.write(prompt)

    # Append user input to chat history
    st.session_state.messages.append({
        "role": "user", 
        "message": prompt
    })

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
