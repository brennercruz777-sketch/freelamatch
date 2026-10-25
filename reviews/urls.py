from django.urls import path

from .views import ReviewCreateView

urlpatterns = [
    path("job/<int:job_pk>/avaliar/", ReviewCreateView.as_view(), name="review_create"),
]