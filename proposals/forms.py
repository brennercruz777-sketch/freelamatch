from django import forms

from .models import Proposal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ("amount", "deadline_days", "message")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
        }
        labels = {
            "amount": "Valor da proposta (R$)",
            "deadline_days": "Prazo de entrega (dias)",
            "message": "Mensagem para o cliente",
        }