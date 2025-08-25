import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file (for API keys, server URL, etc.)
load_dotenv()

# Initialize the OpenAI client (new v1 SDK interface)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class MCPClient:
    """
    MCP client to discover tools/resources/prompts, orchestrate LLM calls,
    and dynamically execute MCP capabilities (tools or resources).
    """

    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = None
        self.message_id = 0
        self.tools = []
        self.resources = []
        self.prompts = []

    async def connect(self):
        """
        Connect to MCP server and discover tools, resources, and prompts.
        """
        self.session = aiohttp.ClientSession()
        print(f"✅ Connected to MCP server at {self.server_url}")

        # Discover capabilities
        tools_resp = await self.send_request("tools/list")
        self.tools = tools_resp.get("result", {}).get("tools", [])

        resources_resp = await self.send_request("resources/list")
        self.resources = resources_resp.get("result", {}).get("resources", [])

        prompts_resp = await self.send_request("prompts/list")
        self.prompts = prompts_resp.get("result", {}).get("prompts", [])

    async def send_request(self, method: str, params: dict = None):
        """
        Send a JSON-RPC request to the MCP server.
        """
        self.message_id += 1
        msg_id = str(self.message_id)

        request = {"jsonrpc": "2.0", "id": msg_id, "method": method}
        if params:
            request["params"] = params

        async with self.session.post(
            self.server_url,
            json=request,
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed {method}: {resp.status}")
                return None

            response = await resp.json()
            print(f"\n📥 Response for {method}:")
            print(json.dumps(response, indent=2))
            return response

    async def orchestrate_llm(self, prompt: str, model: str = "gpt-4"):
        """
        Call OpenAI LLM with context of available tools/resources.
        LLM must return JSON with fields:
        {
            "type": "tool" | "resource",
            "name": "...",
            "arguments": {...}
        }
        """
        print(f"\n💬 Sending prompt to OpenAI ({model})...")
        loop = asyncio.get_event_loop()

        context = {
            "tools": [t["name"] for t in self.tools],
            "resources": [r["name"] for r in self.resources],
        }

        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an orchestrator. "
                            "Given user request and available MCP tools/resources, "
                            "always respond in pure JSON ONLY with fields: "
                            "'type' ('tool' or 'resource'), 'name', and 'arguments'. "
                            "Use 'arguments' only for tools that require parameters."
                        )
                    },
                    {
                        "role": "assistant",
                        "content": f"Available capabilities:\n{json.dumps(context, indent=2)}"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=300
            )
        )

        output = response.choices[0].message.content.strip()
        print(f"\n🤖 OpenAI LLM Raw Output:\n{output}")

        try:
            instructions = json.loads(output)
            return instructions
        except json.JSONDecodeError:
            print("❌ LLM output is not valid JSON.")
            return None

    async def execute_capability(self, request: dict):
        """
        Execute a tool or resource dynamically based on LLM instructions.
        """
        if not request or "type" not in request or "name" not in request:
            print("⚠️ No valid tool/resource request found.")
            return None

        type_ = request["type"]
        name = request["name"]
        arguments = request.get("arguments", {})

        if type_ == "tool":
            if name not in [t["name"] for t in self.tools]:
                print(f"❌ Tool '{name}' not found in MCP capabilities.")
                return None
            response = await self.send_request(
                "tools/call",
                {"name": name, "arguments": arguments}
            )
            print(f"\n🔧 Tool Execution Result:\n{json.dumps(response, indent=2)}")
            return response

        elif type_ == "resource":
            # Find the resource by name
            resource = next((r for r in self.resources if r["name"] == name), None)
            if not resource:
                print(f"❌ Resource '{name}' not found in MCP capabilities.")
                return None

            # Use the real URI from resource definition
            uri = resource.get("uri")
            response = await self.send_request(
                "resources/read",
                {"uri": uri}
            )
            print(f"\n📦 Resource Fetch Result:\n{json.dumps(response, indent=2)}")
            return response

        else:
            print(f"❌ Unknown capability type: '{type_}'")
            return None

    async def close(self):
        """
        Close the aiohttp session if open.
        """
        if self.session:
            await self.session.close()


async def main():
    """
    Main entry point:
    - Connects to MCP server
    - Orchestrates LLM with available capabilities
    - Executes tool or resource dynamically
    - Closes the session
    """
    client = MCPClient(os.getenv("MCP_SERVER_URL"))
    try:
        await client.connect()

        # Step 1: Ask LLM for instructions
        instructions = await client.orchestrate_llm("Show me the catalog of products.")

        # Step 2: Execute the capability (tool or resource)
        if instructions:
            await client.execute_capability(instructions)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
