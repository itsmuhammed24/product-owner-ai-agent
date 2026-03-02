# Architecture — PO Agent

## Vision

Assistant IA qui décharge le PO sur trois piliers : **analyse de feedback**, **priorisation data-driven**, **rédaction de user stories** prêtes pour Jira.

---

## Schéma technique (vue d'ensemble)

### Vue stack (User → UI → AI Agent → LLM → outils)

![Architecture PO Agent — Stack](assets/architecture-po-agent.png)

### Vue flux (Input → Pipeline 7 agents → Outputs)

![Architecture PO Agent — Détail](assets/architecture-detaille.png)

*[Détail agentique](agentic.md) · [Schéma interactif](architecture-diagram.html)*

---

## Flux global

```mermaid
flowchart LR
    subgraph Input
        A[JSONL/CSV]
        B[Canny]
    end

    subgraph API["API FastAPI"]
        INGEST["/ingest"]
        RUN["/run"]
    end

    subgraph Pipeline["LangGraph"]
        direction TB
        FB[Feedback] --> INS[Insight] --> PRIO[Priority] --> RAG[RAG] --> STORY[Story] --> CRIT[Critique] --> SYNTH[Synthesis]
    end

    A --> INGEST
    B --> INGEST
    INGEST --> RUN
    RUN --> Pipeline
    Pipeline --> OUT[Résultat]
```

---

## Pipeline LangGraph (détail)

```mermaid
flowchart TD
    START([feedback]) --> FB[analyze_feedback]
    FB --> INS[extract_insights]
    INS --> PRIO[prioritize_features]
    PRIO --> RAG[enrich_retrieval]
    RAG --> STORY[generate_stories]
    STORY --> CRIT[critique_stories]

    CRIT --> CHECK{score < 4 et passes < 2 ?}
    CHECK -->|oui| STORY
    CHECK -->|non| SYNTH[generate_summary]
    SYNTH --> END([résultat final])
```

---

## Couches applicatives

```mermaid
flowchart TB
    subgraph UI["Frontend (React + Vite)"]
        PAGES[Pages: Feedback, Roadmap, Stories]
        CHAT[ChatFab ReAct]
    end

    subgraph API["API (FastAPI)"]
        ROUTES["/ingest, /run, /chat, /export"]
    end

    subgraph Core["po_agent"]
        subgraph domain["domain"]
            MODELS[models Pydantic]
            SCORING[RICE, WSJF, MoSCoW]
        end

        subgraph agents["agents"]
            FA[FeedbackAgent]
            IA[InsightAgent]
            PA[PriorityAgent]
            RA[RetrievalAgent]
            SA[StoryAgent]
            CA[CritiqueAgent]
            SYA[SynthesisAgent]
        end

        subgraph intelligence["intelligence"]
            ROADMAP[roadmap Now/Next/Later]
            EMBED[embeddings]
            WHATIF[whatif]
            VSTORE[vector_store Chroma]
        end
    end

    UI --> API
    API --> agents
    agents --> domain
    agents --> intelligence
```

---

## Agents & rôles

| Agent | Entrée | Sortie | Rôle |
|-------|--------|--------|------|
| **FeedbackAgent** | FeedbackItem[] | AnalyzedFeedback[] | Catégorie, feature requests (LLM) |
| **InsightAgent** | AnalyzedFeedback[] | Insight[] | Clustering sémantique, consolidation |
| **PriorityAgent** | Insight[] | BacklogItem[] | RICE, WSJF, MoSCoW (domain + LLM) |
| **RetrievalAgent** | BacklogItem[] | enrichissement | RAG — features similaires |
| **StoryAgent** | BacklogItem[] | UserStory[] | Stories Jira-ready (LLM) |
| **CritiqueAgent** | UserStory[] | UserStory[] | LLM-as-a-judge, raffinement |
| **SynthesisAgent** | Backlog + roadmap | summary | Résumé exécutif |

---

## Décisions techniques

| Choix | Raison |
|-------|--------|
| **LangGraph** | Orchestration claire, états typés, conditional edges, débogage |
| **Domain pur** | RICE, WSJF, MoSCoW calculés sans LLM → testable, reproductible |
| **Pydantic** | Outputs structurés validés, prêt pour intégration |
| **Groq** | API gratuite, latence faible |
| **Human-in-the-loop** | `stop_at=insights|backlog` — revue PO avant stories |

---

## Frameworks de priorisation

- **RICE** : (Reach × Impact × Confidence) / Effort
- **WSJF** : Cost of Delay / Effort  
- **MoSCoW** : Must / Should / Could / Won't (mappé depuis RICE par quartiles)

---

## Robustesse

| Aspect | Implémentation |
|--------|----------------|
| Limites | MAX_FEEDBACKS, MAX_TEXT_LENGTH, MAX_INGEST_SIZE_MB |
| Validation | `validate_and_prepare_feedback()` — tronque, limite |
| Résilience | Erreurs isolées par item, partial success, state["errors"] |
| Batching | FeedbackAgent : lots de 3 pour réduire appels LLM |
