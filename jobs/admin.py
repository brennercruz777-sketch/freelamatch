from django.contrib import admin

from .models import Category, Job


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "category", "budget_min", "budget_max", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "description", "client__username")
    readonly_fields = ("created_at", "completed_at")