import os
from typing import List
from fastapi import UploadFile
from app.services.vector_retriever import VectorRetriever

def save_uploaded_files(files: List[UploadFile]) -> List[dict]:
    
    # Directory to save uploaded files
    UPLOAD_DIRECTORY = os.path.join(os.path.dirname(__file__), "documents")

    # Ensure the directory exists
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
        
    file_details = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        file_details.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": os.path.getsize(file_location),
            "location": file_location
        })
        print(f"Uploaded file: {file.filename}, Size: {os.path.getsize(file_location)} bytes")
    
    # Call the vectoriser to create a vector datastore out of the given files.
    VectorRetriever().data_vectoriser()
        
    return file_details