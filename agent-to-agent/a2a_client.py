import logging
from uuid import uuid4
import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = "http://localhost:9999"  #Endpoint of the A2AStarletteApplication where agent messages were collected and managed

    async with httpx.AsyncClient() as httpx_client:
        # --- Fetch agent card ---
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        logger.info("[Agent Client] Fetched agent card: %s", agent_card)

        # --- Initialize A2A client (deprecated, but works) ---
        client = A2AClient(agent_card=agent_card, httpx_client=httpx_client)
        logger.info("[Agent Client] A2A Client initialized.")

        # --- Prepare message payload ---
        send_message_payload = {
            "message": {
                "role": "user",
                #"parts": [{"kind": "text", "text": "Hello world from A2A client 🤣"}],
                "parts": [{"kind": "text", "text": "Give me product catalog"}],
                "messageId": uuid4().hex,
            }
        }

        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        # --- Normal request ---
        response = await client.send_message(request)
        try:
            if response.message and response.message.parts:
                agent_text = response.message.parts[0].text
                print(f"[Agent Client] Server said: {agent_text}")
            else:
                print("[Agent Client] Raw response:", response.model_dump(mode="json", exclude_none=True))
        except Exception:
            print("[Agent Client] Raw response:", response.model_dump(mode="json", exclude_none=True))

        # --- Streaming request ---
        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        async for chunk in client.send_message_streaming(streaming_request):
            try:
                if chunk.delta and chunk.delta.message and chunk.delta.message.parts:
                    agent_text = chunk.delta.message.parts[0].text
                    print(f"[Agent Client][stream] Server said: {agent_text}")
                else:
                    print("[Agent Client][stream] chunk:", chunk.model_dump(mode="json", exclude_none=True))
            except Exception:
                print("[Agent Client][stream] chunk:", chunk.model_dump(mode="json", exclude_none=True))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())