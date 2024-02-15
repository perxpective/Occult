# Import the required modules
from urllib.request import urlopen
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader, UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import DeepInfra
import os
from dotenv import load_dotenv
load_dotenv()
# Set the environment variables for the DeepInfra and HuggingFaceHub APIs
DEEP_INFRA_API_TOKEN = os.getenv("DEEP_INFRA_API_TOKEN")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Initialize the DeepInfra model with the specified ID and parameters
llm = DeepInfra(model_id="meta-llama/Llama-2-70b-chat-hf")
llm.model_kwargs = {
    "temperature": 0.5,
    "repetition_penalty": 1.2,
    "max_new_tokens": 250,
    "top_p": 0.9,
}

# Define a list of URLs for different malware samples
urls = ['win.gozi','win.isfb','win.originlogger','win.agent_tesla','win.qakbot']

# Open a file to write the links that could not be processed
leftover=open('leftover.txt','w')

# Loop through each URL in the list
for url in urls:
    # Initialize an empty list to store the links for each malware
    links=[]
    # Fetch the HTML content from the Malpedia website for the given malware
    myConnection = urlopen('https://malpedia.caad.fkie.fraunhofer.de/details/'+url).read() #replace link for each malware
    
    # Decode the HTML content and split it by line
    array=myConnection.decode().split('\n')
    # Loop through each line in the HTML content
    for x in array:
        # If the line contains a URL for the malware sample, extract it and append it to the links list
        if "url = {" in x:
            links+=[x[10:-2]+'\n']
    # Loop through each link in the links list
    for link in links:
        # Try to fetch the content from the link
        try:
            myConnection = urlopen(link).read()
            # Define the header bytes for a PDF file
            png_header=bytes.fromhex('25504446')
            # If the content is a PDF file, save it as a temporary file
            if png_header in myConnection:
                temp_file=open('temp.pdf','wb')
                temp_file.write(myConnection)
                temp_file.close()
                # Load the PDF file using the PyPDFLoader module
                file = PyPDFLoader('temp.pdf').load()
                # Delete the temporary file
                os.remove('temp.pdf')
                # Split the PDF file into smaller chunks using the RecursiveCharacterTextSplitter module
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                documents = text_splitter.split_documents(file)
            # If the content is not a PDF file, assume it is an HTML file and save it as a temporary file
            else:
                temp_file=open('temp.html','wb')
                temp_file.write(myConnection)
                temp_file.close()
                # Load the HTML file using the UnstructuredHTMLLoader module
                file = UnstructuredHTMLLoader('temp.html').load()
                # Delete the temporary file
                os.remove('temp.html')
                # Split the HTML file into smaller chunks using the RecursiveCharacterTextSplitter module
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                documents = text_splitter.split_documents(file)
            # Create a Chroma vector store from the documents using the HuggingFaceEmbeddings module
            vdb=Chroma.from_documents(documents,embedding=HuggingFaceEmbeddings(),persist_directory='database')
            # Save the vector store to the specified directory
            vdb.persist()
        # If an error occurs while fetching the content from the link, write the link to the leftover file
        except:
            leftover.write(link)
# Close the leftover file
leftover.close()