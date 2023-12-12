from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import functions from chain.py (to process user prompt with LLM)
import chain 

# Initialize FastAPI
app = FastAPI(title="Occult", version="0.1.0")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Declare chat prompt model
class ChatPrompt(BaseModel):
    role: str
    message: str

# API for PCAP file upload
@app.post("/uploadpcap")
async def upload_pcap(file: UploadFile = File(...)):
    return {
        "message": "File uploaded successfully!",
        "file_uploaded": file.filename.replace(" ", "_")
    }

# API to receive chat prompt
@app.post("/chat/prompt/receive")
async def receive_prompt(chat_prompt: ChatPrompt):
    # Process chat message with LLM
    chat_prompt.role = "Assistant"
    received_message = chat_prompt.message
    processed_message = received_message

    # Return chat prompt
    reply = {
        "prompt": chat_prompt.role,
        "message": processed_message
    }
    return reply