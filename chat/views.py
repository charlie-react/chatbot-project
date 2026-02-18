from django.shortcuts import render, redirect, get_object_or_404
from openai import OpenAI,RateLimitError
import os

from .forms import RegisterForm
from dotenv import load_dotenv
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from .models import Conversation,Message
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Create your views here.

# def _make_title(text: str) -> str:
#     text = (text or "").strip()
#     if not text:
#         return "New chat"
#     words = text.split()
#     title = " ".join(words[:8])
#     return title[:120]

@login_required
def chat_home(request):
    convo = Conversation.objects.filter(user=request.user).order_by("-updated_at").first()
    if convo:
        return redirect("chat:detail",conversation_id=convo.id)
    return redirect("chat:new")

@login_required
def new_conversation(request):
    convo  = Conversation.objects.create(user=request.user,title="New Chat")
    return redirect("chat:detail",conversation_id=convo.id)

@login_required
def chat_detail(request,conversation_id):
    conversation = get_object_or_404(Conversation,id=conversation_id,user=request.user)

    conversations = (Conversation.objects.filter(user=request.user).order_by("-updated_at","-created_at"))

    messages = Message.objects.filter(conversation=conversation).order_by("created_at", "id")

    return render(request,"chat/index.html",{"conversation":conversation,"conversations":conversations,"messages":messages})

# def index(request):
#     conversation, created = Conversation.objects.get_or_create(user=request.user)
#     error_message = None
#     if request.method == "POST":
#              user_message = request.POST.get("message")
#              if user_message:
#               Message.objects.create(conversation=conversation,content=user_message,is_bot=False)
#               try:
#                 response = client.responses.create(
#                     model="gpt-4.1-mini",
#                     input=user_message,
#                     max_output_tokens=200
#                 )
#                 bot_response = response.output_text
#                 Message.objects.create(conversation=conversation,content=bot_response,is_bot=True)
#
#
#               except RateLimitError:
#                 error_message = "⚠️ API quota exceeded. Please check billing."
#
#
#               except Exception as e:
#                 error_message = f"Internal error: {str(e)}"
#
#     messages = Message.objects.filter(conversation=conversation)
#
#     return render(request, "chat/index.html",{"messages":messages,"error_message":error_message},)

def register_view(request):
    if request.method == "POST":
        form= RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chat:home")
    else:
        form = RegisterForm()

    return render(request, "chat/register.html", {"form": form})


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("chat:home")
        else:
         error = "Invalid username or password"
    return render(request, "chat/login.html", {"error": error})

