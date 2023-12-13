from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

# Import functions from chain.py (to process user prompt with LLM)
# import chain

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
    return {
        "message": "File uploaded successfully!",
        "filename": file.filename,
        "filetype": file.content_type,
        "filepath": str(file_path)
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