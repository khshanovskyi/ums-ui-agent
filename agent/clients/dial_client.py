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
        self.tools = tools
        self.tool_name_client_map = tool_name_client_map
        self.model = model
        self.async_openai = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=""
        )
        logger.info(
            "DialClient initialized",
            extra={
                "model": model,
                "endpoint": endpoint,
                "tool_count": len(tools)
            }
        )

    async def response(self, messages: list[Message]) -> Message:
        """Non-streaming completion with tool calling support"""
        logger.debug(
            "Creating non-streaming completion",
            extra={"message_count": len(messages), "model": self.model}
        )

        response = await self.async_openai.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            tools=self.tools,
            temperature=0.0,
            stream=False
        )

        ai_message = Message(
            role=Role.ASSISTANT,
            content=response.choices[0].message.content,
        )
        if tool_calls := response.choices[0].message.tool_calls:
            ai_message.tool_calls = tool_calls
            logger.info(
                "AI response includes tool calls",
                extra={"tool_call_count": len(tool_calls)}
            )

        if ai_message.tool_calls:
            messages.append(ai_message)
            await self._call_tools(ai_message, messages)
            return await self.response(messages)

        logger.debug("Non-streaming completion finished")
        return ai_message

    async def stream_response(self, messages: list[Message]) -> AsyncGenerator[str, None]:
        """
        Streaming completion with tool calling support.
        Yields SSE-formatted chunks.
        """
        logger.debug(
            "Creating streaming completion",
            extra={"message_count": len(messages), "model": self.model}
        )

        stream = await self.async_openai.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            tools=self.tools,
            temperature=0.0,
            stream=True
        )

        content_buffer = ""
        tool_deltas = []

        async for chunk in stream:
            delta = chunk.choices[0].delta

            if delta.content:
                chunk_data = {
                    "choices": [{
                        "delta": {"content": delta.content},
                        "index": 0,
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                content_buffer += delta.content

            if delta.tool_calls:
                tool_deltas.extend(delta.tool_calls)

        if tool_deltas:
            tool_calls = self._collect_tool_calls(tool_deltas)
            logger.info(
                "Streaming response includes tool calls",
                extra={"tool_call_count": len(tool_calls)}
            )

            ai_message = Message(
                role=Role.ASSISTANT,
                content=content_buffer,
                tool_calls=tool_calls
            )

            messages.append(ai_message)
            await self._call_tools(ai_message, messages)

            # Recursively stream the next response
            async for chunk in self.stream_response(messages):
                yield chunk
            return

        # Add final message
        messages.append(
            Message(
                role=Role.ASSISTANT,
                content=content_buffer
            )
        )

        # Send completion signal
        logger.debug("Streaming completion finished")
        final_chunk = {
            "choices": [{
                "delta": {},
                "index": 0,
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"

    def _collect_tool_calls(self, tool_deltas):
        """Convert streaming tool call deltas to complete tool calls"""
        tool_dict = defaultdict(lambda: {"id": None, "function": {"arguments": "", "name": None}, "type": None})

        for delta in tool_deltas:
            idx = delta.index
            if delta.id: tool_dict[idx]["id"] = delta.id
            if delta.function.name: tool_dict[idx]["function"]["name"] = delta.function.name
            if delta.function.arguments: tool_dict[idx]["function"]["arguments"] += delta.function.arguments
            if delta.type: tool_dict[idx]["type"] = delta.type

        collected_tools = list(tool_dict.values())
        logger.debug(
            "Collected tool calls from deltas",
            extra={"tool_count": len(collected_tools)}
        )
        return collected_tools

    async def _call_tools(self, ai_message: Message, messages: list[Message], silent: bool = False):
        """Execute tool calls using MCP client"""
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            client = self.tool_name_client_map.get(tool_name)
            if not client:
                error_msg = f"Unable to call {tool_name}. MCP client not found."
                logger.error(
                    "MCP client not found for tool",
                    extra={"tool_name": tool_name}
                )
                messages.append(
                    Message(
                        role=Role.TOOL,
                        content=f"Error: {error_msg}",
                        tool_call_id=tool_call["id"],
                    )
                )
                continue

            if not silent:
                logger.info(
                    "Calling tool",
                    extra={"tool_name": tool_name, "tool_args": tool_args}
                )

            tool_result = await client.call_tool(tool_name, tool_args)

            messages.append(
                Message(
                    role=Role.TOOL,
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )
