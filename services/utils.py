import os, logging, asyncio
from typing import Callable, Any, Dict, List, Optional, Sequence, Union, Literal
from pydantic import BaseModel
from fastapi import HTTPException, status, WebSocket
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult


SENDER_USER = "user"
SENDER_AGENT = "agent"
MESSAGE_STREAM_START = "stream_start"
MESSAGE_STREAM_TOKEN = "stream_token"
MESSAGE_STREAM_END = "stream_end"
MESSAGE_ERROR = "error"
MESSAGE_NORMAL = "message"
MESSAGE_PING = "ping"

class ChatResponse(BaseModel):
    """Chat response schema."""

    sender: Literal["user", "agent"]
    message: str
    type: Literal["stream_start", "stream_token", "stream_end", "error", "message", "ping"]


async def send_ping(websocket: WebSocket):
    while True:
        logging.info("SERVER: SEND_PING")
        try:
            await websocket.send_json(
                ChatResponse(sender=SENDER_USER, message="PINGPINGPING", type=MESSAGE_PING).dict()
            )
        except:
            logging.info("WebSocketDisconnect - PING Finishing")
            return
        await asyncio.sleep(30)

class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket):
        self.websocket = websocket
        
    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        # logging.info("on_llm_start", serialized, prompts, kwargs, "\n")
        resp = ChatResponse(sender=SENDER_AGENT, message="", type=MESSAGE_STREAM_START)
        await self.websocket.send_json(resp.dict())

    async def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List[Any]], **kwargs: Any
    ) -> Any:
        """Run when Chat Model starts running."""
        logging.info("on_chat_model_start", messages, kwargs, "\n")
        resp = ChatResponse(sender=SENDER_AGENT, message="", type=MESSAGE_STREAM_START)
        await self.websocket.send_json(resp.dict())

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        # logging.info("on_llm_new_token", token)
        resp = ChatResponse(sender=SENDER_AGENT, message=token, type=MESSAGE_STREAM_TOKEN)
        await self.websocket.send_json(resp.dict())

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        logging.info("on_llm_end", kwargs, "\n")
        resp = ChatResponse(sender=SENDER_AGENT, message="", type=MESSAGE_STREAM_END)
        await self.websocket.send_json(resp.dict())

    async def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        logging.info("on_llm_error", error, "\n")