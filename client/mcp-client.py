import requests
import json
import os
from dotenv import load_dotenv

try:
    import readline
except ImportError:
    import pyreadline3 as readline

from openai import OpenAI

load_dotenv()

# -----------------------------
# Salesforce MCP Client
# -----------------------------
class SalesforceMCPClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self._request_counter = 1

    def _next_id(self):
        rid = self._request_counter
        self._request_counter += 1
        return rid

    def send_request(self, method, params=None):
        payload = {"id": self._next_id(), "method": method}
        if params:
            payload["params"] = params

        headers = {"Content-Type": "application/json"}
        response = requests.post(self.base_url, json=payload, headers=headers)

        try:
            return response.json()
        except Exception:
            return {"error": "Invalid JSON response", "raw": response.text}

    # ---- MCP helpers ----
    def call_tool(self, tool_name, arguments=None):
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })

    def list_tools(self):
        return self.send_request("tools/list")

# -----------------------------
# LLM Orchestrator Agent
# -----------------------------
class LLMOrchestrator:
    def __init__(self, client: SalesforceMCPClient, model="gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY environment variable")
        self.client = client
        self.model = model
        self.llm = OpenAI(api_key=api_key)

    def handle_user_request(self, user_input: str):
        """
        Ask the LLM to decide which MCP tool to call and its arguments.
        """
        # Get available tools from Salesforce
        tools_response = self.client.list_tools()
        tools = tools_response.get("result", {}).get("tools", [])

        system_prompt = f"""
            You are an autonomous Salesforce MCP agent.
            Available tools: {json.dumps(tools, indent=2)}.

            When the user asks something, decide which MCP tool to call and what arguments to pass.
            Always respond ONLY in JSON with this structure:
            {{
              "tool": "<tool_name>",
              "arguments": {{ ... }}
            }}
            Example:
            {{
              "tool": "create-leads",
              "arguments": {{ "leadLastName": "Doe", "leadFirstName": "John", "company": "Acme" }}
            }}
        """

        completion = self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )

        try:
            llm_response = json.loads(completion.choices[0].message.content)
        except Exception as e:
            return {"error": f"Failed to parse LLM output: {e}",
                    "raw": completion.choices[0].message.content}

        tool_name = llm_response.get("tool")
        arguments = llm_response.get("arguments", {})

        if not tool_name:
            return {"error": "LLM did not specify a tool", "raw": llm_response}

        return self.client.call_tool(tool_name, arguments)

# -----------------------------
# Interactive CLI (Natural Language)
# -----------------------------
def main():
    BASE_URL = os.getenv('MCP_SERVER_URL')
    if not BASE_URL:
        raise RuntimeError("Set MCP_SERVER_URL environment variable")

    client = SalesforceMCPClient(BASE_URL)
    orchestrator = LLMOrchestrator(client)

    print("🤖 Salesforce MCP Agent Ready")
    print("Type natural language instructions (e.g., 'create a lead for John Doe at Acme Inc.')")
    print("Type 'exit' to quit")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            break

        result = orchestrator.handle_user_request(user_input)
        print("mcp>", json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
