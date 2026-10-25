from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def home(request):
    return render(request, "base.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("jobs/", include("jobs.urls")),
    path("proposals/", include("proposals.urls")),
    path("threads/", include("messaging.urls")), 
    path("accounts/", include("accounts.urls")),
    path("reviews/", include("reviews.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)