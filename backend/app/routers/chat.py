from fastapi import APIRouter, WebSocket, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List
import logging
from app.services.save_files import save_uploaded_files 
from app.services.conversational_chain import ConversationalChain

router = APIRouter()

@router.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    file_details = save_uploaded_files(files)
    return JSONResponse(content={"message": "Files uploaded successfully!", "file_details": file_details}, status_code=200)


@router.websocket("/ws/chat")
async def chat_endpoint(
    websocket: WebSocket
):
    await websocket.accept()
    conversational_chain = ConversationalChain(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            logging.info(f"Received data: {data}")
            print(f"Received data: {data}")

            session_id = data.get("session_id")
            user_query = data.get("user_query")
            if not session_id or not user_query:
                logging.error("Missing session_id or user_query in the received data")
                await websocket.send_text("Something went wrong, no session_id or query provided...")
                continue

            try:
                await conversational_chain.handle_user_query(session_id, user_query)
                logging.info("Streaming is completed...")
                print("Streaming is done...")
            except Exception as e:
                logging.error(f"Error in streaming response: {e}")
                await websocket.send_text("Something went wrong...")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await websocket.send_text("An unexpected error occurred")
    finally:
        await websocket.close()
        logging.info("WebSocket connection closed")
