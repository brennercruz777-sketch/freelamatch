from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from accounts.mixins import ClientRequiredMixin, OwnerRequiredMixin
from .forms import JobForm
from .models import Category, Job
from django.utils import timezone
from django.views import View


class JobListView(ListView):
    """Listagem pública de jobs com busca, filtro por categoria e status."""
    model = Job
    template_name = "jobs/job_list.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        qs = Job.objects.select_related("client", "category")

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        category = self.request.GET.get("category", "").strip()
        if category:
            qs = qs.filter(category__slug=category)

        status = self.request.GET.get("status", Job.Status.OPEN)
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["current_q"] = self.request.GET.get("q", "")
        ctx["current_category"] = self.request.GET.get("category", "")
        ctx["current_status"] = self.request.GET.get("status", Job.Status.OPEN)
        ctx["status_choices"] = Job.Status.choices
        return ctx


class JobDetailView(DetailView):
    """Detalhe público do job."""
    model = Job
    template_name = "jobs/job_detail.html"
    context_object_name = "job"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        job = self.object

        # Regra 1: Pode enviar proposta?
        ctx["can_propose"] = (
            user.is_authenticated
            and user.role == "freelancer"
            and job.is_open
            and not job.proposals.filter(freelancer=user).exists()
        )

        # Regra 2: Pode abrir conversa?
        # Usamos hasattr para verificar com segurança se a Thread existe
        ctx["can_chat"] = False
        if user.is_authenticated and hasattr(job, "thread"):
            ctx["can_chat"] = job.thread.is_participant(user)

        # Regra 3: Pode avaliar?
        ctx["can_review"] = False
        if user.is_authenticated and job.status == Job.Status.COMPLETED:
            accepted = job.proposals.filter(status="accepted").select_related("freelancer").first()
            if accepted and (user == job.client or user == accepted.freelancer):
                ja_avaliou = job.reviews.filter(reviewer=user).exists()
                ctx["can_review"] = not ja_avaliou

        return ctx


class MyJobsView(ClientRequiredMixin, ListView):
    """Jobs do cliente logado."""
    model = Job
    template_name = "jobs/my_jobs.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        return Job.objects.filter(client=self.request.user).select_related("category")


class JobCreateView(ClientRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"
    success_url = reverse_lazy("my_jobs")

    def form_valid(self, form):
        form.instance.client = self.request.user
        messages.success(self.request, "Job publicado com sucesso!")
        return super().form_valid(form)


class JobUpdateView(OwnerRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"
    owner_field = "client"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(self, "object") and not self.object.is_open:
            messages.error(request, "Só é possível editar jobs abertos.")
            return redirect(self.object.get_absolute_url())
        return response

    def form_valid(self, form):
        messages.success(self.request, "Job atualizado.")
        return super().form_valid(form)


class JobDeleteView(OwnerRequiredMixin, DeleteView):
    model = Job
    template_name = "jobs/job_confirm_delete.html"
    success_url = reverse_lazy("my_jobs")
    owner_field = "client"

    def form_valid(self, form):
        messages.success(self.request, "Job excluído.")
        return super().form_valid(form)


class JobProposalsView(OwnerRequiredMixin, DetailView):
    """Lista as propostas recebidas em um job do cliente logado."""
    model = Job
    template_name = "jobs/job_proposals.html"
    context_object_name = "job"
    owner_field = "client"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["proposals"] = (
            self.object.proposals
            .select_related("freelancer__freelancer_profile")
            .order_by("-created_at")
        )
        return ctx

class JobCompleteView(OwnerRequiredMixin, View):
    owner_field = "client"

    def get_object(self, queryset=None):
        from django.shortcuts import get_object_or_404
        from django.core.exceptions import PermissionDenied
        job = get_object_or_404(Job, pk=self.kwargs["pk"])
        
        # A checagem manual que evita o freelancer de concluir o job
        if job.client != self.request.user:
            raise PermissionDenied("Você não é o dono deste job.")
        return job

    def post(self, request, *args, **kwargs):
        job = self.get_object()
        if job.status != Job.Status.IN_PROGRESS:
            messages.error(request, "Só é possível concluir jobs em andamento.")
        else:
            job.status = Job.Status.COMPLETED
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "completed_at"])
            messages.success(request, "Job concluído! Agora vocês podem se avaliar.")
        return redirect(job.get_absolute_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        job = self.object

        ctx["can_propose"] = (
            user.is_authenticated
            and user.role == "freelancer"
            and job.is_open
            and not job.proposals.filter(freelancer=user).exists()
        )

        # A MUDANÇA ESTÁ AQUI:
        ctx["can_chat"] = False
        if user.is_authenticated and hasattr(job, "thread"):
            ctx["can_chat"] = job.thread.is_participant(user)

        ctx["can_review"] = False
        if user.is_authenticated and job.status == Job.Status.COMPLETED:
            accepted = job.proposals.filter(status="accepted").select_related("freelancer").first()
            if accepted and (user == job.client or user == accepted.freelancer):
                ja_avaliou = job.reviews.filter(reviewer=user).exists()
                ctx["can_review"] = not ja_avaliou

        return ctx  