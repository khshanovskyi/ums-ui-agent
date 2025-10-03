import json
import logging
from collections import defaultdict
from typing import Any, AsyncGenerator

from openai import AsyncAzureOpenAI

from agent.clients.stdio_mcp_client import StdioMCPClient
from agent.models.message import Message, Role
from agent.clients.http_mcp_client import HttpMCPClient

logger = logging.getLogger(__name__)


class DialClient:
    """Handles AI model interactions and integrates with MCP client"""

    def __init__(
            self,
            api_key: str,
            endpoint: str,
            model: str,
            tools: list[dict[str, Any]],
            tool_name_client_map: dict[str, HttpMCPClient | StdioMCPClient]
    ):
        #TODO:
        # 1. set tools, tool_name_client_map and model
        # 2. Create AsyncAzureOpenAI as `async_openai` with:
        #   - api_key=api_key
        #   - azure_endpoint=endpoint
        #   - api_version=""
        raise NotImplementedError()

    async def response(self, messages: list[Message]) -> Message:
        """Non-streaming completion with tool calling support"""
        #TODO:
        # 1. Create chat completions request (self.async_openai.chat.completions.create) and get it as `response`
        # 2. Create message `ai_message`
        # 3. Check if message contains tool_calls, if yes, then add them as tool_calls
        # 4. If `ai_message` contains tool calls then:
        #       - add `ai_message` to messages
        #       - call `_call_tools(ai_message, messages)`
        #       - make recursive call with messages to process further
        # 5. return ai_message
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message]) -> AsyncGenerator[str, None]:
        """
        Streaming completion with tool calling support.
        Yields SSE-formatted chunks.
        """
        #TODO:
        # 1. Create chat completions request (self.async_openai.chat.completions.create) and get it as `stream`
        # 2. Create empty sting and assign it to `content_buffer` variable (we will collect content while streaming)
        # 3. Create empty array with `tool_deltas` variable name
        # 4. Make async loop through `stream` (async for chunk in stream):
        #       - get delta chunk
        #       - if delta contains content
        #           - create dict:{"choices": [{"delta": {"content": delta.content}, "index": 0, "finish_reason": None}]} as `chunk_data`
        #           - `yield f"data: {json.dumps(chunk_data)}\n\n"`
        #           - concat `content_buffer` with delta content
        #       - if delta has tool calls then extend `tool_deltas` with `delta.tool_calls`
        # 5. If `tool_deltas` are present:
        #       - collect tool calls with `_collect_tool_calls` method and assign to the `tool_calls` variable
        #       - create assistant message with collected content and tool calls
        #       - add created assistant message to `messages`
        #       - call `_call_tools(ai_message, messages)` (its async, don't forget about await)
        #       - make recursive call with messages to process further:
        #           `async for chunk in self.stream_response(messages):
        #               yield chunk
        #            return`
        # 6. Add assistant message with collected content
        # 7. Create final chunk dict: {"choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]}
        # 8. yield f"data: {json.dumps(final_chunk)}\n\n"
        # 9. yield "data: [DONE]\n\n"
        raise NotImplementedError()

    def _collect_tool_calls(self, tool_deltas):
        """Convert streaming tool call deltas to complete tool calls"""
        #TODO:
        # 1. Create `tool_dict` with `defaultdict(lambda: {"id": None, "function": {"arguments": "", "name": None}, "type": None})`
        # 2. Iterate through tool_deltas and:
        #       - get delta index
        #       - if delta has id then add it to `tool_dict[idx]["id"]`
        #       - if delta has name (function.name) the add to `tool_dict[idx]["function"]["name"]`
        #       - if delta has arguments (function.arguments) the add to `tool_dict[idx]["function"]["arguments"]`
        #       - if delta has type then add it to `tool_dict[idx]["type"]`
        # 3. Create list from `tool_dict` values and return it
        raise NotImplementedError()

    async def _call_tools(self, ai_message: Message, messages: list[Message], silent: bool = False):
        """Execute tool calls using MCP client"""
        #TODO:
        # Iterate through ai_message tool_calls:
        # 1. Get tool name from tool call (function.name)
        # 2. Load tool arguments from tool call (function.arguments) through `json.loads`
        # 3. Get MCP client from `tool_name_client_map` via tool name
        # 4. If no MCP Client found then create tool message with info in content that such tool is absent, add it to
        #    `messages`, and `continue`
        # 5. Make tool call with MCP client (its async!)
        # 6. Add tool message with content with tool execution result to `messages`
        raise NotImplementedError()
