# Jeux de données démo

## Fichiers disponibles

| Fichier | Contenu | Usage |
|---------|---------|-------|
| `feedback_minimal.jsonl` | 6 feedbacks variés (SSO, SCIM, Gantt, audit, perf, notifications) | Démo rapide (~30 s) |
| `feedback_chroma_session1.jsonl` | 3 feedbacks : SSO Azure, Calendar, Export PDF | **Session 1** — à lancer en premier pour remplir Chroma |
| `feedback_chroma_session2.jsonl` | 3 feedbacks similaires : SAML/Okta, Timeline, Azure AD | **Session 2** — teste l'enrichissement Chroma avec l'historique |

## Tester la démo (UI)

1. `make start`
2. Ouvrir http://localhost:5173
3. Page Feedback → **Charger l'exemple** (8 premiers du sample) ou **Démo one-click**
4. Cliquer **Lancer l'analyse**

## Tester Chroma (2 sessions)

```bash
# Terminal 1
make start

# Terminal 2
./scripts/test_chroma_demo.sh
```

Ou manuellement avec les fichiers de data/demo :

```bash
# Session 1
curl -s -X POST http://localhost:8000/ingest -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile c data/demo/feedback_chroma_session1.jsonl '{content: $c, format: "jsonl"}')" \
  | jq -c '{feedback: .feedback}' | \
  xargs -I {} curl -s -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{}'

# Session 2 (Chroma enrichit avec les features de la session 1)
curl -s -X POST http://localhost:8000/ingest -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile c data/demo/feedback_chroma_session2.jsonl '{content: $c, format: "jsonl"}')" \
  | jq -c '{feedback: .feedback}' | \
  xargs -I {} curl -s -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{}'
```

## Format JSONL

Chaque ligne = 1 objet JSON :

```json
{"id":"FB-001","source":"ticket","client":"Acme","segment":"mid-market","plan":"Pro","created_at":"2026-02-12","text":"Votre feedback ici"}
```

- **id** (requis) : identifiant unique
- **source** (requis) : `ticket` | `email` | `comment`
- **text** (requis) : contenu du feedback
- **client**, **segment**, **plan**, **created_at** : optionnels
