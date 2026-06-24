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

from app.agents.intake_agent import (
    intake_agent,
)

from app.agents.research_agent import (
    research_agent,
)

from app.agents.writer_agent import (
    writer_agent,
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
    "intake",
    intake_agent,
)

workflow.add_node(
    "research",
    research_agent,
)

workflow.add_node(
    "writer",
    writer_agent,
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
    "intake",
)

workflow.add_edge(
    "intake",
    "research",
)

workflow.add_edge(
    "research",
    "writer",
)

workflow.add_edge(
    "writer",
    "save_and_export",
)

workflow.add_edge(
    "save_and_export",
    END,
)


proposal_graph = workflow.compile()