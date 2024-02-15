# Occult (Server)
This is the backend server for Occult built with [FastAPI](https://fastapi.tiangolo.com/).

## Outline
- [Occult (Server)](#occult-server)
  - [Outline](#outline)
  - [API Documentation](#api-documentation)
    - [Uploading PCAP Files](#uploading-pcap-files)
    - [Receiving Messages and Sending Message Replies](#receiving-messages-and-sending-message-replies)
    - [Configuring LLM Settings](#configuring-llm-settings)
    - [Clearing Occult's Memory](#clearing-occults-memory)
    - [Retrieving CSV Data From the `data` Folder](#retrieving-csv-data-from-the-data-folder)

## API Documentation

### Uploading PCAP Files
```python
@app.post("/uploads/pcap")
```
Uploads PCAP files to the server for processing from the Streamlit frontend. The PCAP file is stored in the `uploads` directory.

Subsequently, the uploaded PCAP files are processed by extracting the fields from them and stored in a CSV file in the `data` directory.

**Request Body**
```json
{
  "file": uploaded_file
}
```

**Response Body**
```json
{
  "message": "File uploaded and processed successfully!",
  "filename": file.filename,
  "filetype": file.content_type,
  "filepath": str(file_path),
}
```

### Receiving Messages and Sending Message Replies
```python
@app.post("/chat/prompt/send")
```
Receives messages from the Streamlit frontend interface and sends them to the FastAPI backend server for processing. 

Using a Retrieval QA library from LangChain, the CSV files uploaded are embedded and indexed into a local vector database to provide the Llama model with context to generate an accurate response.

Once the response is generated, it is sent back to the Streamlit frontend interface to be displayed as a chat message by Occult.

**Request Body**
```json
{
  "role": "user", 
  "message": prompt
}
```

**Response Body**
```json
{
  "role": "assistant",
  "message": response
}
```

### Configuring LLM Settings
```python
@app.put("/chat/settings")
```
Configures the settings for the LLM model. The settings are stored in the form of keyword arguments in the model.

**Request Body**
```json
{
  "temperature": temperature,
  "top_p": top_p
}
```

**Response Body**
```json
{
  "message": "Updated LLM settings successfully!",
  "temperature": settings.temperature,
  "top_p": settings.top_p
}

```

### Clearing Occult's Memory
```python
@app.delete("/uploads/clear")
```
Clears the `uploads` and `data` directories in the backend server. This is so that new context can be uploaded and processed by Occult if the user wishes to do so.

**Response Body**
```json
{
  "message": "Cleared uploads and data folder successfully!"
}
```

### Retrieving CSV Data From the `data` Folder
```python
@app.get("/data/csv")
```
Retrieves the CSV data from the `data` directory and sends it to the Streamlit frontend interface in a dictionary format.

**Response Body**
```json
{
  "message": "Retrieved CSV data successfully!",
  "csv_filenames": csv_filenames,
  "csv_data": csv_data
}
```