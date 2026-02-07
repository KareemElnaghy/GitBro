"""State schema for LangGraph multi-agent workflow."""
from typing import Dict, List, Optional, TypedDict, Annotated
from operator import add


class AgentState(TypedDict):
    """Shared state passed between all agents."""

    # Input
    repo_url: str

    # GitHub Data (from API)
    owner: str
    repo_name: str
    metadata: Dict  # stars, language, description
    file_tree: List[Dict]  # [{path, type, size}]
    code_samples: Dict[str, str]  # {filename: content}
    readme_content: Optional[str]  # README text fetched once upfront

    # Agent Outputs
    navigator_map: Optional[Dict]  # entry_points, core_modules, dependencies
    context_output: Optional[Dict]  # structured code analysis (functions, classes, etc.)
    context_summary: Optional[str]  # human-readable code analysis summary
    mentor_guide: Optional[str]  # onboarding sequence
    visualization: Optional[str]  # Mermaid diagram
    final_report: Optional[str]  # orchestrator synthesis

    # Workflow Control
    messages: Annotated[List[str], add]  # agent communication log
    errors: Annotated[List[str], add]  # error tracking
