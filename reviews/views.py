from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView

from jobs.models import Job
from .forms import ReviewForm
from .models import Review


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(Job, pk=kwargs["job_pk"])

        if self.job.status != Job.Status.COMPLETED:
            messages.error(request, "Só é possível avaliar jobs concluídos.")
            return redirect(self.job.get_absolute_url())

        accepted = self.job.proposals.filter(status="accepted").select_related("freelancer").first()
        if not accepted:
            messages.error(request, "Não há freelancer aceito neste job.")
            return redirect(self.job.get_absolute_url())

        self.reviewee = (
            accepted.freelancer if request.user == self.job.client else self.job.client
        )
        # quem pode avaliar: cliente dono OU freelancer aceito
        if request.user != self.job.client and request.user != accepted.freelancer:
            raise PermissionDenied("Você não participa deste job.")

        if Review.objects.filter(job=self.job, reviewer=request.user).exists():
            messages.info(request, "Você já avaliou este job.")
            return redirect(self.job.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["job"] = self.job
        ctx["reviewee"] = self.reviewee
        return ctx

    def form_valid(self, form):
        form.instance.job = self.job
        form.instance.reviewer = self.request.user
        form.instance.reviewee = self.reviewee
        messages.success(self.request, "Avaliação enviada. Obrigado!")
        return super().form_valid(form)

    def get_success_url(self):
        return self.job.get_absolute_url()