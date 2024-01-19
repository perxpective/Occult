from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from langchain.prompts   import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.vectorstores import Chroma
from langchain.llms import DeepInfra
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
from langchain.vectorstores import Chroma
import chromadb.utils.embedding_functions as embedding_functions
import time

# Import functions from chain.py
import chain

# Load environment variables
load_dotenv()

# Import environment variables
DEEP_INFRA_API_TOKEN = os.getenv("DEEP_INFRA_API_TOKEN")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Embeddings
embeddings = HuggingFaceEmbeddings()



# Initialize FastAPI
app = FastAPI(title="Occult", version="0.1.0")

# LLM configurations
llm = DeepInfra(model_id="meta-llama/Llama-2-70b-chat-hf")
llm.model_kwargs = {
    "temperature": 0.5,
    "repetition_penalty": 1.2,
    "max_new_tokens": 250,
    "top_p": 0.9,
}

# Initialize chain and vector store
vector_store = Chroma(persist_directory="./../database", embedding_function=embeddings)
lang_chain = RetrievalQA.from_chain_type(
    llm=llm, 
    retriever=vector_store.as_retriever()
    )

# Prompt Template
# You are an AI network security pcap analyzer named Occult. You will be given a network capture (pcap) in CSV format.
# Your tasks will be to analyse the CSV and answer user questions and do not answer any question twice.
template = """
You are an AI network security pcap analyzer named Occult. You have been given a network capture (pcap) in CSV format and some CTI data.
You will answer user questions regarding the network capture. Try to give a conclusive answer, do not beat around the bush. Do not refer to the CTI data when the user asks network capture related questions.
Look for answers in various columns like protocol_name, packet_information and etc.
Question: {query}
Answer: 
"""

prompt_template = PromptTemplate(
    input_variables=["query"],
    template=template
)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Declare classes for API request and response
class ChatPrompt(BaseModel):
    role: str
    message: str

class LLMSettings(BaseModel):
    temperature: float
    top_p: float

# API for retrieving file uploads
@app.get("/uploads")
async def get_uploads():
    # Get all files in uploads folder
    uploads = []
    for file in os.listdir("uploads"):
        uploads.append(file)

    return {
        "message": "Retrieved uploads successfully!",
        "uploads": uploads
    }

# API for PCAP file upload
@app.post("/uploads/pcap")
async def upload_pcap(file: UploadFile = File(...)):
    # Set folder path to save PCAP file
    upload_folder = Path("uploads")
    upload_folder.mkdir(parents=True, exist_ok=True)

    print("File received: " + str(file.filename))
    
    # Check filetype of uploaded file
    if not (str(file.filename).endswith(".pcap") or str(file.filename).endswith(".pcapng")):
        return JSONResponse(
            status_code = 415, 
            content = {
                "message": "Filetype not supported."
            }
        )

    # Save uploaded file
    file_path = upload_folder / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    # Process PCAP file (getting common fields using scapy)
    extracted_fields = chain.extract_pcap_fields(str(file_path))

    # Convert PCAP to CSV file in data folder
    csv_filename = str(Path("data") / str(file.filename).replace(".pcap", ".csv").replace(".pcapng", ".csv"))
    print("Created new CSV file:", csv_filename)

    # Write the extracted data to the CSV file (without info)
    chain.write_to_csv(extracted_fields, csv_filename)


    csv_filename_info = f"{csv_filename}_info.csv"
    chain.extract_pcap_info(str(file_path),csv_filename_info)

    chain.merge_csv_files(csv_filename, csv_filename_info, "frame_number", csv_filename)
    time.sleep(5)


    # Iterate through all CSV files in data folder
    csv_files = Path("data").glob("*.csv")
    print(f"CSV files found in data folder: {csv_files}")

    global vector_store
    
    for csv_file in csv_files:
        vector_store = Chroma.from_documents(chain.split_csv(csv_file), embedding=embeddings, persist_directory="./../database")

    global lang_chain
    lang_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
    
    return {
        "message": "File uploaded and processed successfully!",
        "filename": file.filename,
        "filetype": file.content_type,
        "filepath": str(file_path),
    }

# API to receive chat prompt and return a LLM generated response
@app.post("/chat/prompt/send")
async def receive_prompt(chat_prompt: ChatPrompt):
    # Process chat message with LLM
    received_message = chat_prompt.message
    print(f"User Message Received: {received_message}")

    global vector_store
    print("Initializing chain...")

    # Process chat message with LLM
    global lang_chain
    response_message = lang_chain.run(prompt_template.format(query=received_message))
    print("Response Messsage Sent:", response_message)

    # Return chat prompt
    reply = {
        "role": "assistant",
        "message": response_message
    }
    return reply

# API to configure LLM settings
@app.put("/chat/settings")
async def configure_llm(settings: LLMSettings):
    # Update LLM settings
    llm.model_kwargs = {
        "temperature": settings.temperature,
        "top_p": settings.top_p,
        "repetition_penalty": 1.2,
        "max_new_tokens": 250,
    }

    return {
        "message": "Updated LLM settings successfully!",
        "temperature": settings.temperature,
        "top_p": settings.top_p
    }

# API to clear uploads and data folder
@app.delete("/uploads/clear")
async def clear_uploads():
    # Clear uploads and data folder
    for file in os.listdir("uploads"):
        os.remove(os.path.join("uploads", file))
    for file in os.listdir("data"):
        os.remove(os.path.join("data", file))

    return {
        "message": "Cleared uploads and data folder successfully!"
    }