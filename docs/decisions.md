# Architectural Decisions & Decisions Log (ADRs)

This document contains key Architectural Decision Records (ADRs) made during the design and refactoring of the Proposal AI Assistant.

---

## ADR 1: Stateful Workflow Orchestration using LangGraph
* **Status**: Accepted
* **Context**: The proposal generation lifecycle is multi-phased: loading history, extracting client details, querying past vector documents (RAG), generating multiple markdown sections, creating docx assets, and committing results. A simple linear sequence of LLM calls makes error handling and partial state updates fragile.
* **Decision**: Adopt **LangGraph StateGraph** to define node-based, stateful workflows. 
* **Consequences**: Nodes can easily retrieve or output state variables without tight coupling. If a step fails, the graph state is preserved, and state updates are passed cleanly back to the orchestration layer.

---

## ADR 2: Composite Session Keys for Multi-Session Support
* **Status**: Accepted
* **Context**: Consultants need to generate proposals for multiple clients at the same time. If a user is mapped 1:1 with a Slack user ID or a single session, they cannot switch between different client workspaces without clearing the database.
* **Decision**: Represent sessions using a composite `slack_user_id` string in the format `base_user_id:session_suffix` (where `session_suffix` is a Streamlit session UUID or a Slack Channel ID).
* **Consequences**: 
  - Each Slack channel or Streamlit workspace acts as an independent session with its own transcripts, proposals, and chat log.
  - Cross-thread memory lookup remains possible by splitting the composite string on `:` to resolve the base user ID (`base_user_id`) and querying all associated session rows.

---

## ADR 3: Pure State Updates in Graph Nodes
* **Status**: Accepted
* **Context**: The initial load memory node mutated the dictionary state in-place, which is an anti-pattern that causes silent failure and data inconsistencies when deploying checkpointing or Annotated reducers.
* **Decision**: All nodes must return a **partial state update dictionary** containing only the keys that have changed, leaving the state modification to the LangGraph executor.
* **Consequences**: Clean data flow, robust serialization, and full compatibility with LangGraph's checkpoint persistence models.

---

## ADR 4: Decoupling Database Persistence from LangChain Tool Decorators
* **Status**: Accepted
* **Context**: Wrapping database operations (like `store_proposal`) with `@tool` decorators expects all arguments (including the database `Session`) to be JSON-serializable. Passing a SQLAlchemy connection object caused validation crashes.
* **Decision**: Convert database persistence operations into standard, helper module functions. Call these database helpers directly from within dedicated exporter graph nodes or service layers, bypassing the LangChain tool execution pipeline.
* **Consequences**: No runtime validation errors, cleaner database session handling, and improved separation of concerns between tool calling and data persistence.
