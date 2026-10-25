from django.urls import path

from .views import MessageCreateView, MyThreadsView, ThreadDetailView, DebugThreadsView # Adicione o import

urlpatterns = [
    path("debug/", DebugThreadsView.as_view(), name="debug_threads"),
    path("", MyThreadsView.as_view(), name="my_threads"),
    path("<int:pk>/", ThreadDetailView.as_view(), name="thread_detail"),
    path("<int:pk>/enviar/", MessageCreateView.as_view(), name="message_create"),
]