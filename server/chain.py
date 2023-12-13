"""
Important Libraries to install before working on
!pip install langchain
!pip install faiss-gpu
!pip install faiss-cpu
!pip install transformers
!pip install pandas
!pip install CSV
!pip install scapy
!pip install numpy
!pip install sentence-transformers
"""
import csv
import os
from scapy.all import rdpcap, PacketList

# Extract important pcap fields to be added into a csv files
def extract_pcap_fields(pcap_file):
    packets = rdpcap(pcap_file)

    extracted_fields = []
    empty_field = 0  # Value to use for empty fields

    for i, packet in enumerate(packets, 1):
        print(packet)
        entry = {
            'frame_number': i,
            'src_mac': packet.src,
            'dst_mac': packet.dst,
            'eth_type': packet.type,
            'src_ip': packet['IP'].src if packet.haslayer('IP') else empty_field,
            'dst_ip': packet['IP'].dst if packet.haslayer('IP') else empty_field,
            'ip_proto': packet['IP'].proto if packet.haslayer('IP') else empty_field,
            'ip_ttl': packet['IP'].ttl if packet.haslayer('IP') else empty_field,
            'src_port': packet['TCP'].sport if packet.haslayer('TCP') else packet['UDP'].sport if packet.haslayer('UDP') else empty_field,
            'dst_port': packet['TCP'].dport if packet.haslayer('TCP') else packet['UDP'].dport if packet.haslayer('UDP') else empty_field,
            'tcp_flags': packet['TCP'].flags if packet.haslayer('TCP') else empty_field,
            'packet_time': packet.time,
            'packet_length': len(packet)
        }
        extracted_fields.append(entry)
    return extracted_fields


# Writing all the extracted fields above to a csv file 
def write_to_csv(extracted_fields, csv_file):
    # Check if the CSV file exists, and create it if not
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = extracted_fields[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the file doesn't exist, write the header row
        if not file_exists:
            writer.writeheader()

        # Write the data rows
        writer.writerows(extracted_fields)


import faiss
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
os.environ['HUGGINGFACEHUB_API_TOKEN'] = "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"
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings

def split_csv(csv_file):
    csvLoader = CSVLoader(csv_file)
    csvdocs = csvLoader.load()
    return csvdocs

import os
os.environ["DEEPINFRA_API_TOKEN"] = 'o509gx7p1KfJZpwbMfwrLelEajKD4cK3'
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
from langchain.llms import DeepInfra
from langchain.chains import RetrievalQA
from langchain.schema import retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
import sentence_transformers


if __name__ == "__main__":
    #Input the pcap file
    pcap_file = '/content/2023-01-Unit42-Wireshark-quiz.pcap' # Pls modify this as needed
    extracted_fields = extract_pcap_fields(pcap_file)

    # Define the output CSV file name 
    output_csv_file = '/content/output.csv' # Pls modify this as needed

    # Write the extracted data to the CSV file
    write_to_csv(extracted_fields, output_csv_file)

    # Split the CSV docs according to its header
    csv_docs = split_csv(output_csv_file)

    #Split context files
    

    # Embedding the csv chunks into local vector store
    embeddings = HuggingFaceEmbeddings()
    vectorStore = FAISS.from_documents(csv_docs, embedding=embeddings)

    # LLM Settings
    llm = DeepInfra(model_id="meta-llama/Llama-2-70b-chat-hf")
    llm.model_kwargs = {
        "temperature": 0.7,
        "repetition_penalty": 1.2,
        "max_new_tokens": 250,
        "top_p": 0.9,
    }

    # Retrieving the vector store so that the LLM can use
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorStore.as_retriever()
    )




# Prompt Template (If needed pls modify the template below)

from langchain import PromptTemplate
template = """
You are an AI network security pcap analyzer. You will be given a network capture(pcap) in CSV format.
Your tasks will be to analyse the CSV and answer user questions and do not answer any question twice.
Question: {query}

Answer: 
"""
prompt_template = PromptTemplate(
    input_variables=["query"],
    template=template
)

# Querying the LLm 
query = "Help me classify it using the mitre attack framework?"
chain.run(prompt_template.format(query=query))
