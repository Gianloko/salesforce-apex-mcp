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
