# Script démo — 8–10 min

## Avant

```bash
# Vérifier que .env contient GROQ_API_KEY (obligatoire pour la démo)
make start
# http://localhost:5173 (UI) • http://localhost:8000 (API)
```

---

## Déroulé

### 1. Contexte (1 min)
> "L'agent traite le feedback clients, identifie les patterns, priorise avec RICE et MoSCoW, génère des user stories Jira-ready."

### 2. Upload + Run (2 min)
1. **Démo one-click** ou « Charger l'exemple »
2. **Lancer l'analyse**

### 3. Résultats (4–5 min)
- **Insights** — Regroupement sémantique
- **Roadmap** — Now / Next / Later (MoSCoW)
- **Backlog** — RICE, WSJF, justification
- **User Stories** — As a / I want / So that, critères Gherkin
- **Diff Critique** — Avant/après raffinement
- **What-if** — Recalcul RICE en temps réel

### 4. Export + API (1 min)
- CSV Jira → téléchargement
- Swagger : http://localhost:8000/docs

---

## Conclusion
> "De la collecte de feedback à la roadmap priorisée et aux user stories prêtes pour Jira, avec traçabilité complète."
