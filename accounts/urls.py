from django.urls import path
from .views import SignUpView
from dashboard.views import DashboardView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]