# Proposal AI Generator & Assistant

An intelligent, multi-agent AI assistant designed to streamline the sales proposal lifecycle. Consultants can upload or paste transcripts of initial client conversations, extract structured client profiles, generate polished `.docx` proposals, perform revisions, and query details using a context-aware Q&A chat.

---

## 🚀 Core Features

1. **Structured Client Profiles**: Automatically extracts client company name, industry, objectives, budget, timeline, and key stakeholders from conversation transcripts.
2. **AI-Driven Proposal Drafting**: Automatically builds a comprehensive, structured proposal containing Executive Summary, Objectives, Scope, Timeline, Pricing, and Conclusion.
3. **Iterative Revisions**: Make natural language revision requests (e.g., *"change timeline to 12 weeks"*) to iteratively rewrite specific proposal sections.
4. **Context-Aware Q&A with Follow-up Support**: Chat with the assistant regarding the current proposal, initial transcript, or client profile. Includes full conversational memory for follow-up questions.
5. **Cross-Thread / Session Memory**: Automatically surfaces details and timelines from previous sessions or proposals linked to the same consultant/user, allowing queries like *"What was the timeline of the proposal for Acme Corp from my other session?"*.
6. **Multi-Session Switcher**: Streamlit interface allows users to switch between active sessions, start new sessions, and load historical data instantly.
7. **Slack & Streamlit Frontends**: Accessible via a Slack bot server or a web-based Streamlit dashboard.

---

## 📁 Codebase Directory Structure

```text
├── app/
│   ├── agents/          # LangGraph node agents (intake, writer, revision, qa, load_memory, save_and_export)
│   ├── config/          # Project configurations & environment settings
│   ├── database/        # Database models (SQLAlchemy), connection settings, and repository functions
│   ├── llm/             # LLM client configuration (Groq Chat LLM)
│   ├── prompts/         # Structured system and human prompts for agents
│   ├── rag/             # Retrieval-augmented generation vector store setup (Qdrant)
│   ├── schemas/         # Pydantic schemas for data validation and LLM structured output
│   ├── services/        # Orchestration layer (Proposal, QA, and Revision services)
│   ├── slack/           # Slack event router, handlers, and tools
│   ├── tools/           # Custom helpers (docx generation, Slack integration)
│   ├── workflows/       # LangGraph workflows and state definitions
│   └── startup.py       # DB initialization and startup tasks
├── docs/                # Project documentation (architecture, decisions)
├── generated_proposals/ # Target directory for output .docx files
├── run.py               # Uvicorn FastAPI startup entry point
├── streamlit_app.py     # Streamlit dashboard client app
├── requirements.txt     # Python package dependencies
└── pyproject.toml       # Python metadata
```

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- **Python 3.11** installed.
- Access to **Groq API** (key for LLM inference).
- A **Qdrant** endpoint and API key (optional for vector search).

### 2. Clone and Setup Environment
Copy the `.env.example` file to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Ensure you provide at least your `GROQ_API_KEY`.

### 3. Create a Virtual Environment & Install Dependencies
```powershell
# Create venv
python -m venv .venv

# Activate venv
.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Qdrant Vector Store
Run the startup script to create the SQLite tables and ingest initial sample proposals into the vector collection:
```powershell
python -c "import app.startup; app.startup.startup_tasks()"
```

### 5. Run the Clients

#### Run the Web Dashboard (Streamlit)
```powershell
streamlit run streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

#### Run the API Bot Server (FastAPI / Slack)
```powershell
python run.py
```
Starts the server at [http://localhost:8000](http://localhost:8000). Set up your Slack app to forward message and file events to `/slack/events`.

---

## 💡 How to Use

### 1. Proposal Generation
- Paste a client conversation transcript into the text area under the **Generate Proposal** tab, then click **Generate**.
- The system will run the intake, research, and writing workflows to generate a structured proposal and Client Profile. It will also compile a `.docx` copy available for download.

### 2. Multi-Session Management
- In the sidebar, select your **User ID** (e.g. `consultant_1`).
- Switch between active sessions or select `➕ Create New Session` to start fresh. This allows you to work on multiple clients concurrently.

### 3. Revision
- Go to the **Revise Proposal** tab, submit a revision instruction (e.g., *"change pricing to $200 per hour and rewrite objectives"*).
- The revision agent will update the proposal, commit it to database, and rebuild the DOCX file.

### 4. Q&A and Cross-Thread Memory
- Go to the **Q&A** tab and chat naturally with the assistant.
- You can ask about current details: *"What are the stakeholders?"*
- You can ask follow-up questions: *"What did we say about their budget again?"*
- You can query details across other sessions: *"Show me the goals specified in my other sessions."*
