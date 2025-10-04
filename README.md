# Users Management Agent

**Create Production ready Agent with Tool use pattern and MCP**

## 📋 Requirements

- **Python**: 3.11 or higher
- **Dependencies**: Listed in `requirements.txt`
- **API Access**: DIAL API key with appropriate permissions
- **Network**: EPAM VPN connection for internal API access
- Docker and Docker Compose

### If the task is hard for you, then switch to the `main` or `with-detailed-description` branch

## Task

In this task you will need to implement an Agent with classical Tool use patten and connect to several MCP servers:
- We need to support streaming and non-streaming flow
- Will use UI chat with response streaming
- All the conversations must be stored in the Redis storage
- As tools, we will use tools from 3 different MCP Servers
    - UMS MCP: Server that works with UMS Service, we will run it locally from docker-compose `http://localhost:8005/mcp"`
    - Fetch MCP: Remote Server that has tools to fetch WEB content `https://remote.mcpservers.org/fetch/mcp`
    - DucDuckGo: Will run it locally (with application start in docker container), provides with WEB Search capabilities `mcp/duckduckgo:latest`
- Since agent is working with PII it seems that we need to handle the cases with Credit card information disclosure
- Run [docker-compose](docker-compose.yml) with UMS, UMS MCP and Redis
- Additionally, support both OpenAiI (GPT) and Anthropic models (two different clients)

## 🏗️ Architecture

Suggestion of how it should work

```
├── 📂 agent/
│   │
│   ├── 📂 clients/
│   │   ├── openai_client.py       ℹ️ Holds logic with connection to OpenAI, tool calling (heart of this Agent)
│   │   ├── http_mcp_client.py     ℹ️ Connects to HTTP Streaming MCP servers (http://localhost:8005/mcp" and Fetch)
│   │   └── stdio_mcp_client.py    ℹ️ Connects to STDIO MCP Servers that will be run locally while client start
│   ├── 📂 models/
│   │   └── message.py             ℹ️ Model with message in OpenAi format
│   ├── app.py                     ℹ️ Main start point with endpoints and management
│   ├── conversation_manager.py    ℹ️ Handles all the actions with Conversations (CRUD), holds AI Client and Redis client
│   └── prompts.py                 ℹ️ Provides System promp for agent
├── docker-compose.yml             ℹ️ Set up to run UMS, UMS MCP and Redis
└── index.html                     ℹ️ Chat UI, should work in streaming mode
```

<img src="/flow_diagrams/general_flow.png" alt="General Flow Diagram" />

<img src="/flow_diagrams/chat-agent_communication_flow.png" alt="Communication Flow" />

<img src="/flow_diagrams/ui-chat.png" alt="UI Chat" />

## Redis insight

- You can connect to Redis Insight by URL http://localhost:6380
- To see the conversations add database with URL `redis-ums:6379`