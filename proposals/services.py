from django.db import transaction

from jobs.models import Job
from messaging.models import Thread
from .models import Proposal


class ProposalError(Exception):
    """Erro de negócio ao tentar aceitar uma proposta."""
    pass


@transaction.atomic
def accept_proposal(proposal: Proposal) -> Proposal:
    """
    Aceita uma proposta e move o job para in_progress.

    Regras:
    - O job precisa estar open.
    - A proposta precisa estar pending.
    - Ao aceitar, todas as demais propostas do job viram rejected.
    - Uma Thread é criada para o job (se ainda não existir).

    Tudo roda em uma transação: se qualquer passo falhar, nada é persistido.
    """
    # Trava a linha do job para evitar corrida entre dois aceites simultâneos.
    job = Job.objects.select_for_update().get(pk=proposal.job_id)

    if job.status != Job.Status.OPEN:
        raise ProposalError("Este job não está mais aberto.")
    if proposal.status != Proposal.Status.PENDING:
        raise ProposalError("Esta proposta não está mais pendente.")

    proposal.status = Proposal.Status.ACCEPTED
    proposal.save(update_fields=["status"])

    job.status = Job.Status.IN_PROGRESS
    job.save(update_fields=["status"])

    Proposal.objects.filter(job=job).exclude(pk=proposal.pk).update(
        status=Proposal.Status.REJECTED
    )

    Thread.objects.get_or_create(job=job)

    return proposal