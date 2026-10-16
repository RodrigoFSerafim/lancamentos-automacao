# 🎬 Rastreador de Lançamentos

Automação em Python que acompanha **filmes, séries e jogos** que você quer ver/jogar e **avisa quando a estreia está chegando**, consultando as APIs REST do [TMDB](https://www.themoviedb.org/) (filmes e séries) e do [RAWG](https://rawg.io/) (jogos).

## Integrantes

| Nome | RM |
| :--- | :--- |
| Rodrigo Fernandes Serafim | 550816 |

## Problema que resolve

Nunca mais perder a estreia de um filme, o novo episódio de uma série ou o lançamento de um jogo: você monta uma lista e o script, rodando todo dia, avisa no terminal quando a data estiver próxima.

## Funcionalidades

- 🔎 `search`: busca títulos por nome (filmes, séries e jogos)
- 📅 `upcoming`: lista os próximos lançamentos da janela de dias escolhida
- ➕ `add` / ➖ `remove` / 📋 `list`: gerencia a sua lista de acompanhamento
- 🔔 `check`: consulta as APIs e notifica estreias nos próximos N dias
  - séries: considera a data do **próximo episódio**
  - cada título/data é notificado **uma única vez** (se a data mudar, avisa de novo)
  - notificação no terminal

## Estrutura

```
release-tracker/
├── main.py              # CLI (argparse)
├── requirements.txt
├── .env.example         # modelo de configuração das chaves
├── tracker/
│   ├── config.py        # leitura das chaves (.env)
│   ├── http.py          # cliente HTTP (requests) com tratamento de erros
│   ├── tmdb.py          # integração TMDB (filmes e séries)
│   ├── rawg.py          # integração RAWG (jogos)
│   ├── storage.py       # watchlist em JSON local
│   ├── checker.py       # regra de negócio: o que notificar
│   ├── notifier.py      # notificações no terminal
│   └── models.py        # dataclass Release
└── tests/test_core.py   # testes offline (unittest)
```

## Instalação

```bash
git clone <url-do-seu-repositorio>
cd release-tracker
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Chaves de API

1. **TMDB** (grátis): crie uma conta e gere a chave em <https://www.themoviedb.org/settings/api> (use a *API Key v3*).
2. **RAWG** (grátis): gere a chave em <https://rawg.io/apidocs>.
```bash
cp .env.example .env     # Windows: copy .env.example .env
# edite o .env e cole as chaves
```

## Uso

```bash
# descobrir o id de um título
python main.py search "dune" --type movie
python main.py search "zelda" --type game

# adicionar à lista (tipo: movie | tv | game)
python main.py add movie 693134
python main.py add game 3498

# ver a lista
python main.py list

# verificar estreias nos próximos 7 dias (padrão) e notificar
python main.py check
python main.py check --days 30

# explorar lançamentos futuros
python main.py upcoming --type game --days 60
```

## Rodando todo dia (automação)

**Linux/macOS (cron)**: todo dia às 9h:

```cron
0 9 * * * cd /caminho/release-tracker && .venv/bin/python main.py check
```

**Windows**: Agendador de Tarefas → nova tarefa diária executando
`C:\caminho\release-tracker\.venv\Scripts\python.exe main.py check` com a pasta do projeto em "Iniciar em".

## Testes

```bash
python -m unittest
```

Os testes não fazem chamadas reais às APIs.

## Requisitos do trabalho

| Requisito | Como é atendido |
|---|---|
| Somente Python | Todo o código é Python 3 |
| Integração externa | Consumo das APIs REST do TMDB e RAWG com `requests` |
| Código limpo e comentado | Módulos pequenos por responsabilidade, docstrings e comentários onde faz diferença |
| `requirements.txt` | `requests` e `python-dotenv` |

## Créditos

Este produto usa a API do TMDB, mas não é endossado nem certificado pelo TMDB.
Dados de jogos fornecidos por [RAWG](https://rawg.io/).

## Ideias para evoluir

- Agendar com GitHub Actions em vez de cron local
- Notificação por e-mail ou Discord
- Filtrar por plataforma (jogos) ou provedor de streaming (filmes/séries)
