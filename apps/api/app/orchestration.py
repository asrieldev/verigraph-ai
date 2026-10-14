from typing import TypedDict

AGENTS = ["Code Review Agent", "Security Agent", "Fix Agent", "Test Agent"]


class PipelineState(TypedDict):
    completed: list[str]


def agent_order() -> list[str]:
    """Execute the coordination graph; retain a fallback for minimal demo installs."""
    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore[import-not-found]
    except ImportError:
        return AGENTS.copy()

    graph = StateGraph(PipelineState)
    previous = START
    for index, name in enumerate(AGENTS):
        node_name = f"agent_{index}"

        def complete(state: PipelineState, agent_name: str = name) -> PipelineState:
            return {"completed": [*state["completed"], agent_name]}

        graph.add_node(node_name, complete)
        graph.add_edge(previous, node_name)
        previous = node_name
    graph.add_edge(previous, END)
    result = graph.compile().invoke({"completed": []})
    return list(result["completed"])
