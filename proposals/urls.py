from django.urls import path

from .views import ProposalCreateView

urlpatterns = [
    path("job/<int:job_pk>/propor/", ProposalCreateView.as_view(), name="proposal_create"),
]