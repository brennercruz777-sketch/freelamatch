from django import forms

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ("category", "title", "description", "budget_min", "budget_max", "deadline")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        bmin = cleaned.get("budget_min")
        bmax = cleaned.get("budget_max")
        if bmin is not None and bmax is not None and bmin > bmax:
            raise forms.ValidationError("O orçamento mínimo não pode ser maior que o máximo.")
        return cleaned