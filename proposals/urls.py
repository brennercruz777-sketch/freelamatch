from django.urls import path

from .views import ProposalAcceptView, ProposalCreateView

urlpatterns = [
    path("job/<int:job_pk>/propor/", ProposalCreateView.as_view(), name="proposal_create"),
    path("<int:pk>/aceitar/", ProposalAcceptView.as_view(), name="proposal_accept"),
]