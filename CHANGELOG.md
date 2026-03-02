# Changelog

Toutes les modifications notables du projet sont documentées ici.

## [0.1.0] - 2026-03-01

### Ajouté

- **i18n** : Interface FR/EN (bouton langue dans la sidebar)
- Pipeline agentic complet : Feedback → Insights → Backlog → Stories → Critique → Synthèse
- API FastAPI (health, ingest, run, stream, chat, export)
- UI React (Vite) : Feedback, Roadmap, Stories, What-if, Chat
- Priorisation RICE, WSJF, MoSCoW (quartiles)
- Export Jira CSV, rapport HTML
- Import Canny, JSONL, CSV
- Démo one-click
- `make start` : une commande pour setup + lancement
- CI GitHub Actions (tests, lint)
- Docker + docker-compose
- Tests compatibilité API, MockLLM pour tests unitaires
- Pre-commit hooks (Ruff, ESLint)
- HEALTHCHECK Docker
- Tests frontend (Vitest), CI frontend (build + tests)
- Error Boundary React, page 404 dédiée
- CONTRIBUTING.md
- Meta description SEO, Docker full-stack (optionnel)

### Technique

- LangGraph pour l'orchestration
- Groq comme provider LLM
- Pydantic pour les modèles
