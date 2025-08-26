# Salesforce MCP Server

A Model Context Protocol (MCP) implementation for Salesforce, enabling AI systems to interact with Salesforce CRM data through standardized protocols.

## Overview

The Salesforce MCP Server is an Apex-based implementation that exposes Salesforce functionality through the MCP protocol. This allows AI models and tools to seamlessly access and manipulate CRM data, execute tools, and utilize pre-defined prompts within the Salesforce ecosystem.

## Architecture

The server follows a modular architecture with the following key components:

### Core Components

```
┌───────────────────────┐
│   REST Endpoint       │ ← Entry point (/mcp/*)
│ RestResourceMcpServer │
└──────────┬────────────┘
           │
           v
┌─────────────────────┐
│      Server         │ ← Main orchestrator
│   (MCP Protocol)    │
└──────────┬──────────┘
           │
           ├─── Tools ────────┐
           ├─── Resources ────┼── Pluggable Components
           └─── Prompts ──────┘
```

### Request Flow

1. **HTTP Request** → REST Resource endpoint (`/mcp/*`)
2. **Server Initialization** → Creates MCP server instance with registered components
3. **Method Routing** → Routes MCP protocol methods to appropriate handlers
4. **Component Execution** → Executes tools, reads resources, or processes prompts
5. **JSON Response** → Returns standardized MCP response

## File Structure

### RestResourceMcpServer.cls
The main REST endpoint that handles incoming MCP requests.

**Key Features:**
- Maps to `/mcp/*` URL pattern
- Initializes the MCP server with components
- Registers example tool, resource, and prompt
- Delegates request processing to the Server class

### Server.cls
The core MCP protocol implementation that manages the server lifecycle.

**Key Responsibilities:**
- **Protocol Compliance**: Implements MCP 2025-06-18 specification
- **Component Registry**: Manages tools, resources, and prompts
- **Request Routing**: Routes MCP methods to appropriate handlers
- **Error Handling**: Standardized error responses and exception management
- **JSON Response Generation**: Creates compliant MCP responses

**Supported MCP Methods:**
- `initialize` - Server initialization and capability negotiation
- `resources/list` - List available resources
- `resources/templates/list` - List resource templates
- `resources/read` - Read resource content
- `tools/list` - List available tools
- `tools/call` - Execute a tool
- `prompts/list` - List available prompts
- `prompts/get` - Retrieve prompt content
- `ping` - Health check

### Method.cls
Handles the execution logic for each MCP protocol method.

**Core Methods:**

#### `initialize()`
Performs the MCP handshake, returning:
- Protocol version compatibility
- Server information (name, version, title)
- Available capabilities (tools, resources, prompts)
- Optional server instructions

#### `resourcesList(Boolean retrieveTemplates)`
Returns either static resources or resource templates based on the parameter.

#### `resourcesRead()`
Reads content from a specific resource URI, supporting template-based resource matching.

#### `toolsList()` / `toolsCall()`
Lists available tools and executes tool calls with provided arguments.

#### `promptsList()` / `promptsGet()`
Manages prompt templates and retrieves processed prompt content.

## Component Types

### Tools
Executable functions that perform actions within Salesforce.

**Example**: `LeadTool` - Manages lead operations (create, update, query)

**Structure**:
```apex
global abstract class Tool {
    global abstract String getName();
    global abstract String call(Map<String, Object> arguments);
    global abstract String toJson();
}
```

### Resources
Data sources that can be read by AI systems.

**Example**: `ProductResource` - Exposes product catalog data

**Structure**:
```apex
global abstract class Resource {
    global abstract Boolean isTemplate();
    global abstract Boolean matchesTemplate(String uri);
    global abstract List<Content> read();
    global abstract String toJson();
}
```

### Prompts
Reusable prompt templates with parameter substitution.

**Example**: `CodeReviewPrompt` - Provides code review guidelines

**Structure**:
```apex
global abstract class Prompt {
    global abstract String getName();
    global abstract List<Message> get(Map<String, Object> arguments);
    global abstract String toJson();
}
```

## Error Handling

The server implements comprehensive error handling with:

- **MCP-specific exceptions** (`mcpException`) for protocol violations
- **Standard Salesforce exceptions** for platform errors
- **Structured error responses** with error codes and details
- **Graceful degradation** for partial failures

## Configuration

### Server Setup
```apex
Server server = new Server('1.0.0', 'salesforce-mcp-server', 
                          'Salesforce MCP Server', 
                          'MCP Server to expose CRM data');

// Register components
server.registerTool(new LeadTool());
server.registerResource(new ProductResource());
server.registerPrompt(new CodeReviewPrompt());
```

### Testing the MCP Server

To test the server, use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) tool.

### Connecting to Your Server with MCP Inspector

1. Select **Transport Type**: Streamable HTTP
2. Enter your server URL (e.g., `https://{instance_url}/services/apexrest/mcp`)
3. Click **Connect**

After a successful connection, you'll see the list of available resources, tools, and prompts, as shown in the
screenshot below:

![MCP Inspector](https://i.imgur.com/pkNvuRg.png)

### Connecting to Your Server with a Python client

1. Install dependencies:

```bash
pip install aiohttp
```

2. Run the python MCP Client

```bash
python client/mcp-client.py
```

3. Results
![Terminal Results]([https://i.imgur.com/pkNvuRg.png](https://github.com/Gianloko/salesforce-apex-mcp-server/blob/6a711091c1a171386facab3dab906c82f71b109b/assets/mcp_client_py.jpg))

### Security Considerations (Salesforce MCP Apex Server)
- Uses `global without sharing` for the REST endpoint to allow external access
- Individual components can implement their own sharing rules
- Recommend implementing proper authentication and authorization
- Consider rate limiting for production deployments

## Usage Examples

### Initialize Connection
```json
POST /services/apexrest/mcp/
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

### List Available Tools
```json
POST /services/apexrest/mcp/
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

### Execute a Tool
```json
POST /services/apexrest/mcp/
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "LeadTool",
    "arguments": {
      "action": "create",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com"
    }
  }
}
```

## Deployment

1. **Deploy Apex Classes**: Deploy the server classes to your Salesforce org
2. **Configure Remote Site Settings**: If accessing external resources
3. **Set Up Connected Apps**: For OAuth authentication if needed
4. **Test Endpoints**: Verify the `/services/apexrest/mcp/` endpoint is accessible

## Extending the Server

### Adding New Tools
```apex
global class CustomTool extends Tool {
    global override String getName() {
        return 'CustomTool';
    }
    
    global override String call(Map<String, Object> arguments) {
        // Implementation logic
        return 'Tool execution result';
    }
    
    global override String toJson() {
        // Tool definition in JSON format
    }
}
```

### Adding New Resources
```apex
global class CustomResource extends Resource {
    global override Boolean isTemplate() {
        return true; // or false for static resources
    }
    
    global override List<Content> read() {
        // Resource reading logic
    }
    
    // Other required methods...
}
```

## Protocol Compliance

This implementation follows the MCP specification version `2025-06-18` and supports:

- ✅ Server initialization and capability negotiation
- ✅ Tool listing and execution
- ✅ Resource listing and reading (including templates)
- ✅ Prompt listing and retrieval
- ✅ Structured error responses
- ✅ JSON-RPC 2.0 message format

## Contributing

When extending this server:

1. Follow Salesforce coding standards and best practices
2. Implement proper error handling for all operations
3. Add comprehensive test coverage
4. Document new components and their usage
5. Ensure security and sharing rules are properly configured

## License

This project follows Salesforce's standard licensing terms. Consult your Salesforce licensing agreement for details.

---

For more information about the Model Context Protocol, visit the [MCP specification documentation](https://spec.modelcontextprotocol.io/).
