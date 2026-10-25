from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Avg, Count

from jobs.models import Job
from proposals.models import Proposal
from reviews.models import Review

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == "client":
            # Estatísticas do Cliente
            jobs = Job.objects.filter(client=user)
            ctx["jobs_total"] = jobs.count()
            ctx["jobs_ativos"] = jobs.filter(status=Job.Status.IN_PROGRESS).count()
            ctx["jobs_abertos"] = jobs.filter(status=Job.Status.OPEN).count()
            ctx["propostas_recebidas"] = Proposal.objects.filter(job__client=user).count()
            
            # Últimos 5 jobs criados
            ctx["ultimos_jobs"] = jobs.order_by("-created_at")[:5]

        elif user.role == "freelancer":
            # Estatísticas do Freelancer
            propostas = Proposal.objects.filter(freelancer=user)
            ctx["propostas_enviadas"] = propostas.count()
            ctx["propostas_aceitas"] = propostas.filter(status=Proposal.Status.ACCEPTED).count()
            
            # Média de avaliações recebidas
            media = Review.objects.filter(reviewee=user).aggregate(Avg("rating"))["rating__avg"]
            ctx["media_avaliacoes"] = round(media, 1) if media else "Sem avaliações"
            ctx["total_avaliacoes"] = Review.objects.filter(reviewee=user).count()
            
            # Últimas 5 propostas enviadas
            ctx["ultimas_propostas"] = propostas.order_by("-created_at")[:5]

        return ctx