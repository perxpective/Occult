import streamlit as st
import os 
import requests
from dotenv import load_dotenv
from PIL import Image
import pandas as pd
import pandasai
import io
# from pandasai import PandasAI
from pandasai.llm import GooglePalm
from pandasai import SmartDataframe
import matplotlib.pyplot as plt
import plotly.graph_objects as go



load_dotenv()

# Base URL
BASE_URL = os.getenv("BASE_URL")

# Load favicon
favicon = Image.open("assets/Occult.png")

# Load GooglePalm LLM
llm = GooglePalm(api_key=os.getenv("GOOGLE_API_KEY"))
# pandas_ai = PandasAI(llm=llm)

# Page configurations
st.set_page_config(
    page_title="Occult",
    page_icon=favicon,
)

# Page title and description
st.title("Analyse with Occult! 📊")
st.markdown("This page displays the results of Occult's analysis of your PCAP files in the form of visible diagrams which may help you to better visualise your network logs! 📈")

# Function to get summaries
def get_summaries(prompt):
    # Build prompt
    try:
        summary = requests.post(BASE_URL + "chat/prompt/send", json={
            "role": "system", 
            "message": prompt
        })
        if summary.status_code == 200:
            return summary.json()["message"]
    except requests.exceptions.RequestException as e:
        st.toast("Failed to ask Occult for summary! 😢")
        st.toast(e)

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
    st.markdown("## Occult's Data Analysis!")
    st.markdown("""
        Occult has analysed the data from the PCAP files you have uploaded and has generated some stats for you! You can view the stats in the form of charts or dataframes below!
        
        Some information worth mentioning are:
        - IP addresses
        - MAC addresses
        - Ports
        - Packets
        - Packet Length
                
    """)

    # Tabs (Charts or dataframes)
    chart_tab, df_tab = st.tabs(["Charts", "Dataframes"])
    
    # Display dataframes
    response = requests.get(BASE_URL + "data/csv")
    csv_filenames = response.json()["csv_filenames"]
    csv_datas = response.json()["csv_data"]

    # Dataframe Tab Contents
    with df_tab:
        try:
            for filename, data in zip(csv_filenames, csv_datas):
                st.markdown(f"### {filename}")
                st.dataframe(data)
        except requests.exceptions.RequestException as e:
            st.toast("Failed to retrieve dataframes from Occult! 😢")
            st.toast(e)

    # Charts Tab Contents
    with chart_tab:
        try:
            for filename, data in zip(csv_filenames, csv_datas):
                smart_df = SmartDataframe(data, config={"llm": llm})
                df = pd.DataFrame(data)
                st.markdown(f"### {filename}")
                st.markdown("#### Occult's Summary!")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Packets found", smart_df.chat("How many packets are there in the dataframe altogether?"))
                    st.metric("Average TTL", smart_df.chat("What is the average time to live (TTL) of the packets?"))
                with col2:
                    st.metric("Unique IP Addresses", smart_df.chat("How many unique IP addresses are there in the dataframe?"))
                    st.metric("Average Packet Length", smart_df.chat("What is the average packet length?"))
                with col3:
                    st.metric("Unique MAC Addresses", smart_df.chat("How many unique MAC addresses are there in the dataframe?"))
                    st.metric("Largest Packet Length", smart_df.chat("What is the largest packet length?"))
                with col4:
                    st.metric("Unique Ports", smart_df.chat("How many unique ports are there in the dataframe?"))


                # Bar graph
                st.markdown("### Display a Bar Graph!")
                variable = st.selectbox("Select a variable to plot a bar graph", ("src_mac","dst_mac","eth_type","src_ip","dst_ip","ip_proto","ip_ttl","src_port","dst_port","packet_time","packet_length"), key="0") 
                st.bar_chart(df[variable].value_counts())

        except requests.exceptions.RequestException as e:
            st.toast("Failed to retrieve dataframes from Occult! 😢")
            st.toast(e) 