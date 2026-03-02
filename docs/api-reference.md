# Référence API

Base URL : `http://localhost:8000` (ou `/api` en Docker)

## Endpoints

| Méthode | Route | Rôle |
|---------|-------|------|
| GET | `/health` | Santé de l'API |
| POST | `/ingest` | Parse JSONL/CSV → FeedbackItem[] |
| POST | `/ingest/canny` | Import depuis Canny (CANNY_API_KEY) |
| POST | `/run` | Pipeline complet |
| POST | `/run/stream` | Pipeline en SSE |
| POST | `/run/partial` | Stop après insights ou backlog |
| POST | `/run/whatif` | Recalcul RICE avec override |
| POST | `/export/jira` | Export CSV Jira |
| POST | `/chat` | Assistant ReAct |

---

## Exemples

**Ingest** (content = chaîne JSONL, une ligne par feedback) :
```json
POST /ingest
{"content": "{\"id\":\"FB-1\",\"source\":\"ticket\",\"text\":\"Add SSO\"}\n", "format": "jsonl"}
```

**Run** :
```json
POST /run
{"feedback": [{"id":"FB-1","source":"ticket","text":"Add SSO"}]}
```

**Swagger** : http://localhost:8000/docs

---

## Format des données (import)

**JSONL** : une ligne = un JSON. Champs requis : `id`, `source` (email|ticket|comment), `text`.

```json
{"id":"FB-001","source":"ticket","text":"Add SSO authentication."}
```

**CSV** : colonnes `id,source,client,segment,plan,created_at,text`. Optionnels : client, segment, plan, created_at.
