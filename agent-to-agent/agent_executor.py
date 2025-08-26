import asyncio
import json
from openai import OpenAI
import httpx
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

client = OpenAI()


class LLMBackedAgent:
    """
    MCP-style LLM agent:
    - Discovers resources via JSON-RPC POST
    - Uses LLM to orchestrate which resource to call
    - Executes resource via JSON-RPC and streams output to EventQueue
    """

    def __init__(self, mcp_base_url="http://localhost:8888"):
        self.mcp_base_url = mcp_base_url
        self.resources = {}  # {name: uri}

    async def discover_resources(self):
        """Fetch available resources from MCP server using JSON-RPC POST."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "resources/list",
                    "params": {}
                }
                resp = await client.post(self.mcp_base_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                self.resources = {
                    r["name"]: r.get("uri") for r in data.get("result", {}).get("resources", [])
                }
                print(f"[LLMBackedAgent] Discovered resources: {list(self.resources.keys())}")
            except Exception as e:
                print(f"[LLMBackedAgent] Failed to discover resources: {e}")
                self.resources = {}

    async def orchestrate_llm(self, user_message: str) -> dict:
        """Ask LLM which resource to call, returning JSON instructions."""
        system_prompt = (
            "You are an orchestrator. Given the user request and the available MCP resources, "
            "always respond in JSON with fields: type ('resource'), name, and arguments (optional).\n"
            f"Available resources: {list(self.resources.keys())}"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0,
            )
            raw = response.choices[0].message.content.strip()
            if not raw:
                raise ValueError("Empty LLM output")
            instructions = json.loads(raw)
        except Exception:
            # Fallback to first discovered resource
            instructions = {
                "type": "resource",
                "name": list(self.resources.keys())[0] if self.resources else "hello_world"
            }
        return instructions

    async def execute_capability(self, instructions: dict, event_queue: EventQueue):
        """Execute resource using JSON-RPC POST and stream output to EventQueue."""
        name = instructions.get("name")
        uri = self.resources.get(name)
        if not uri:
            # fallback to first resource URI
            uri = list(self.resources.values())[0] if self.resources else "hello_world"
            print(f"[LLMBackedAgent] Resource '{name}' not found, using default URI '{uri}'.")

        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "resources/read",
                    "params": {"uri": uri}
                }
                resp = await client.post(self.mcp_base_url, json=payload)
                resp.raise_for_status()
                result = resp.json()
                # Stream the result to EventQueue
                await event_queue.enqueue_event(new_agent_text_message(json.dumps(result)))
                print(f"[LLMBackedAgent] Streamed result: {result}")
            except Exception as e:
                print(f"[LLMBackedAgent] Failed to execute resource '{name}': {e}")

    async def invoke(self, user_message: str, event_queue: EventQueue):
        """Main entry point: discover resources, orchestrate LLM, execute capability."""
        await self.discover_resources()
        if not self.resources:
            print("[LLMBackedAgent] No resources discovered. Exiting invoke.")
            return
        instructions = await self.orchestrate_llm(user_message)
        await self.execute_capability(instructions, event_queue)


class HelloWorldAgentExecutor(AgentExecutor):
    """
    AgentExecutor using MCP-style LLMBackedAgent:
    - LLM decides which resource to call
    - Streams responses to EventQueue
    """

    def __init__(self):
        self.llm_agent = LLMBackedAgent(mcp_base_url="https://orgfarm-225b06bd2f-dev-ed.develop.my.salesforce-sites.com/website/services/apexrest/mcp/")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_message = context.get_user_input()
        print(f"[Agent Executor] Received user message: {user_message}")

        # Invoke the LLM-backed agent
        await self.llm_agent.invoke(user_message, event_queue)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Optional: implement cancellation logic if your agent supports streaming cancellation
        print("[Agent Executor] Cancel requested.")