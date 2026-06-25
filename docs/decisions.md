# Architectural Decisions & Decisions Log (ADRs)

This document contains key Architectural Decision Records (ADRs) explaining the system design choices, component justifications, and limitations/production trade-offs.

---

## 🛠️ Technology Justifications

### 1. Vector Database Selection: Qdrant
* **Why Selected**: 
  - **Payload Filtering**: Qdrant offers extremely fast, native payload-based filtering (e.g., filtering strictly by `industry: manufacturing` or `industry: retail`) using a JSON-like match structure. This allows us to restrict similarity searches to relevant domain case studies prior to semantic similarity computation.
  - **Developer Experience**: It has a robust Python SDK (`qdrant-client`) that integrates cleanly with modern libraries.
  - **Memory Efficiency**: For local development, Qdrant can run in-memory or in a local folder with minimal setup.

### 2. Structured Storage: SQLite
* **Why Selected**:
  - **Zero-Setup Portability**: SQLite requires no installation, configuration, or active running process. The database is a single, portable file (`proposal_assistant.db`), which makes running the application locally completely hassle-free.
  - **SQLAlchemy Support**: Full compatibility with SQLAlchemy allows us to model relations (Sessions, Client Profiles, Proposal Versions, Message Logs) cleanly.
  - **Future Migration**: If we migrate to PostgreSQL in production, SQLAlchemy makes the schema transfer trivial since the models remain identical.

### 3. API Framework: FastAPI
* **Why Selected**:
  - **Asynchronous Processing**: FastAPI's support for async handlers makes handling webhooks (like incoming Slack events) highly performant without blocking other operations.
  - **Automatic OpenAPI Docs**: Instantly exposes interactive API docs for developer testing.
  - **Pydantic Validation**: Strong validation of payloads prevents schema mismatch exceptions before they reach database/logic layers.

---

## 🧠 Core Architectural Decisions

### ADR 1: Stateful Workflow Orchestration using LangGraph
* **Status**: Accepted
* **Context**: The proposal generation lifecycle is multi-phased: loading history, extracting client details, querying past vector documents (RAG), generating multiple markdown sections, creating docx assets, and committing results. A simple linear sequence of LLM calls makes error handling and partial state updates fragile.
* **Decision**: Adopt **LangGraph StateGraph** to define node-based, stateful workflows. 
* **Consequences**: Nodes can easily retrieve or output state variables without tight coupling. If a step fails, the graph state is preserved, and state updates are passed cleanly back to the orchestration layer.

### ADR 2: Composite Session Keys for Multi-Session Support
* **Status**: Accepted
* **Context**: Consultants need to generate proposals for multiple clients at the same time. If a user is mapped 1:1 with a Slack user ID or a single session, they cannot switch between different client workspaces without clearing the database.
* **Decision**: Represent sessions using a composite `slack_user_id` string in the format `base_user_id:session_suffix` (where `session_suffix` is a Streamlit session UUID or a Slack Channel ID).
* **Consequences**: 
  - Each Slack channel or Streamlit workspace acts as an independent session with its own transcripts, proposals, and chat log.
  - Cross-thread memory lookup remains possible by splitting the composite string on `:` to resolve the base user ID (`base_user_id`) and querying all associated session rows.

### ADR 3: Pure State Updates in Graph Nodes
* **Status**: Accepted
* **Context**: The initial load memory node mutated the dictionary state in-place, which is an anti-pattern that causes silent failure and data inconsistencies when deploying checkpointing or Annotated reducers.
* **Decision**: All nodes must return a **partial state update dictionary** containing only the keys that have changed, leaving the state modification to the LangGraph executor.
* **Consequences**: Clean data flow, robust serialization, and full compatibility with LangGraph's checkpoint persistence models.

### ADR 4: Decoupling Database Persistence from LangChain Tool Decorators
* **Status**: Accepted
* **Context**: Wrapping database operations (like `store_proposal`) with `@tool` decorators expects all arguments (including the database `Session`) to be JSON-serializable. Passing a SQLAlchemy connection object caused validation crashes.
* **Decision**: Convert database persistence operations into standard, helper module functions. Call these database helpers directly from within dedicated exporter graph nodes or service layers, bypassing the LangChain tool execution pipeline.
* **Consequences**: No runtime validation errors, cleaner database session handling, and improved separation of concerns between tool calling and data persistence.

---

## ⚠️ Limitations & Future Production Enhancements

Under typical development time constraints, certain production-grade features were deferred:

1. **PostgreSQL Migration**: While SQLite is ideal for local development, it lacks support for high-concurrency writes. A production deployment should swap to PostgreSQL (using the same SQLAlchemy models) to enable horizontal scaling.
2. **Slack OAuth Flow**: The Slack integration currently relies on a single static `SLACK_BOT_TOKEN` configured in `.env`. For a multi-tenant application, a database-backed OAuth installation flow is required to handle installation tokens for different workspaces.
3. **LLM Fallback & Rate Limiting**: The system uses Groq's ChatGroq client. Under heavy consultant usage, rate limits could block proposal generation. Adding fallback providers (e.g., falling back to OpenAI or Anthropic if Groq fails) is recommended.
4. **Vector DB Lifecycle**: Currently, database creation completely recreates the Qdrant collection. In production, we need a delta-ingest mechanism to append new proposal documents without resetting the collection.
