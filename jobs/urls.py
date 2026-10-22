from django.urls import path

from .views import (
    JobCreateView,
    JobDeleteView,
    JobDetailView,
    JobListView,
    JobUpdateView,
    MyJobsView,
)

urlpatterns = [
    path("", JobListView.as_view(), name="job_list"),
    path("novo/", JobCreateView.as_view(), name="job_create"),
    path("meus/", MyJobsView.as_view(), name="my_jobs"),
    path("<int:pk>/", JobDetailView.as_view(), name="job_detail"),
    path("<int:pk>/editar/", JobUpdateView.as_view(), name="job_update"),
    path("<int:pk>/excluir/", JobDeleteView.as_view(), name="job_delete"),
]