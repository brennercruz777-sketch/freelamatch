from django.contrib import admin

from .models import Proposal


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("job", "freelancer", "amount", "deadline_days", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("job__title", "freelancer__username")
    readonly_fields = ("created_at",)