import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from agent.clients.dial_client import DialClient
from agent.clients.http_mcp_client import HttpMCPClient
from agent.clients.stdio_mcp_client import StdioMCPClient
from agent.conversation_manager import ConversationManager
from agent.models.message import Message

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

conversation_manager: Optional[ConversationManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MCP clients, Redis, and ConversationManager on startup"""
    global conversation_manager

    logger.info("Application startup initiated")

    #TODO:
    # 1. Create empty list with dicts with name `tools`
    # 2. Create empty dict with name `tool_name_client_map` that applies as key `str` and sa value `HttpMCPClient | StdioMCPClient`
    # 3. Create HttpMCPClient for UMS MCP, url is "http://localhost:8005/mcp" (HttpMCPClient has static method create,
    #    don't forget that it is async and you need to await)
    # 4. Get tools for UMS MCP, iterate through them and add it to `tools` and and to the `tool_name_client_map`, key
    #    is tool name, value the UMS MCP Client
    # 5. Do the same as in 3 and 4 steps for Fetch MCP, url is "https://remote.mcpservers.org/fetch/mcp"
    # 6. Create StdioMCPClient for DuckDuckGo, docker image name is "mcp/duckduckgo:latest", and do the same as in 4th step
    # 7. Initialize DialClient with:
    #       - api_key=os.getenv("DIAL_API_KEY")
    #       - endpoint="https://ai-proxy.lab.epam.com"
    #       - model, here choose gpt-4o or claude-3-7-sonnet@20250219, would be perfect if you test it with both of them later
    #       - tools=tools
    #       - tool_name_client_map=tool_name_client_map
    # 8. Create Redis client (redis.Redis) with:
    #       - host=os.getenv("REDIS_HOST", "localhost")
    #       - port=int(os.getenv("REDIS_PORT", 6379))
    #       - decode_responses=True
    # 9. ping to redis to check if its alive (ping method in redis client)
    # 10. Create ConversationManager with DIAL clien and Redis client and assign to `conversation_manager` (global variable)
    yield


app = FastAPI(
    #TODO: add `lifespan` param from above, like:
    # - lifespan=lifespan
)
app.add_middleware(
    #TODO:
    # Since we will run it locally there will be some issues from FrontEnd side with CORS, and its okay for local setup to disable them:
    #   - CORSMiddleware,
    #   - allow_origins=["*"]
    #   - allow_credentials=True
    #   - allow_methods=["*"]
    #   - allow_headers=["*"]
)


# Request/Response Models
class ChatRequest(BaseModel):
    message: Message
    stream: bool = True


class ChatResponse(BaseModel):
    content: str
    conversation_id: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class CreateConversationRequest(BaseModel):
    title: str = None

# Endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "conversation_manager_initialized": conversation_manager is not None
    }


@app.post("/conversations")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation"""
    #TODO:
    # 1. Check if `conversation_manager` is present, if not then raise HTTPException(status_code=503, detail="Service not initialized")
    # 2. return result of `conversation_manager` create conversation with request title (it is async, don't forget about await)
    raise NotImplementedError()


@app.get("/conversations")
async def list_conversations():
    """List all conversations sorted by last update time"""
    #TODO:
    # 1. Check if `conversation_manager` is present, if not then raise HTTPException(status_code=503, detail="Service not initialized")
    # 2. Get conversations list with `conversation_manager` (it is async, don't forget about await)
    # 3. Converts dicts to `ConversationSummary` (iterate through it and create `ConversationSummary(**conv_dict)`) and return the result
    raise NotImplementedError()


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    #TODO:
    # 1. Check if `conversation_manager` is present, if not then raise HTTPException(status_code=503, detail="Service not initialized")
    # 2. Get conversation by id with `conversation_manager` (it is async, don't forget about await)
    # 3. If no conversation was found then raise `HTTPException(status_code=404, detail="Conversation not found")`
    # 4. return retrieved conversation
    raise NotImplementedError()


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    #TODO:
    # 1. Check if `conversation_manager` is present, if not then raise HTTPException(status_code=503, detail="Service not initialized")
    # 2. Delete conversation by id with `conversation_manager` (it is async, don't forget about await)
    # 3. If no conversation was returned then raise `HTTPException(status_code=404, detail="Conversation not found")`
    # 4. return `{"message": "Conversation deleted successfully"}`
    raise NotImplementedError()


@app.post("/conversations/{conversation_id}/chat")
async def chat(conversation_id: str, request: ChatRequest):
    """
    Chat endpoint that processes messages and returns assistant response.
    Supports both streaming and non-streaming modes.
    Automatically saves conversation state.
    """
    #TODO:
    # 1. Check if `conversation_manager` is present, if not then raise HTTPException(status_code=503, detail="Service not initialized")
    # 2. Call chat of `conversation_manager` (await the result) with:
    #   - user_message=request.message
    #   - conversation_id=conversation_id
    #   - stream=request.stream
    # 3. If `request.stream` then return `StreamingResponse(result, media_type="text/event-stream")`, otherwise return `ChatResponse(**result)`
    raise NotImplementedError()


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting UMS Agent server")
    uvicorn.run(
        #TODO:
        #  - app
        #  - host="0.0.0.0"
        #  - port=8011
        #  - log_level="debug"
    )