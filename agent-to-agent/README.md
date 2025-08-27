# HelloWorld A2A Agent – Salesforce MCP Integration

This project implements an **Agent-to-Agent (A2A) architecture** that connects an **LLM-backed HelloWorld Agent** to **Salesforce MCP (Model Context Protocol)** resources. The system is designed to handle natural language inputs from clients, orchestrate them via an LLM, and fetch structured results from Salesforce.

---

## 🔹 Architecture Overview

### Components

1. **A2A Client**
   - Sends **JSON-RPC POST requests** to the HelloWorld Agent server.
   - Example:  
     ```json
     {
       "id": "123",
       "type": "user",
       "content": "Give me product catalog"
     }
     ```

2. **HelloWorld Agent Server**
   - Built with **FastAPI** (`__main__.py`).
   - Routes user requests to the `HelloWorldAgentExecutor`.
   - Maintains an **EventQueue** for streaming responses.

3. **HelloWorldAgentExecutor**
   - Logs user input.
   - Delegates task execution to the `LLMBackedAgent`.
   - Streams results back to the client.

4. **LLMBackedAgent**
   - **Discovers resources** from Salesforce MCP using a `resources/list` JSON-RPC POST.
   - **Calls an LLM** (e.g., OpenAI GPT) to interpret user intent and decide which resource to invoke.
   - **Executes resources** via Salesforce MCP using JSON-RPC POST requests (`resources/read`).
   - **Streams results** back into the `EventQueue`.

5. **Salesforce MCP Server**
   - Exposes MCP endpoints for business resources.
   - Example: `product-catalog`, `order-status`, etc.
   - Returns structured JSON results to the agent.

---

## 🔹 Request Flow

1. **Client → Agent Server**
   - Client sends a user message as JSON-RPC POST.

2. **Agent Server → HelloWorldAgentExecutor**
   - Executor enqueues the message and forwards it to the agent.

3. **Executor → LLMBackedAgent**
   - Agent queries Salesforce MCP for available resources.
   - LLM decides the correct resource to use.

4. **LLMBackedAgent → Salesforce MCP**
   - Agent POSTs a `resources/read` request to Salesforce MCP.
   - MCP responds with structured business data.

5. **Salesforce MCP → Agent → Client**
   - The response is streamed back through the EventQueue to the client.

---

## 🔹 Example Interaction

**User Input:**  
```
Give me product catalog
```

**Agent Flow:**  
1. Discovers `product-catalog` resource from Salesforce MCP.  
2. LLM matches the intent to the `product-catalog` resource.  
3. Executes `resources/read` via Salesforce MCP.  
4. Streams back the structured product catalog as JSON.  

---

## 🔹 Key Files

- `__main__.py`  
  → Starts the FastAPI-based Agent Server.

- `agent_executor.py`  
  → Contains `HelloWorldAgentExecutor` and `LLMBackedAgent`.  
  → Handles LLM orchestration, resource discovery, and execution.

- `test_client.py`  
  → Simple test client for sending messages to the agent.

---

## 🔹 Extending the Agent

To add new Salesforce MCP resources:
1. Expose them in the Salesforce MCP server (Apex REST service).  
2. Ensure they appear in `/resources/list`.  
3. Update LLM prompt templates to recognize new intents.  

---

## 🔹 Future Enhancements
- **Authentication:** Secure MCP endpoints with OAuth2 (Salesforce Connected App).  
- **Advanced Orchestration:** Support multi-step workflows across multiple resources.  
- **Error Handling:** Improve graceful recovery when MCP resources fail.  
- **Caching:** Cache MCP resource lists for faster startup.  

---

## 🚀 Run Instructions

0. Remember to export OPENAI_API_KEY variable or insert it into an .env file
   ```bash
   export OPENAI_API_KEY=sk-.....
   ```

2. Start the A2A Starlette Server with Agent Executor:
   ```bash
   python __main__.py
   ```

3. Start an A2A Agent and send messages:
   ```bash
   python test_client.py
   ```

4. Observe results streamed back from Salesforce MCP discovered by Agent Executor.
