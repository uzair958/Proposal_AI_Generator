from langgraph.graph import (
    StateGraph,
    END,
)

from app.workflows.state import (
    ProposalState,
)

from app.agents.load_memory_agent import (
    load_memory_agent,
)

from app.agents.revision_agent import (
    revision_agent,
)

from app.agents.save_and_export import (
    save_and_export_agent,
)


workflow = StateGraph(
    ProposalState
)

workflow.add_node(
    "load_memory",
    load_memory_agent,
)

workflow.add_node(
    "revision",
    revision_agent,
)

workflow.add_node(
    "save_and_export",
    save_and_export_agent,
)

workflow.set_entry_point(
    "load_memory"
)

workflow.add_edge(
    "load_memory",
    "revision",
)

workflow.add_edge(
    "revision",
    "save_and_export",
)

workflow.add_edge(
    "save_and_export",
    END,
)

revision_graph = workflow.compile()