import json
import os
from channels.generic.websocket import WebsocketConsumer
from openai import OpenAI, RateLimitError
from .models import Conversation, Message

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def make_title(text: str) -> str:
    words = (text or "").strip().split()
    if not words:
        return "New Chat"
    return " ".join(words[:8])[:120]

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            self.close()
            return
        self.accept()

    def receive(self, text_data):
        user = self.scope["user"]
        data = json.loads(text_data)

        user_message = (data.get("message") or "").strip()
        conversation_id = data.get("conversation_id")

        if not user_message or not conversation_id:
            return

        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            self.send(text_data=json.dumps({"type": "error", "text": "Conversation not found"}))
            return

        # Auto-title if default
        if conversation.title.strip().lower() in ("new chat", ""):
            conversation.title = make_title(user_message)
            conversation.save()
            self.send(text_data=json.dumps({"type": "title", "text": conversation.title}))

        # Save user message
        Message.objects.create(conversation=conversation, content=user_message, is_bot=False)

        # Tell frontend to create empty bot bubble
        self.send(text_data=json.dumps({"type": "start"}))

        bot_text = ""

        try:
            with client.responses.stream(
                model="gpt-4.1-mini",
                input=user_message,
                max_output_tokens=200,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        chunk = event.delta
                        bot_text += chunk
                        self.send(text_data=json.dumps({"type": "delta", "text": chunk}))

            # Save bot message once
            Message.objects.create(conversation=conversation, content=bot_text, is_bot=True)
            self.send(text_data=json.dumps({"type": "done"}))

        except RateLimitError:
            self.send(text_data=json.dumps({"type": "error", "text": "⚠️ API quota exceeded."}))
        except Exception as e:
            self.send(text_data=json.dumps({"type": "error", "text": f"Internal error: {str(e)}"}))