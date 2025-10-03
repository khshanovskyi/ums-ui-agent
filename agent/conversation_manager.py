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
        #TODO:
        # 1. Create conversation id `str(uuid.uuid4())`
        # 2. Create current datatime `datetime.now(UTC).isoformat()`
        # 3. Create `conversation` dict with:
        #       - id - conversation_id
        #       - title -title
        #       - messages - []
        #       - created_at - created datatime from 2nd point
        #       - updated_at - created datatime from 2nd point
        # 4. Set conversation in redis (`set` is async, don't forget to await) with:
        #       - f"{CONVERSATION_PREFIX}{conversation_id}"
        #       - json.dumps(conversation)
        # 5. Add conversation in redis (`zadd` is async, don't forget to await) with:
        #       - CONVERSATION_LIST_KEY
        #       - {conversation_id: datetime.now(UTC).timestamp()}
        # 6. Log the conversation info
        # 7. Return conversation
        raise NotImplementedError()

    async def list_conversations(self) -> list[dict]:
        """List all conversations sorted by last update time"""
        #TODO:
        # 1. Get `conversation_ids` with `await self.redis.zrevrange(CONVERSATION_LIST_KEY, 0, -1)`
        # 2. Create empty list as `conversations`
        # 3. Iterate through `conversation_ids` and:
        #       - get conversation from redis, use CONVERSATION_PREFIX before conversation_id (don't forget to await, it is async)
        #       - if conversation is present then:
        #           - load it with json (json.loads)
        #           - add to `conversations` list a dict with:
        #               - id - conv["id"]
        #               - title - conv["title"]
        #               - created_at - conv["created_at"]
        #               - updated_at - conv["updated_at"]
        #               - message_count - len(conv["messages"])
        # 4. return conversations
        raise NotImplementedError()

    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get a specific conversation"""
        #TODO:
        # 1. Get conversation from redis, use CONVERSATION_PREFIX before conversation_id (don't forget to await, it is async)
        # 2. If nothing found then return None
        # 3. Load it with json (json.loads)
        # 4. return conversation
        raise NotImplementedError()

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        #TODO:
        # 1. Call delete conversation in redis, use CONVERSATION_PREFIX before conversation_id (don't forget to await, it is async)
        # 2. Id nothing was deleted then return False, otherwise True
        raise NotImplementedError()

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
        #TODO:
        # 1. Log request
        # 2. Get conversation (use method `get_conversation`)
        # 3. Raise an error that no conversation foud if conversation is not present
        # 4. Get `messages` from conversation, iterate through them and create array with `Message(**msg_data)`
        # 5. If `messages` array is empty it means that it is beginning of the conversation. Add system prompt as 1st message
        # 6. Agge `user_message` to `messages` array
        # 7. If `stream` is true then call `_stream_chat` (without await!), otherwise call `_non_stream_chat` (with await) and return it
        raise NotImplementedError()


    async def _stream_chat(
            self,
            conversation_id: str,
            messages: list[Message],
    ) -> AsyncGenerator[str, None]:
        """Handle streaming chat with automatic saving"""
        #TODO:
        # 1. Send conversation_id first: `yield f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"`
        # 2. Stream the response - full_messages will be modified by dial_client:
        #       `async for chunk in self.dial_client.stream_response(messages):
        #           yield chunk`
        # 3. Save conversation (`_save_conversation_messages` method, don't forget to await)
        raise NotImplementedError()

    async def _non_stream_chat(
            self,
            conversation_id: str,
            messages: list[Message],
    ) -> dict:
        """Handle non-streaming chat"""
        #TODO:
        # 1. Call `await self.dial_client.response(messages)`
        # 2. Save conversation (`_save_conversation_messages` method, don't forget to await)
        # 3. Return dict with:
        #       - "content": ai_message.content or ''
        #       - "conversation_id": conversation_id
        raise NotImplementedError()

    async def _save_conversation_messages(
            self,
            conversation_id: str,
            messages: list[Message]
    ):
        """Save or update conversation messages"""
        #TODO:
        # 1. Get conversation from redis, use CONVERSATION_PREFIX before conversation_id (don't forget to await, it is async)
        # 2. Load it with json (json.loads) as `conversation`
        # 3. Create list with messages dits (use `model_dump` method) and it set `conversation` 'messages'
        # 4. Update `updated_at` time with `datetime.now(UTC).isoformat()` in `conversation`
        # 5. Save it with `_save_conversation` method
        raise NotImplementedError()

    async def _save_conversation(self, conversation: dict):
        """Internal method to persist conversation to Redis"""
        #TODO:
        # 1. Get conversation id
        # 2. Call redis set with:
        #       - f"{CONVERSATION_PREFIX}{conversation_id}"
        #       - json.dumps(conversation)
        # 3. Call redis zadd with:
        #       - CONVERSATION_LIST_KEY
        #       - {conversation_id: datetime.now(UTC).timestamp()}
        raise NotImplementedError()
