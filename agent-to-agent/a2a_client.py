import asyncio
import logging
import json
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest, SendStreamingMessageRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A2A Agent")


async def main():
    #base_url = "http://localhost:9999"  # Endpoint of your A2A agent
    base_url = "https://orgfarm-225b06bd2f-dev-ed.develop.my.salesforce-sites.com/website/services/apexrest/a2a/"  # Endpoint of your A2A agent

    async with httpx.AsyncClient() as httpx_client:
        # --- Fetch agent card ---
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        logger.info("✅ Fetched agent card: %s", agent_card)

        # --- Initialize deprecated A2A client ---
        client = A2AClient(agent_card=agent_card, httpx_client=httpx_client)
        logger.info("✅ A2A Client initialized.")

        # --- Prepare message payload ---
        message_payload = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "Give me product catalog"}],
                "messageId": uuid4().hex,
            }
        }

        # -----------------------------
        # Non-streaming request
        # -----------------------------
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**message_payload)
        )

        try:
            response = await client.send_message(request)
            logger.info("[Agent Client] Non-streaming raw response: %s", response)

            # --- Extract message parts safely ---
            root = getattr(response, "root", None)
            if root and getattr(root, "result", None) and getattr(root.result, "parts", None):
                raw_text = root.result.parts[0].root.text  # <-- fixed access
                print("[Agent Client] Raw text:", raw_text)
                try:
                    parsed = json.loads(raw_text)
                    print("[Agent Client] Parsed JSON catalog:", json.dumps(parsed, indent=2))
                except json.JSONDecodeError as e:
                    print("[Agent Client] JSON parsing failed:", e)
            else:
                print("[Agent Client] No message parts found in response.root.result. Maybe the response object is a Task")
        except Exception as ex:
            logger.exception("❌ Exception during non-streaming send: %s", ex)


        if getattr(agent_card.capabilities, "streaming", False):
            # -----------------------------
            # Streaming request
            # -----------------------------
            streaming_request = SendStreamingMessageRequest(
                id=str(uuid4()), params=MessageSendParams(**message_payload)
            )

            try:
                async for event in client.send_message_streaming(streaming_request):
                    logger.info("[Agent Client][stream] raw event: %s", event)

                    root = getattr(event, "root", None)
                    if root and getattr(root, "result", None) and getattr(root.result, "parts", None):
                        raw_text = root.result.parts[0].root.text  # <-- fixed access
                        try:
                            parsed = json.loads(raw_text)
                            print("[Agent Client][stream] Parsed JSON catalog:", json.dumps(parsed, indent=2))
                        except json.JSONDecodeError as e:
                            print("[Agent Client][stream] JSON parsing failed:", e)
                    else:
                        print("[Agent Client][stream] No parts found in event.root.result")
            except Exception as ex:
                logger.exception("❌ Exception during streaming send: %s", ex)
        else:
            logger.info("[Agent Client] ⚡ Server does NOT support streaming")

if __name__ == "__main__":
    asyncio.run(main())
