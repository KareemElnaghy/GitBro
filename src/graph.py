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
    Clones the repo locally for file reading, uses API for metadata/commits/PRs.
    """
    owner, repo_name = github_client.parse_repo_url(repo_url)

    print("Fetching repository metadata...")
    metadata = github_client.get_repo_metadata(owner, repo_name)

    print("Cloning repository...")
    repo_dir = github_client.clone_repo(repo_url)

    try:
        print("Scanning file tree...")
        file_tree = github_client.walk_local_repo(repo_dir)

        print(f"Reading source code ({len(file_tree)} files in repo)...")
        code_samples = github_client.read_all_source_files(repo_dir, file_tree)

        print("Reading README...")
        readme_content = github_client.read_local_readme(repo_dir)

        print("Reading config & dependency files...")
        config_files = github_client.read_local_config_files(repo_dir, file_tree)
    finally:
        print("Cleaning up clone...")
        github_client.cleanup_clone(repo_dir)

    # Git data via API (commits, PRs)
    print("Fetching commits & pull requests...")
    recent_commits = github_client.get_recent_commits(owner, repo_name)
    pull_requests = github_client.get_pull_requests(owner, repo_name)

    print(f"Data collected: {len(code_samples)} source files, {len(config_files)} config files, "
          f"{len(recent_commits)} commits, {len(pull_requests)} PRs")

    initial_state: AgentState = {
        "repo_url": repo_url,
        "owner": owner,
        "repo_name": repo_name,
        "metadata": metadata,
        "file_tree": file_tree,
        "code_samples": code_samples,
        "readme_content": readme_content,
        "config_files": config_files,
        "recent_commits": recent_commits,
        "pull_requests": pull_requests,
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
