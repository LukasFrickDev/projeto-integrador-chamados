# Sistema Web de Gestão de Chamados de Manutenção

Prova de conceito desenvolvida para o Projeto Integrador do 4º semestre de Tecnologia em Análise e Desenvolvimento de Sistemas.

A aplicação centraliza o registro, o atendimento e o acompanhamento de chamados de manutenção em instituições de ensino, concretizando a jornada definida na primeira etapa do Projeto Integrador.

## Sobre a prova de conceito

A POC demonstra de ponta a ponta a integração entre frontend, backend e persistência de dados.

A jornada principal implementada é:

**Mariana registra chamado → chamado fica Aberto → Rafael consulta → inicia atendimento → torna-se responsável → status muda para Em andamento → Rafael registra atualização → Rafael conclui → status muda para Concluído → Mariana consulta status, responsável e histórico.**

O escopo foi mantido intencionalmente pequeno, completo e demonstrável, priorizando a execução integral da jornada principal.

## Funcionalidades implementadas

- criação de chamados pelo perfil solicitante;
- definição automática do status inicial como `Aberto`;
- listagem de chamados;
- consulta de detalhes;
- busca por título ou local;
- filtro por status;
- início de atendimento pelo perfil de manutenção;
- associação do responsável pelo atendimento;
- transição de `Aberto` para `Em andamento`;
- registro de atualização textual;
- conclusão do atendimento;
- transição de `Em andamento` para `Concluído`;
- histórico cronológico do chamado;
- consulta de status, responsável e histórico pelo solicitante;
- validação de permissões por perfil;
- tratamento de carregamento, erros e estados vazios;
- interface responsiva.

## Perfis demonstrativos

### Mariana Ribeiro — Solicitante

Pode:

- registrar chamados;
- consultar seus chamados;
- visualizar detalhes;
- consultar status;
- consultar responsável;
- consultar histórico.

Não pode executar ações de manutenção.

### Rafael Martins — Manutenção

Pode:

- consultar chamados;
- visualizar detalhes;
- iniciar atendimento;
- tornar-se responsável pelo chamado;
- registrar atualizações;
- concluir atendimento.

A troca entre os perfis é feita diretamente pela interface da POC.

> Esta versão utiliza perfis demonstrativos pré-definidos. Não foi implementado um fluxo completo de autenticação, pois ele não faz parte do recorte da prova de conceito.

## Tecnologias utilizadas

### Frontend

- React 19;
- TypeScript 6;
- Vite 8;
- CSS nativo.

### Backend

- Python 3.13;
- Django 5.2.17;
- Django REST Framework 3.18.0.

### Persistência

- SQLite.

### Integração

- API REST;
- JSON;
- proxy do Vite para `/api`.

### Versionamento

- Git;
- GitHub;
- desenvolvimento organizado por branches e Pull Requests.

## Estrutura do projeto

```text
projeto-integrador-chamados/
├── backend/
│   ├── chamados/
│   ├── config/
│   ├── db.sqlite3
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
├── video/
│   └── [vídeo de demonstração]
└── README.md
```

## Pré-requisitos

Antes de executar o projeto, verifique se o ambiente possui:

- Git;
- Python **3.13**;
- Node.js **20.19.0 ou superior compatível com o Vite 8**;
- npm.

A versão de Python utilizada e validada para esta POC é a **3.13**.

Para conferir as versões instaladas:

```bash
git --version
python --version
node --version
npm --version
```

No macOS ou Linux, dependendo da instalação, o comando do Python pode ser:

```bash
python3 --version
```

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/LukasFrickDev/projeto-integrador-chamados.git
cd projeto-integrador-chamados
```

## Backend

### 2. Entrar na pasta do backend

```bash
cd backend
```

### 3. Criar o ambiente virtual

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

Confirme primeiro que `python --version` informa Python 3.13 e execute:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

Com o ambiente virtual ativo:

```bash
python -m pip install -r requirements.txt
```

### 5. Aplicar as migrations

```bash
python manage.py migrate
```

### 6. Preparar os dados demonstrativos

```bash
python manage.py seed_demo --reset
```

Esse comando prepara novamente o cenário canônico da demonstração.

### 7. Iniciar o backend

```bash
python manage.py runserver
```

Por padrão, o Django ficará disponível em:

```text
http://127.0.0.1:8000
```

Mantenha esse terminal aberto.

## Frontend

### 8. Abrir outro terminal

A partir da raiz do repositório:

```bash
cd frontend
```

### 9. Instalar as dependências

Como o projeto possui `package-lock.json`, utilize:

```bash
npm ci
```

Esse comando instala exatamente as versões registradas no lockfile.

### 10. Iniciar o frontend

```bash
npm run dev
```

O Vite exibirá no terminal o endereço da aplicação. Em condições padrão:

```text
http://localhost:5173
```

O frontend encaminha requisições iniciadas por `/api` ao backend local em:

```text
http://127.0.0.1:8000
```

## Banco de dados e dados demonstrativos

O projeto utiliza SQLite.

O arquivo:

```text
backend/db.sqlite3
```

está versionado intencionalmente com um cenário demonstrativo preparado.

Mesmo assim, para garantir um estado conhecido antes da demonstração, recomenda-se executar:

```bash
python manage.py migrate
python manage.py seed_demo --reset
```

### Cenário preparado

O seed cria os perfis:

- Mariana Ribeiro;
- Rafael Martins.

E chamados nos três estados utilizados pela POC:

- `Aberto`;
- `Em andamento`;
- `Concluído`.

## Fluxo recomendado para demonstração

1. acessar como **Mariana Ribeiro**;
2. criar um novo chamado;
3. confirmar que ele foi criado como `Aberto`;
4. abrir o detalhe do chamado;
5. trocar para **Rafael Martins**;
6. localizar e abrir o mesmo chamado;
7. iniciar o atendimento;
8. confirmar que o status mudou para `Em andamento`;
9. confirmar Rafael como responsável;
10. registrar uma atualização textual;
11. conferir a atualização no histórico;
12. concluir o atendimento;
13. confirmar que o status mudou para `Concluído`;
14. voltar para Mariana;
15. abrir o chamado concluído;
16. conferir status, responsável e histórico completo.

## Validações técnicas

### Backend

Com o ambiente virtual ativo e dentro de `backend/`:

```bash
python manage.py check
python manage.py test
```

Estado final validado no desenvolvimento:

```text
35 testes aprovados
```

Também foi validado:

```bash
python manage.py makemigrations --check
```

### Frontend

Dentro de `frontend/`:

```bash
npm run lint
npm run build
```

O comando `npm run build` também executa a verificação TypeScript antes da geração do build.

### Validações adicionais realizadas

- fluxo integrado frontend → backend → SQLite;
- criação de chamado;
- início de atendimento;
- registro de atualização;
- conclusão;
- histórico;
- persistência após recarregamento;
- busca por título;
- busca por local;
- filtro por status;
- permissões por perfil;
- validação de campos obrigatórios;
- responsividade;
- reconstrução dos dados demonstrativos;
- execução a partir de clone limpo em outra máquina.

## Endpoints principais da API

```text
GET  /api/chamados/
POST /api/chamados/

GET  /api/chamados/{id}/

POST /api/chamados/{id}/iniciar/
POST /api/chamados/{id}/atualizacoes/
POST /api/chamados/{id}/concluir/
```

O perfil demonstrativo é informado ao backend pelo cabeçalho:

```text
X-Demo-User
```

Valores utilizados:

```text
mariana
rafael
```

## Repositório

GitHub:

https://github.com/LukasFrickDev/projeto-integrador-chamados

O desenvolvimento foi realizado por incrementos e Pull Requests, mantendo histórico das etapas da implementação.

## Vídeo de demonstração

O vídeo final está incluído na pasta:

```text
video/
```

O vídeo apresenta de forma objetiva a jornada principal implementada na POC.

## Integrantes

- **Lukas Christoph Frick** — GitHub: [LukasFrickDev](https://github.com/LukasFrickDev)
- **Arthur de Lima Chaves** — GitHub: [dandy763](https://github.com/dandy763)

## Status

**POC concluída e funcional.**

A aplicação possui frontend, backend, persistência real em SQLite, dados demonstrativos reproduzíveis e a jornada principal da primeira etapa concretizada de ponta a ponta.
