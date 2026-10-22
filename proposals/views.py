from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView

from accounts.mixins import FreelancerRequiredMixin, OwnerRequiredMixin
from jobs.models import Job
from .forms import ProposalForm
from .models import Proposal


class ProposalCreateView(FreelancerRequiredMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = "proposals/proposal_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(Job, pk=kwargs["job_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["job"] = self.job
        return ctx

    def form_valid(self, form):
        form.instance.job = self.job
        form.instance.freelancer = self.request.user

        if not self.job.is_open:
            form.add_error(None, "Este job não está mais aberto para propostas.")
            return self.form_invalid(form)
        if self.job.client == self.request.user:
            form.add_error(None, "Você não pode propor no seu próprio job.")
            return self.form_invalid(form)
        if self.job.proposals.filter(freelancer=self.request.user).exists():
            form.add_error(None, "Você já enviou uma proposta para este job.")
            return self.form_invalid(form)

        messages.success(self.request, "Proposta enviada com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("job_detail", args=[self.job.pk])


class ProposalListView(OwnerRequiredMixin, CreateView):
    """Não é usado diretamente — placeholder para evitar import errado."""
    pass