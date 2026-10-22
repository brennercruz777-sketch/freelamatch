from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import User


class RoleRequiredMixin(LoginRequiredMixin):
    """Exige que o usuário esteja logado e tenha o role `required_role`."""

    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if self.required_role and request.user.role != self.required_role:
            raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return super().dispatch(request, *args, **kwargs)


class ClientRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.CLIENT


class FreelancerRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.FREELANCER


class OwnerRequiredMixin(LoginRequiredMixin):
    """Exige que o usuário seja dono do objeto (usa `owner_field`).

    Por padrão, verifica se `obj.<owner_field>` == request.user.
    Para `Job`, o campo dono é `client`. Para `Proposal`, é `freelancer`.
    """

    owner_field = "client"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        owner = getattr(obj, self.owner_field, None)
        if owner != self.request.user:
            raise PermissionDenied("Você não é o dono deste recurso.")
        return obj