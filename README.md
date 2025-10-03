# Users Management Agents

**Create Production ready Agent with Tool use pattern and MCP**

In this task you will need to implement an Agent with classical Tool use patten and connect to several MCP servers:
- We need to support streaming and non-streaming flow
- Will use UI chat with response streaming
- All the conversations must be stored in the Redis storage
- As tools, we will use tools from 3 different MCP Servers
  - UMS MCP: Server that works with UMS Service, we will run it locally from docker-compose
  - Fetch MCP: Remote Server that has tools to fetch WEB content
  - DucDuckGo: Will run it locally (with application start in docker container), provides with WEB Search capabilities
- Auth will be skipped in this task

## 📋 Requirements

- **Python**: 3.11 or higher
- **Dependencies**: Listed in `requirements.txt`
- **API Access**: DIAL API key with appropriate permissions
- **Network**: EPAM VPN connection for internal API access
- Docker and Docker Compose

## Task

### If the task in the main branch is hard for you, then switch to the `with-detailed-description` branch

1. Implement all TODO blocks in [http_mcp_client](agent/clients/http_mcp_client.py)
2. Implement all TODO blocks in [stdio_mcp_client](agent/clients/stdio_mcp_client.py)
3. Implement all TODO blocks in [dial_client](agent/clients/dial_client.py)
4. Implement all TODO blocks in [conversation_manager](agent/conversation_manager.py)
5. Write system prompt, at first it can be simple [prompts](agent/prompts.py)
6. Implement all TODO blocks in [app](agent/app.py)
7. Run [docker-compose](docker-compose.yml) with UMS, UMS MCP and Redis
8. Start application [app](agent/app.py)
9. Open in browser [index.html](index.html) and test your agent

## 🏗️ Architecture

```
├── 📂 agent/
│   │
│   ├── 📂 clients/
│   │   ├── dial_client.py         ⚠️ TODO: implement logic
│   │   ├── http_mcp_client.py     ⚠️ TODO: implement logic
│   │   └── stdio_mcp_client.py    ⚠️ TODO: implement logic
│   ├── 📂 models/
│   │   └── message.py             ✅ Complete
│   ├── app.py                     ⚠️ TODO: implement logic
│   ├── conversation_manager.py    ⚠️ TODO: implement logic
│   └── prompts.py                 ⚠️ TODO: write prompt
├── docker-compose.yml             ✅ Complete
└── index.html                     ✅ Complete
```
### <img src="/flow_diagrams/general_flow.png">
### <img src="/flow_diagrams/chat-agent_communication_flow.png">
### <img src="/flow_diagrams/ui-chat.png">

## Redis insight
- You can connect to Redis Insight by URL http://localhost:6380
- To see the conversations add database with URL `redis-ums:6379`