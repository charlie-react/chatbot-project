import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import OpenAI, RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = (data.get("message") or "").strip()
        if not user_message:
            return

        # tell frontend: start a new bot bubble
        await self.send(text_data=json.dumps({"type": "start"}))

        try:
            with client.responses.stream(
                model="gpt-4.1-mini",
                input=user_message,
                max_output_tokens=200,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        await self.send(text_data=json.dumps({
                            "type": "delta",
                            "text": event.delta
                        }))

            await self.send(text_data=json.dumps({"type": "done"}))

        except RateLimitError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "text": "⚠️ API quota exceeded."
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "text": f"Internal error: {str(e)}"
            }))