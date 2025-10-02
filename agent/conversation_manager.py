import json
import logging
import os
import uuid
from datetime import datetime, UTC
from typing import Optional, AsyncGenerator

import redis.asyncio as redis

from agent.clients.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

CONVERSATION_PREFIX = "conversation:"
CONVERSATION_LIST_KEY = "conversations:list"


class ConversationManager:
    """Manages conversation lifecycle including AI interactions and persistence"""

    def __init__(self, dial_client: DialClient, redis_client: redis.Redis):
        self.dial_client = dial_client
        self.redis = redis_client
        logger.info("ConversationManager initialized")

    async def create_conversation(self, title: str) -> dict:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()

        conversation = {
            "id": conversation_id,
            "title": title,
            "messages": [],
            "created_at": now,
            "updated_at": now
        }

        await self.redis.set(
            f"{CONVERSATION_PREFIX}{conversation_id}",
            json.dumps(conversation)
        )

        await self.redis.zadd(
            CONVERSATION_LIST_KEY,
            {conversation_id: datetime.now(UTC).timestamp()}
        )

        logger.info(
            "Conversation created",
            extra={
                "conversation_id": conversation_id,
                "title": conversation["title"]
            }
        )

        return conversation

    async def list_conversations(self) -> list[dict]:
        """List all conversations sorted by last update time"""
        logger.debug("Listing all conversations")
        conversation_ids = await self.redis.zrevrange(CONVERSATION_LIST_KEY, 0, -1)

        conversations = []
        for conv_id in conversation_ids:
            conv_data = await self.redis.get(f"{CONVERSATION_PREFIX}{conv_id}")
            if conv_data:
                conv = json.loads(conv_data)
                conversations.append({
                    "id": conv["id"],
                    "title": conv["title"],
                    "created_at": conv["created_at"],
                    "updated_at": conv["updated_at"],
                    "message_count": len(conv["messages"])
                })

        logger.info(
            "Conversations listed",
            extra={"conversation_count": len(conversations)}
        )

        return conversations

    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get a specific conversation"""
        logger.debug("Retrieving conversation", extra={"conversation_id": conversation_id})

        conv_data = await self.redis.get(f"{CONVERSATION_PREFIX}{conversation_id}")
        if not conv_data:
            logger.warning("Conversation not found", extra={"conversation_id": conversation_id})
            return None

        conversation = json.loads(conv_data)
        logger.debug(
            "Conversation retrieved",
            extra={
                "conversation_id": conversation_id,
                "message_count": len(conversation.get("messages", []))
            }
        )

        return conversation

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        logger.info("Deleting conversation", extra={"conversation_id": conversation_id})

        deleted = await self.redis.delete(f"{CONVERSATION_PREFIX}{conversation_id}")
        if deleted == 0:
            logger.warning("Conversation not found for deletion", extra={"conversation_id": conversation_id})
            return False

        await self.redis.zrem(CONVERSATION_LIST_KEY, conversation_id)
        logger.info("Conversation deleted successfully", extra={"conversation_id": conversation_id})

        return True

    async def chat(
            self,
            user_message: Message,
            conversation_id: str,
            stream: bool = False
    ):
        """
        Process chat messages and return AI response.
        Automatically saves conversation state.
        """
        logger.info(
            "Processing chat request",
            extra={
                "conversation_id": conversation_id,
                "stream": stream,
                "message_role": user_message.role
            }
        )

        # Get existing conversation to preserve history
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            logger.error("Conversation not found", extra={"conversation_id": conversation_id})
            raise ValueError(f"Conversation with id {conversation_id} not found")

        messages = [Message(**msg) for msg in conversation["messages"]]
        logger.debug(
            "Loaded conversation history",
            extra={
                "conversation_id": conversation_id,
                "message_count": len(messages)
            }
        )

        if not messages:
            messages.append(
                Message(
                    role=Role.SYSTEM,
                    content=os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT)
                )
            )
            logger.debug("Added system message to new conversation")

        messages.append(user_message)

        if stream:
            return self._stream_chat(conversation_id, messages)
        else:
            return await self._non_stream_chat(conversation_id, messages)

    async def _stream_chat(
            self,
            conversation_id: str,
            messages: list[Message],
    ) -> AsyncGenerator[str, None]:
        """Handle streaming chat with automatic saving"""
        logger.debug("Starting streaming chat", extra={"conversation_id": conversation_id})

        # Send conversation_id first
        yield f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"

        # Stream the response - full_messages will be modified by dial_client
        async for chunk in self.dial_client.stream_response(messages):
            yield chunk

        await self._save_conversation_messages(conversation_id, messages)

        logger.info(
            "Streaming chat completed is finished",
            extra={ "conversation_id": conversation_id}
        )

    async def _non_stream_chat(
            self,
            conversation_id: str,
            messages: list[Message],
    ) -> dict:
        """Handle non-streaming chat"""
        logger.debug("Starting non-streaming chat", extra={"conversation_id": conversation_id})

        ai_message = await self.dial_client.response(messages)

        await self._save_conversation_messages(conversation_id, messages)

        logger.info(
            "Non-streaming chat completed",
            extra={"conversation_id": conversation_id}
        )

        return {
            "content": ai_message.content or "",
            "conversation_id": conversation_id
        }

    async def _save_conversation_messages(
            self,
            conversation_id: str,
            messages: list[Message]
    ):
        """Save or update conversation messages"""
        logger.debug(
            "Saving conversation messages",
            extra={ "conversation_id": conversation_id}
        )

        conv_data = await self.redis.get(f"{CONVERSATION_PREFIX}{conversation_id}")

        conversation = json.loads(conv_data)
        conversation["messages"] = [msg.model_dump() for msg in messages]
        conversation["updated_at"] = datetime.now(UTC).isoformat()
        logger.debug("Updating existing conversation", extra={"conversation_id": conversation_id})

        await self._save_conversation(conversation)

    async def _save_conversation(self, conversation: dict):
        """Internal method to persist conversation to Redis"""
        conversation_id = conversation["id"]

        await self.redis.set(
            f"{CONVERSATION_PREFIX}{conversation_id}",
            json.dumps(conversation)
        )

        await self.redis.zadd(
            CONVERSATION_LIST_KEY,
            {conversation_id: datetime.now(UTC).timestamp()}
        )

        logger.debug(
            "Conversation persisted to Redis",
            extra={
                "conversation_id": conversation_id,
                "message_count": len(conversation.get("messages", []))
            }
        )
