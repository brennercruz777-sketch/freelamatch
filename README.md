# 💼 FreelaMatch

O **FreelaMatch** é uma plataforma de marketplace de freelancers (estilo Workana/Upwork). O sistema conecta clientes que precisam de serviços a freelancers, permitindo a publicação de vagas, envio de propostas, negociação via chat e avaliações mútuas.

🔗 **[Acesse o projeto online aqui](https://freelamatch.onrender.com/)**

## 🚀 Tecnologias Utilizadas
- **Backend:** Python, Django 5
- **Banco de Dados:** PostgreSQL (Produção) / SQLite (Desenvolvimento)
- **Frontend:** Django Templates, Bootstrap 5
- **Deploy:** Render, Gunicorn, WhiteNoise
- **Testes:** Django TestCase (Cobertura de permissões e regras de negócio)

## ⚙️ Funcionalidades (Máquina de Estados)
O grande diferencial deste projeto é a modelagem de regras de negócio e estados:
- **Jobs**: `open` → `in_progress` → `completed` / `cancelled`
- **Propostas**: `pending` → `accepted` / `rejected` / `withdrawn`
- **Aceite Atômico**: Ao aceitar uma proposta, o sistema rejeita todas as outras do mesmo job e cria uma thread de conversa em uma única transação no banco.

### Principais Recursos:
- **Autenticação com Papéis:** Separação clara entre Clientes e Freelancers.
- **Gestão de Vagas:** Clientes publicam jobs com orçamento e prazo; freelancers buscam com filtros.
- **Chat:** Conversa exclusiva por job entre o cliente e o freelancer aceito.
- **Avaliações:** Sistema de feedback mútuo (1 a 5 estrelas) após a conclusão.
- **Dashboard:** Visões personalizadas com estatísticas para clientes e freelancers.

## 🧪 Como testar o projeto (Dados de Demonstração)
Você pode explorar o projeto online. Para facilitar, o banco já foi populado com dados de demonstração.

- **Acesse:** [https://freelamatch.onrender.com/](https://freelamatch.onrender.com/)
- **Contas de Cliente:** `cliente1` / senha: `123456`
- **Contas de Freelancer:** `freela1` / senha: `123456`

*(Sinta-se à vontade para criar sua própria conta clicando em "Cadastrar").*

## 💻 Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/brennercruz777-sketch/freelamatch.git
   cd freelamatch