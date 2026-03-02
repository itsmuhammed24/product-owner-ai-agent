# Guide de contribution

Merci de votre intérêt pour contribuer au Product Owner AI Agent.

## Prérequis

- Python 3.10+
- Node.js 18+
- Compte Groq (gratuit) pour `GROQ_API_KEY`

## Installation

```bash
git clone <repo>
cd product-owner-ai-agent
cp .env.example .env   # ajouter GROQ_API_KEY (console.groq.com)
make start
```

Ou manuellement :

```bash
python3 -m venv .venv
. .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -e ".[dev,rag,chroma]"
cd apps/web && npm install
cp .env.example .env  # puis ajouter GROQ_API_KEY
```

## Commandes

| Commande | Description |
|----------|-------------|
| `make start` | Setup + lancement API + UI |
| `make run` | API seule (port 8000) |
| `make web` | UI seule (port 5173) |
| `make test` | Tests Python |
| `make lint` | Ruff (Python) |
| `cd apps/web && npm run test` | Tests frontend (Vitest) |
| `cd apps/web && npm run lint` | ESLint |
| `make install-hooks` | Pre-commit (Ruff + ESLint) |

## Workflow

1. Créer une branche depuis `main`
2. Faire les modifications
3. Exécuter `make test` et `make lint`
4. Commit (pre-commit exécute Ruff + ESLint)
5. Ouvrir une Pull Request

## Structure du code

- `po_agent/` — logique métier, agents, pipeline
- `apps/api/` — API FastAPI
- `apps/web/` — UI React (Vite)
- `tests/` — tests Python
- `apps/web/src/**/*.test.tsx` — tests frontend

## Questions

Ouvrez une issue sur le dépôt.
