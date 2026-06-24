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

from app.agents.qa_agent import (
    qa_agent,
)


workflow = StateGraph(
    ProposalState
)

workflow.add_node(
    "load_memory",
    load_memory_agent,
)

workflow.add_node(
    "answer_question",
    qa_agent,
)

workflow.set_entry_point(
    "load_memory"
)

workflow.add_edge(
    "load_memory",
    "answer_question",
)

workflow.add_edge(
    "answer_question",
    END,
)

qa_graph = workflow.compile()