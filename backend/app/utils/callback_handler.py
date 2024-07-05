import logging
from langchain.callbacks.base import AsyncCallbackHandler
from fastapi import WebSocket

class WebSocketStreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.logger = logging.getLogger(__name__)

    async def on_llm_new_token(self, token:str, **kwargs):
        try:
            if isinstance(token, str):
                await self.websocket.send_text(token)
            else:
                self.logger.warning(f"Received non-string token: {token}")
        except Exception as e:
            self.logger.error(f"Error sending token to WebSocket: {e}")
            print(f"Error sending token to WebSocket: {e}")