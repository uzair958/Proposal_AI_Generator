# System Architecture Documentation

This document describes the high-level system architecture, multi-agent workflows, data flow, and database models of the Proposal AI Assistant.

---

## 🏗️ System Overview

The system is designed as a modular, service-oriented architecture using a decoupled frontend/event layer and a shared database backend:

```mermaid
graph TD
    User([Consultant User])
    
    subgraph Frontend Interfaces
        Streamlit[Streamlit Web App]
        Slack[Slack Bot Server]
    end
    
    subgraph FastAPI Backend
        FastAPIRouter[Slack Event Webhook]
    end
    
    subgraph Orchestration Services
        PropService[Proposal Service]
        RevService[Revision Service]
        QAService[QA Service]
    end
    
    subgraph LangGraph Multi-Agent Engine
        PropGraph[Proposal Generation Graph]
        RevGraph[Revision Graph]
        QAGraph[QA Graph]
    end
    
    subgraph Knowledge & Storage
        SQLite[(SQLite DB)]
        Qdrant[(Qdrant Vector DB)]
        LLM[Groq LLM Client]
    end

    User --> Streamlit
    User --> Slack
    Slack --> FastAPIRouter
    
    Streamlit --> PropService & RevService & QAService
    FastAPIRouter --> PropService & RevService & QAService
    
    PropService --> PropGraph
    RevService --> RevGraph
    QAService --> QAGraph
    
    PropGraph & RevGraph & QAGraph -.-> SQLite
    PropGraph & RevGraph & QAGraph -.-> Qdrant
    PropGraph & RevGraph & QAGraph -.-> LLM
```

---

## 🤖 LangGraph Multi-Agent Workflows

The core orchestration uses **LangGraph** to model stateful agent pipelines. State is stored in a structured dict representing the proposal progress and conversation memory.

### 1. Proposal Generation Graph (`proposal_graph.py`)
Used when a raw transcript is submitted to draft a new proposal.
```mermaid
stateDiagram-v2
    [*] --> load_memory : Load existing transcripts/profiles
    load_memory --> intake : Extract Client Profile (Structured Output)
    intake --> research : Search Qdrant RAG for relevant past cases
    research --> writer : Draft Proposal Sections (Executive Summary, Scope, etc.)
    writer --> save_and_export : Generate docx and persist files/DB records
    save_and_export --> [*]
```

### 2. Revision Graph (`revision_graph.py`)
Triggered when the consultant requests tweaks to specific sections of a generated proposal.
```mermaid
stateDiagram-v2
    [*] --> load_memory : Fetch current active proposal version
    load_memory --> revision : Apply edits via LLM revision prompts
    revision --> save_and_export : Save updated proposal version and docx
    save_and_export --> [*]
```

### 3. Q&A Graph (`qa_graph.py`)
Handles conversational questions regarding transcripts, profiles, proposals, or previous sessions.
```mermaid
stateDiagram-v2
    [*] --> load_memory : Load profile, current proposal, thread history, and cross-thread memory
    load_memory --> answer_question : Process query & output response using Groq Chat LLM
    answer_question --> [*]
```

---

## 💾 Data Modeling & Session Persistence

The database stores all history, metadata, and generated files using **SQLite** with **SQLAlchemy ORM**.

```mermaid
erDiagram
    SESSIONS {
        int id PK
        string slack_user_id "BaseUserID:ChannelID or BaseUserID:SessionUUID"
        datetime created_at
        datetime updated_at
    }
    TRANSCRIPTS {
        int id PK
        int session_id FK
        text content
        datetime uploaded_at
    }
    CLIENT_PROFILES {
        int id PK
        int session_id FK
        string company_name
        string industry
        text problem
        text goals "JSON List"
        string budget
        string timeline
        text stakeholders "JSON List"
        text missing_fields "JSON List"
        datetime created_at
    }
    PROPOSAL_VERSIONS {
        int id PK
        int session_id FK
        int version
        text proposal_json
        string docx_path
        datetime created_at
    }
    MESSAGES {
        int id PK
        int session_id FK
        string role "user / assistant"
        text content
        datetime created_at
    }

    SESSIONS ||--o| TRANSCRIPTS : "belongs to"
    SESSIONS ||--o| CLIENT_PROFILES : "has profile"
    SESSIONS ||--o| PROPOSAL_VERSIONS : "contains versions"
    SESSIONS ||--o| MESSAGES : "has history"
```

---

## 🧠 Memory Systems

### Short-Term Thread Memory
Each session contains its own list of QA questions, answers, and revision requests stored in the `messages` table. When executing any workflow:
- The [load_memory_agent](file:///c:/Users/hp/OneDrive/Desktop/root/proposal-ai-assistant/app/agents/load_memory_agent.py) loads these messages.
- The messages are formatted as a text transcript: `User: ... \n Assistant: ...`.
- This conversation block is passed to the LLM, enabling natural referential follow-up questions.

### Cross-Thread / Session Memory
When a user launches a session, the database key is stored as `base_user_id:session_uuid` (e.g. `consultant_1:f837d-9d7a`). 
- When loading memory, the [load_memory_agent](file:///c:/Users/hp/OneDrive/Desktop/root/proposal-ai-assistant/app/agents/load_memory_agent.py) splits on `:` to resolve the base user `consultant_1`.
- It queries all other active sessions for `consultant_1` and gathers their latest client profiles and proposal contents.
- This cross-thread context is formatted and fed into the QA prompt template, letting the LLM answer queries comparing current and historical proposals.
