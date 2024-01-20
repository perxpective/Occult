import streamlit as st
from PIL import Image

# Load favicon
favicon = Image.open("assets/Occult.png")

# Page configurations
st.set_page_config(
    page_title="Occult",
    page_icon=favicon,
)

# Page icon and title
st.image("assets/Occult.png", output_format="png", width=140)
st.title("Welcome to Occult! 🕵️")


# Page description
st.markdown("""
    Occult is a proof-of-concept application 🤖 that leverages large language models (LLMs) 🧠 to help log analysts understand their network logs better and more easily! 😀

    ## How To Use Occult?
    1. Navigate to the **Chat 💬** page to start a conversation with Occult!
    2. To get started, upload your PCAP files to the conversation. 📁
    3. Occult will then process your PCAP files and start asking you questions about your network logs. 🤔
    4. If you want to visualise the vast amount of data in your network logs, navigate to the **Data 📊** page to view the results of Occult's analysis of your network logs in the form of visible diagrams! 📈
            
    ## What Can I Ask Occult?
    Occult is trained and prompt engineered to be knowledgeable about network logs and security. 🔒
    
    Using Cyber Threat Intelligences (CTIs) from [Mitre ATT&CK](https://attack.mitre.org/) fed into our model, Occult can help detect and identify malicious activities in your network logs. 🤯
            
    The list goes on and on! 🤩 It's up to you to explore and find out what Occult can do for you! 🤓
""")

with st.expander("You can ask Occult some questions like... 🤔"):
    st.markdown(""" 
        - What is the source IP address?
        - What is the destination IP address?
        - Can you generate a summary of what happened in the network from the logs?
        - Can you generate some statistics about the network logs?
        - Can you generate a graph of the network logs?
        - Can you identify any malicious activities in the network logs?
        - Can you identify any suspicious activities in the network logs?
        - Can you identify any anomalies in the network logs?
    """)