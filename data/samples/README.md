# Jeux de données (samples)

| Fichier | Description | Items |
|---------|-------------|-------|
| `feedback_sample.jsonl` | Données complètes — démo, tests | 30 |
| `feedback_sample.csv` | Même contenu en CSV | 30 |
| `feedback_minimal.jsonl` | Version courte (tests rapides) | 6 |
| `feedback_minimal.csv` | Même contenu en CSV | 6 |
| `feedback_edge_cases.jsonl` | Cas limites (unicode, champs optionnels) | 5 |

## Format JSONL

Une ligne = un JSON par feedback :
```json
{"id":"FB-001","source":"ticket","client":"Acme","segment":"mid-market","plan":"Pro","created_at":"2026-02-12","text":"SSO with Azure AD is mandatory."}
```

Champs requis : `id`, `source` (email|ticket|comment), `text`.

## Format CSV

Colonnes : `id,source,client,segment,plan,created_at,text`
