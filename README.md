# Salesforce MCP Server

This project implements an **MCP (Model Context Protocol) Server** using **Salesforce Apex REST**.  
It allows AI agents and external MCP clients to interact with Salesforce CRM data via a standardized protocol.

---

## 📌 Overview

- Exposes an **Apex REST Resource** at `/services/apexrest/mcp/*`
- Implements the **MCP protocol** with:
  - **Resources** → access CRM data (e.g., Products, Leads)
  - **Tools** → callable business logic (e.g., LeadTool)
  - **Prompts** → reusable AI prompt templates (e.g., CodeReviewPrompt)
- Provides **protocol-compliant responses** to MCP clients, such as:
  - `initialize`
  - `resources/list`
  - `resources/read`
  - `tools/list`
  - `tools/call`
  - `prompts/list`
  - `prompts/get`
  - `ping`

This allows Salesforce to act as a **MCP-compatible backend** for agents like Claude Desktop, LLM-powered copilots, or any MCP-aware client.

---

## ⚙️ Architecture

```text
MCP Client (Claude, VS Code, etc.)
            │
            ▼
   /services/apexrest/mcp/*
            │
   ┌─────────────────────────────┐
   │ RestResourceMcpServer       │  ← Apex REST entry point
   └─────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │          Server             │  ← Core MCP Server
   │ - Registers Tools           │
   │ - Registers Resources       │
   │ - Registers Prompts         │
   │ - Runs execution flow       │
   └─────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │          Method             │  ← Dispatcher
   │ - Handles protocol methods  │
   │ - Routes to tools/resources │
   │ - Serializes MCP responses  │
   └─────────────────────────────┘

📂 Key Files
1. RestResourceMcpServer

Apex REST entry point

URL: /services/apexrest/mcp/*

Creates and configures the MCP Server:

Registers tools (LeadTool)

Registers resources (ProductResource)

Registers prompts (CodeReviewPrompt)

Invokes server.run() to process the MCP request.

2. Server

Core MCP server implementation.

Responsibilities:

Holds metadata: name, version, title, instructions

Registers:

Tools (registerTool)

Resources (registerResource)

Prompts (registerPrompt)

Executes requests through run()

Handles error responses gracefully.

3. Method

Dispatcher for MCP protocol methods.

Maps MCP methods → Salesforce logic:

initialize → handshake & server capabilities

resources/templates/list → list resource templates

resources/list → list instantiated resources

resources/read → read a specific resource instance

tools/list → list registered tools

tools/call → execute a tool

prompts/list → list prompts

prompts/get → retrieve prompt content

ping → lightweight health check

Returns protocol-compliant JSON responses.

🚀 Usage

Deploy Apex classes into your Salesforce org.

Configure the MCP REST Resource:

Endpoint:

https://yourInstance.salesforce.com/services/apexrest/mcp/


Connect an MCP-compatible client (e.g., Claude Desktop, VSCode extension).

The client can now:

Discover available resources, tools, and prompts

Read Salesforce CRM data via MCP

Call Apex-based tools for custom logic

Use prompt templates hosted in Salesforce

🔧 Extending the Server

You can extend the MCP server by adding:

New Tools
Implement Tool interface and register in RestResourceMcpServer.

New Resources
Implement Resource class to expose Salesforce data (e.g., Accounts, Opportunities).

New Prompts
Implement Prompt to provide structured AI instructions.

Example:

Server server = new Server('1.0.0', 'salesforce-mcp-server');
server.registerTool(new LeadTool());
server.registerResource(new OpportunityResource());
server.registerPrompt(new CustomerEmailPrompt());
server.run();

📜 Supported MCP Methods
Method	Description
initialize	Server handshake & capabilities discovery
resources/templates/list	List resource templates
resources/list	List available resources
resources/read	Read a specific resource
tools/list	List all registered tools
tools/call	Execute a tool with arguments
prompts/list	List available prompts
prompts/get	Retrieve prompt messages
ping	Health check
✅ Example Request / Response

Request:

{
  "id": "1",
  "method": "initialize"
}


Response:

{
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "serverInfo": {
      "name": "salesforce-mcp-server",
      "title": "Salesforce MCP Server",
      "version": "1.0.0"
    },
    "capabilities": {
      "resources": { "listChanged": true },
      "tools": { "listChanged": true },
      "prompts": { "listChanged": true }
    }
  }
}

🧩 Roadmap

 Add OAuth authentication layer

 Expand resource coverage (Accounts, Opportunities)

 Support streaming responses

 Add error catalog for unsupported MCP methods

📖 References

Model Context Protocol (MCP)

Salesforce Apex REST Documentation

🏷 License

This project is provided as-is under the MIT License.


---

Would you like me to also add **example Apex code snippets** for `LeadTool`, `ProductResource`, and `CodeReviewPrompt` in the README so it’s fully illustrative, or should we keep it high-level?

