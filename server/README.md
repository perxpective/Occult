# Occult (Server)
This is the backend server for Occult built with [FastAPI](https://fastapi.tiangolo.com/).

## Outline
- [Occult (Server)](#occult-server)
  - [Outline](#outline)
  - [API Documentation](#api-documentation)
    - [Uploading PCAP Filess](#uploading-pcap-filess)

## API Documentation

### Uploading PCAP Filess
```
POST /uploads/pcap
```
Uploads PCAP files to the server for processing from the Streamlit frontend. The PCAP file is stored in the `uploads` directory.