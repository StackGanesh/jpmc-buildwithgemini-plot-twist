# 🎬 PlotTwist — AI Books & Movies Concierge

> An intelligent, personalized concierge agent for discovering books and movies, estimating reading and binge-watch times, managing interactive watchlists, and generating custom concept poster artwork.

![PlotTwist Agent Demo](demo.gif)

---

## 🌟 Overview

**PlotTwist** is a multi-capable AI agent powered by **Google ADK (Agent Development Kit)** and **Gemini 2.5 Flash**. It acts as your ultimate entertainment concierge: whether you need a personalized book recommendation based on your favorite sci-fi movies, want to calculate how long it will take to binge a show or read a novel, manage your personal watch/read list, or generate custom concept poster artwork for upcoming titles!

---

## ✨ Key Features & Google Cloud Tools

PlotTwist integrates a suite of **Google Cloud & Agent Platform** technologies:

| Feature / Google Cloud Tool | Technology Used | Description |
|---|---|---|
| 🧠 **Cross-Session Memory** | **Vertex AI Memory Bank** | Automatically recalls user preferences, favorite genres, directors, and past choices across conversations. |
| 🗄️ **Watchlist Database** | **Google Cloud Firestore** | Stores and manages personal watchlists/readlists with status tracking (want to watch, completed) and custom notes. |
| 🔍 **Grounded Knowledge Base** | **Vertex AI RAG Engine** | Grounded retrieval corpus storing rich book and movie metadata for accurate, non-hallucinated recommendations. |
| 🎨 **Concept Art Generation** | **Google Cloud Storage (GCS) + Image Tools** | Synthesizes custom cinematic concept posters and serves them securely via public Cloud Storage URLs. |
| 🎴 **Rich Visual UI** | **A2UI (Agent-to-User Interface v0.8)** | Emits structured UI cards, columns, lists, and images rendered dynamically in the chat UI. |
| 🚀 **Serverless Runtime** | **Agent Engine & Cloud Run** | Deployed on Google Cloud Agent Runtime with a lightweight FastAPI proxy hosted on Cloud Run. |

---

## 🏗️ Project Architecture

```
plot-twist/
├── app/                        # ADK Agent Core Logic
│   ├── agent.py                # Main agent definition & orchestration
│   ├── a2ui_utils.py           # A2UI v0.8 message formatting & card callbacks
│   ├── firestore_tools.py      # Firestore watchlist CRUD tools
│   ├── rag_tools.py            # Vertex AI RAG Engine search tool
│   ├── image_tools.py          # Concept poster artwork tool & GCS uploader
│   ├── media_tools.py          # Reading & binge time estimation tools
│   ├── fast_api_app.py         # Agent Engine FastAPI wrapper
│   └── app_utils/              # A2A protocol helpers
├── frontend/                   # Web Chat Frontend & Proxy
│   ├── main.py                 # FastAPI proxy server (A2A client)
│   └── static/index.html       # Web UI with A2UI renderer
├── record_demo.py              # Automated Playwright demo recording script
├── demo.gif                    # Animated inline demo recording
├── pyproject.toml              # Dependencies & project settings
└── README.md                   # Project documentation
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Google Cloud SDK (`gcloud`)

### 1. Installation
```bash
# Clone repository and install dependencies
uv pip install -e .
```

### 2. Run Locally
```bash
# Launch the agent playground
agents-cli playground

# Or launch the frontend server
uv run python frontend/main.py
```

---

## 🚀 Deployment

### Deploy Agent to Agent Engine
```bash
agents-cli deploy --no-confirm-project
```

### Deploy Frontend to Cloud Run
```bash
gcloud run deploy plot-twist-frontend \
  --source frontend \
  --region us-east1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/356173146024/locations/us-east1/reasoningEngines/3668023566818869248" \
  --clear-base-image --quiet
```

---

## 📄 License

Built with Google ADK for the Google Agent Platform.
