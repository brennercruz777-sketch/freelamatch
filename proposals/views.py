from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView

from accounts.mixins import FreelancerRequiredMixin, OwnerRequiredMixin
from jobs.models import Job
from .forms import ProposalForm
from .models import Proposal
from django.views import View
from .services import ProposalError, accept_proposal



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

class ProposalAcceptView(OwnerRequiredMixin, View):
    """Cliente dono do job aceita uma proposta."""
    owner_field = "job__client"  # a proposta pertence ao job do cliente

    def get_object(self, queryset=None):
        return get_object_or_404(
            Proposal.objects.select_related("job"),
            pk=self.kwargs["pk"],
        )

    def dispatch(self, request, *args, **kwargs):
        self.proposal = self.get_object()
        if self.proposal.job.client != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Você não é o dono deste job.")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            accept_proposal(self.proposal)
        except ProposalError as e:
            messages.error(request, str(e))
        else:
            messages.success(request, f"Proposta de {self.proposal.freelancer.username} aceita!")
        return redirect("job_proposals", pk=self.proposal.job_id)