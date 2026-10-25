from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View
from django.http import HttpResponse
from .models import Message, Thread


class MyThreadsView(LoginRequiredMixin, ListView):
    template_name = "messaging/my_threads.html"
    context_object_name = "threads"

    def get_queryset(self):
        user = self.request.user
        todas_threads = Thread.objects.all().order_by("-created_at")
        
        minhas_threads = []
        for t in todas_threads:
            if t.is_participant(user):
                minhas_threads.append(t)
                
        return minhas_threads


class ThreadDetailView(DetailView):
    """Exibe a thread de mensagens do job. Apenas participantes."""
    model = Thread
    template_name = "messaging/thread_detail.html"
    context_object_name = "thread"

    def dispatch(self, request, *args, **kwargs):
        self.thread = get_object_or_404(Thread, pk=kwargs["pk"])
        if not request.user.is_authenticated or not self.thread.is_participant(request.user):
            raise PermissionDenied("Você não participa desta conversa.")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.thread

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["messages_list"] = self.thread.messages.select_related("sender")
        return ctx


class MessageCreateView(View):
    """Envia uma mensagem na thread. Apenas participantes."""

    def post(self, request, *args, **kwargs):
        thread = get_object_or_404(Thread, pk=kwargs["pk"])
        if not request.user.is_authenticated or not thread.is_participant(request.user):
            raise PermissionDenied("Você não participa desta conversa.")

        body = request.POST.get("body", "").strip()
        if not body:
            messages.error(request, "A mensagem não pode estar vazia.")
        else:
            Message.objects.create(thread=thread, sender=request.user, body=body)

        return redirect("thread_detail", pk=thread.pk)



class DebugThreadsView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        # Pega todas as threads do banco
        todas_threads = Thread.objects.all().order_by("-created_at")
        
        html = f"<h1>Debug de Conversas</h1>"
        html += f"<p>Usuário logado: <b>{user.username}</b> (Role: {user.role})</p>"
        html += f"<p>Total de threads no banco: {todas_threads.count()}</p>"
        html += "<hr>"
        
        for t in todas_threads:
            html += f"<p>Thread ID: {t.pk} | Job: {t.job.title}</p>"
            html += f"<p>Cliente do Job: {t.job.client.username}</p>"
            
            # Verifica se o usuário é participante
            is_part = t.is_participant(user)
            html += f"<p>O usuário logado é participante? <b>{is_part}</b></p>"
            
            # Mostra quem o sistema acha que são os participantes
            partes = t.participants()
            nomes = [p.username for p in partes]
            html += f"<p>Participantes detectados: {nomes}</p>"
            html += "<hr>"
            
        return HttpResponse(html)