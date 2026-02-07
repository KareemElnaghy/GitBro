"""LangGraph workflow orchestrating 5 agents sequentially."""
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.navigator_agent import navigator_agent
from src.agents.context_agent import context_agent
from src.agents.mentor_agent import mentor_agent
from src.agents.visualizer_agent import visualizer_agent
from src.agents.orchestrator_agent import orchestrator_agent


def create_agent_graph():
    """
    Create the LangGraph workflow with sequential agent execution.

    Flow: Navigator -> Context -> Mentor -> Visualizer -> Orchestrator -> END
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("navigator", navigator_agent)
    workflow.add_node("context", context_agent)
    workflow.add_node("mentor", mentor_agent)
    workflow.add_node("visualizer", visualizer_agent)
    workflow.add_node("orchestrator", orchestrator_agent)

    workflow.set_entry_point("navigator")
    workflow.add_edge("navigator", "context")
    workflow.add_edge("context", "mentor")
    workflow.add_edge("mentor", "visualizer")
    workflow.add_edge("visualizer", "orchestrator")
    workflow.add_edge("orchestrator", END)

    return workflow.compile()


def run_analysis(repo_url: str, github_client) -> AgentState:
    """
    Execute full analysis workflow on a GitHub repository.

    Args:
        repo_url: GitHub repository URL
        github_client: Initialized GitHubClient instance

    Returns:
        Final AgentState with all analysis results
    """
    owner, repo_name = github_client.parse_repo_url(repo_url)

    print("Fetching data from GitHub API...")
    metadata = github_client.get_repo_metadata(owner, repo_name)
    branch = metadata["default_branch"]
    file_tree = github_client.get_file_tree(owner, repo_name, branch)
    code_samples = github_client.fetch_top_files(owner, repo_name, branch)

    # Fetch README once upfront so agents don't need their own GitHub client
    readme_content = None
    for readme_file in ["README.md", "README.rst", "README.txt", "README"]:
        try:
            readme_content = github_client.get_raw_content(owner, repo_name, readme_file, branch)
            break
        except Exception:
            continue

    print(f"Fetched {len(file_tree)} files, {len(code_samples)} code samples")

    initial_state: AgentState = {
        "repo_url": repo_url,
        "owner": owner,
        "repo_name": repo_name,
        "metadata": metadata,
        "file_tree": file_tree,
        "code_samples": code_samples,
        "readme_content": readme_content,
        "navigator_map": None,
        "context_output": None,
        "context_summary": None,
        "mentor_guide": None,
        "visualization": None,
        "final_report": None,
        "messages": [],
        "errors": [],
    }

    app = create_agent_graph()

    print("Running 5-agent analysis pipeline...\n")

    final_state = app.invoke(initial_state)

    return final_state
