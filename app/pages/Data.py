import streamlit as st
import os 
import requests
from dotenv import load_dotenv
import time
from PIL import Image
import pandas as pd
import numpy as np
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

# Page title and description
st.title("Analyse with Occult! 📊")
st.markdown("This page displays the results of Occult's analysis of your PCAP files in the form of visible diagrams which may help you to better visualise your network logs! 📈")

# Display PCAP files stored in the back-end
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

if len(file_uploads) == 0:
    st.markdown("""
        ### Whoops! There aren't any files uploaded yet! 📁
        There's no way for Occult to give you stats if there's nothing to generate stats from! Upload some PCAP files in the chat page to get started!
    """)

else: 
    # Display stats
    st.markdown("## Ocuclt's Data Analysis!")

    # Tabs (Charts or dataframes)
    chart_tab, df_tab = st.tabs(["Charts", "Dataframes"])

    # Tab Contents
    with df_tab:
        try:
            # Display dataframes
            response = requests.get(BASE_URL + "data/csv")
            csv_filenames = response.json()["csv_filenames"]
            csv_files = response.json()["csv_data"]
            for filename, data in zip(csv_filenames, csv_files):
                st.markdown(f"### {filename}")
                st.dataframe(data)
        except requests.exceptions.RequestException as e:
            st.toast("Failed to retrieve dataframes from Occult! 😢")
            st.toast(e)
