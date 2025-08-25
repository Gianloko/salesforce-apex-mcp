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
    A client for connecting to an MCP (Model Context Protocol) server,
    discovering available tools/resources/prompts, and orchestrating LLM calls.
    """

    def __init__(self, server_url: str):
        """
        Initialize the MCP client.

        Args:
            server_url (str): The base URL of the MCP server.
        """
        self.server_url = server_url
        self.session = None  # HTTP session (aiohttp)
        self.message_id = 0  # Incremental ID for JSON-RPC requests

    async def connect(self):
        """
        Establish a session with the MCP server and discover capabilities.
        """
        self.session = aiohttp.ClientSession()
        print(f"✅ Connected to MCP server at {self.server_url}")

        # Discover server capabilities (tools, resources, prompts)
        await self.send_request("tools/list")
        await self.send_request("resources/list")
        await self.send_request("prompts/list")

    async def send_request(self, method: str, params: dict = None):
        """
        Send a JSON-RPC request to the MCP server.

        Args:
            method (str): The RPC method to call.
            params (dict, optional): Parameters for the method.

        Returns:
            dict | None: The server's JSON response or None if failed.
        """
        self.message_id += 1
        msg_id = str(self.message_id)

        # Construct the JSON-RPC request object
        request = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
        }
        if params:
            request["params"] = params

        # Send POST request to MCP server
        async with self.session.post(
            self.server_url,
            json=request,
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed {method}: {resp.status}")
                return None

            # Parse and pretty-print the JSON response
            response = await resp.json()
            print(f"\n📥 Response for {method}:")
            print(json.dumps(response, indent=2))
            return response

    async def orchestrate_llm(self, prompt: str, model: str = "gpt-4"):
        """
        Call OpenAI's API asynchronously to process a given prompt.

        Args:
            prompt (str): The input text to send to the LLM.
            model (str): The model name (default: gpt-4).

        Returns:
            str: The generated text response from the LLM.
        """
        print(f"\n💬 Sending prompt to OpenAI ({model})...")
        loop = asyncio.get_event_loop()

        # OpenAI SDK call is blocking -> run it in executor to avoid blocking asyncio loop
        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
        )

        # Extract and return the generated response
        output = response.choices[0].message.content
        print(f"\n🤖 OpenAI LLM Output:\n{output}")
        return output

    async def close(self):
        """
        Close the aiohttp session if open.
        """
        if self.session:
            await self.session.close()


async def main():
    """
    Main entry point:
    - Connects to the MCP server
    - Calls OpenAI with an example prompt
    - Cleans up the session
    """
    client = MCPClient(os.getenv("MCP_SERVER_URL"))
    try:
        await client.connect()

        # Example LLM orchestration with OpenAI
        await client.orchestrate_llm("Give me a product catalog.")
    finally:
        await client.close()


if __name__ == "__main__":
    # Run the async main() function
    asyncio.run(main())
