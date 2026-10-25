import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from accounts.models import User
from jobs.models import Category, Job
from proposals.models import Proposal
from proposals.services import accept_proposal
from messaging.models import Message
from reviews.models import Review


class Command(BaseCommand):
    help = "Popula o banco com dados de demonstração para o portfólio."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Limpando dados antigos...")
        # Apaga apenas dados de usuários que não são superusuários para não perder o admin
        User.objects.filter(is_superuser=False).delete()
        Category.objects.all().delete()

        self.stdout.write("Criando categorias...")
        cats = [
            Category.objects.create(name="Desenvolvimento Web", slug="dev-web"),
            Category.objects.create(name="Design Gráfico", slug="design-grafico"),
            Category.objects.create(name="Mobile", slug="mobile"),
            Category.objects.create(name="Redação", slug="redacao"),
        ]

        self.stdout.write("Criando Clientes...")
        clientes = []
        nomes_cli = ["TechCorp", "Padaria do João", "Agência Criativa", "Startup XYZ"]
        for i, nome in enumerate(nomes_cli):
            u = User.objects.create_user(
                username=f"cliente{i+1}",
                email=f"cliente{i+1}@teste.com",
                password="123456",
                role=User.Role.CLIENT,
            )
            u.client_profile.company = nome
            u.client_profile.save()
            clientes.append(u)

        self.stdout.write("Criando Freelancers...")
        freelas = []
        nomes_fre = ["Ana Dev", "Carlos Design", "Mariana Mobile", "Pedro Redator", "Julia Fullstack"]
        for i, nome in enumerate(nomes_fre):
            u = User.objects.create_user(
                username=f"freela{i+1}",
                email=f"freela{i+1}@teste.com",
                password="123456",
                role=User.Role.FREELANCER,
            )
            u.freelancer_profile.headline = nome
            u.freelancer_profile.skills = "Python, Django, HTML, CSS"
            u.freelancer_profile.save()
            freelas.append(u)

        self.stdout.write("Criando Jobs e Propostas...")
        jobs_data = [
            ("Criar site institucional", "Preciso de um site com 5 páginas.", 1500, 3000),
            ("Logo para cafeteria", "Uma logo moderna e minimalista.", 500, 1000),
            ("App de delivery", "Aplicativo simples para pedidos.", 5000, 8000),
            ("Posts para blog", "10 artigos de 1000 palavras sobre tecnologia.", 800, 1500),
            ("Landing page de vendas", "Página para capturar leads.", 1200, 2500),
        ]

        for i in range(10):
            titulo, desc, bmin, bmax = random.choice(jobs_data)
            cli = random.choice(clientes)
            cat = random.choice(cats)
            
            # Cria o Job
            job = Job.objects.create(
                client=cli,
                category=cat,
                title=f"{titulo} #{i+1}",
                description=desc,
                budget_min=Decimal(bmin),
                budget_max=Decimal(bmax),
                deadline=timezone.now().date() + timedelta(days=random.randint(10, 60)),
            )

            # Cria propostas
            freelancers_escolhidos = random.sample(freelas, random.randint(1, 3))
            propostas = []
            for fre in freelancers_escolhidos:
                propostas.append(Proposal.objects.create(
                    job=job,
                    freelancer=fre,
                    amount=Decimal(random.randint(bmin, bmax)),
                    deadline_days=random.randint(5, 30),
                    message="Olá, tenho muita experiência com isso e posso entregar no prazo.",
                ))

            # Lógica de estados
            if i < 3:
                # Os 3 primeiros jobs ficam em andamento ou concluídos
                if propostas:
                    p_aceita = random.choice(propostas)
                    accept_proposal(p_aceita)
                    
                    # Manda mensagens
                    Message.objects.create(thread=job.thread, sender=cli, body="Olá, gostei do seu perfil. Vamos começar!")
                    Message.objects.create(thread=job.thread, sender=p_aceita.freelancer, body="Combinado! Já estou trabalhando nisso.")

                    if i < 2:
                        # 2 jobs concluídos
                        job.status = Job.Status.COMPLETED
                        job.completed_at = timezone.now()
                        job.save()

                        # Cria avaliações
                        Review.objects.create(job=job, reviewer=cli, reviewee=p_aceita.freelancer, rating=5, comment="Excelente trabalho!")
                        Review.objects.create(job=job, reviewer=p_aceita.freelancer, reviewee=cli, rating=5, comment="Ótimo cliente, pagou em dia.")

        self.stdout.write(self.style.SUCCESS("Banco de dados populado com sucesso!"))
        self.stdout.write(self.style.SUCCESS("Usuários criados (senha para todos: 123456):"))
        self.stdout.write("  - Clientes: cliente1, cliente2, cliente3, cliente4")
        self.stdout.write("  - Freelancers: freela1, freela2, freela3, freela4, freela5")