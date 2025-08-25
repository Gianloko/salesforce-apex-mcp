import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = None
        self.message_id = 0

    async def connect(self):
        self.session = aiohttp.ClientSession()
        print(f"✅ Connected to MCP server at {self.server_url}")

        # Discover capabilities
        await self.send_request("tools/list")
        await self.send_request("resources/list")
        await self.send_request("prompts/list")

    async def send_request(self, method: str, params: dict = None):
        """Send a JSON-RPC request via POST."""
        self.message_id += 1
        msg_id = str(self.message_id)

        request = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
        }
        if params:
            request["params"] = params

        async with self.session.post(
            self.server_url,
            json=request,
            headers={"Content-Type": "application/json"},
        ) as resp:
            if resp.status != 200:
                print(f"❌ Failed {method}: {resp.status}")
                return

            response = await resp.json()
            print(f"\n📥 Response for {method}:")
            print(json.dumps(response, indent=2))

    async def close(self):
        if self.session:
            await self.session.close()


async def main():
    client = MCPClient(os.getenv("MCP_SERVER_URL"))
    try:
        await client.connect()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
