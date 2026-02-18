from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
app_name = 'chat'
urlpatterns = [path("",views.chat_home,name="home"),
               path("new/",views.new_conversation,name="new"),
               path("<int:conversation_id>/",views.chat_detail, name="detail"),
               path("login/",views.login_view,name="login"),
               path("register/",views.register_view,name="register"),
               path("logout/",LogoutView.as_view(next_page="chat:login"),name="logout")]