# Stack technique

## Stack visuelle (logos)

<p align="center">
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://langchain-ai.github.io/langgraph"><img src="https://img.shields.io/badge/LangGraph-0.0.20+-F15D2F?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" /></a>
  <a href="https://console.groq.com"><img src="https://img.shields.io/badge/Groq-API-000000?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" /></a>
  <a href="https://www.sbert.net"><img src="https://img.shields.io/badge/sentence--transformers-2.2+-DD67D6?style=for-the-badge" alt="sentence-transformers" /></a>
  <a href="https://docs.trychroma.com"><img src="https://img.shields.io/badge/ChromaDB-0.4+-4285F4?style=for-the-badge" alt="ChromaDB" /></a>
  <a href="https://react.dev"><img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" /></a>
  <a href="https://vitejs.dev"><img src="https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" /></a>
  <a href="https://tailwindcss.com"><img src="https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind" /></a>
  <a href="https://docs.pydantic.dev"><img src="https://img.shields.io/badge/Pydantic-2.5+-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" /></a>
</p>

> *Cliquez sur un badge pour accéder à la documentation officielle.*

---

## Comment les technos se connectent

```mermaid
flowchart TB
    subgraph Frontend["🖥️ Frontend"]
        REACT[React 19]
        VITE[Vite 7]
        TAILWIND[Tailwind CSS]
    end

    subgraph API["⚡ API"]
        FASTAPI[FastAPI]
        PYDANTIC[Pydantic]
    end

    subgraph Agent["🤖 Agent"]
        LANGGRAPH[LangGraph]
        GROQ[Groq LLM]
        RAG[sentence-transformers]
        CHROMA[ChromaDB]
    end

    REACT --> VITE
    REACT --> TAILWIND
    Frontend -->|HTTP /api| API
    FASTAPI --> PYDANTIC
    API --> LANGGRAPH
    LANGGRAPH --> GROQ
    LANGGRAPH --> RAG
    RAG --> CHROMA
```

| Connexion | Détail |
|-----------|--------|
| **Frontend → API** | Appels REST sur `/ingest`, `/run`, `/chat`, `/export` |
| **API → LangGraph** | Pipeline déclenché par les routes FastAPI |
| **LangGraph → Groq** | Appels LLM pour Feedback, Priority, Story, Critique, Synthesis |
| **LangGraph → RAG** | Embeddings (sentence-transformers) + recherche (ChromaDB) |

---

## Vue d'ensemble

| Couche | Technologie | Version | Rôle |
|--------|-------------|---------|------|
| **Backend** | Python | 3.10+ | API, pipeline IA |
| **API** | FastAPI | 0.109+ | REST, validation Pydantic |
| **Orchestration** | LangGraph | 0.0.20+ | Pipeline agentique |
| **LLM** | Groq | API | Modèles Llama (gratuit) |
| **RAG** | sentence-transformers | 2.2+ | Embeddings all-MiniLM-L6-v2 |
| **Vector store** | ChromaDB | 0.4+ | Persistance RAG (optionnel) |
| **Frontend** | React | 19 | UI |
| **Build** | Vite | 7 | Bundler frontend |
| **Styling** | Tailwind CSS | 3.4 | UI |

---

## Références officielles

| Techno | Documentation |
|--------|---------------|
| **FastAPI** | [fastapi.tiangolo.com](https://fastapi.tiangolo.com) |
| **LangGraph** | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph) |
| **Groq** | [console.groq.com](https://console.groq.com) |
| **ChromaDB** | [docs.trychroma.com](https://docs.trychroma.com) |
| **sentence-transformers** | [sbert.net](https://www.sbert.net) |
| **React** | [react.dev](https://react.dev) |
| **Vite** | [vitejs.dev](https://vitejs.dev) |
| **Pydantic** | [docs.pydantic.dev](https://docs.pydantic.dev) |

---

## Dépendances Python (pyproject.toml)

```
pydantic>=2.5.0
openai>=1.0.0        # client Groq (API compatible)
fastapi>=0.109.0
uvicorn[standard]
langgraph>=0.0.20
python-dotenv
requests
```

**Optionnelles** :
- `.[rag]` — sentence-transformers (RetrievalAgent)
- `.[chroma]` — chromadb + sentence-transformers
- `.[dev]` — pytest, ruff, pre-commit
