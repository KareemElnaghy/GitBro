#!/usr/bin/env python3
"""
Test individual agents to verify they're working correctly.
Run each agent separately and display outputs.

Usage: python tests/test_agents.py <github_repo_url>
Example: python tests/test_agents.py https://github.com/tiangolo/fastapi
"""
import sys
import json
from src.github_client import GitHubClient
from src.state import AgentState
from src.agents.navigator_agent import navigator_agent
from src.agents.context_agent import context_agent
from src.agents.mentor_agent import mentor_agent
from src.agents.visualizer_agent import visualizer_agent
from src.agents.orchestrator_agent import orchestrator_agent


def print_separator(title: str):
    """Print a visual separator."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def apply_updates(state: dict, updates: dict) -> dict:
    """Merge agent partial updates into the full state (mimics LangGraph reducer)."""
    for key, value in updates.items():
        if key in ("messages", "errors") and isinstance(value, list):
            # These fields use the `add` reducer in LangGraph
            state[key] = state.get(key, []) + value
        else:
            state[key] = value
    return state


def test_navigator(state: dict) -> dict:
    """Test Navigator Agent."""
    print_separator("TESTING NAVIGATOR AGENT")

    print(f"  Repository: {state['metadata']['full_name']}")
    print(f"  Files in tree: {len(state['file_tree'])}")
    print(f"  Running navigator_agent()...\n")

    updates = navigator_agent(state)
    state = apply_updates(state, updates)

    if state.get("navigator_map"):
        nav_map = state["navigator_map"]
        print("Navigator Output:")
        print(json.dumps(nav_map, indent=2))
        print(f"\n  Entry points found: {len(nav_map.get('entry_points', []))}")
        print(f"  Core modules: {len(nav_map.get('core_modules', []))}")
        print(f"  Dependencies detected: {len(nav_map.get('dependencies', []))}")
        print(f"  Architecture type: {nav_map.get('architecture_type')}")
        print(f"  Confidence score: {nav_map.get('confidence_score', 0):.0%}")

    if state.get("errors"):
        print(f"\nErrors: {state['errors']}")

    return state


def test_context(state: dict) -> dict:
    """Test Context Agent."""
    print_separator("TESTING CONTEXT AGENT")

    print(f"  Code samples: {len(state['code_samples'])} files")
    for filename in list(state["code_samples"].keys())[:3]:
        lines = state["code_samples"][filename].count("\n")
        print(f"    - {filename} ({lines} lines)")
    print(f"  Running context_agent()...\n")

    updates = context_agent(state)
    state = apply_updates(state, updates)

    if state.get("context_summary"):
        print("Context Summary:")
        print(state["context_summary"])

    if state.get("context_output"):
        print("\nDetailed Analysis:")
        print(json.dumps(state["context_output"], indent=2))

    if state.get("errors"):
        print(f"\nErrors: {state['errors']}")

    return state


def test_mentor(state: dict) -> dict:
    """Test Mentor Agent."""
    print_separator("TESTING MENTOR AGENT")

    print(f"  Navigator map: {bool(state.get('navigator_map'))}")
    print(f"  Context output: {bool(state.get('context_output'))}")
    print(f"  Running mentor_agent()...\n")

    updates = mentor_agent(state)
    state = apply_updates(state, updates)

    if state.get("mentor_guide"):
        print("Mentor Guide:")
        print(state["mentor_guide"])

    if state.get("errors"):
        print(f"\nErrors: {state['errors']}")

    return state


def test_visualizer(state: dict) -> dict:
    """Test Visualizer Agent."""
    print_separator("TESTING VISUALIZER AGENT")

    print(f"  Navigator map: {bool(state.get('navigator_map'))}")
    print(f"  Context output: {bool(state.get('context_output'))}")
    print(f"  Running visualizer_agent()...\n")

    updates = visualizer_agent(state)
    state = apply_updates(state, updates)

    if state.get("visualization"):
        print("Mermaid Diagram:")
        print(state["visualization"])

    if state.get("errors"):
        print(f"\nErrors: {state['errors']}")

    return state


def test_orchestrator(state: dict) -> dict:
    """Test Orchestrator Agent."""
    print_separator("TESTING ORCHESTRATOR AGENT")

    print(f"  Navigator map: {bool(state.get('navigator_map'))}")
    print(f"  Context summary: {bool(state.get('context_summary'))}")
    print(f"  Mentor guide: {bool(state.get('mentor_guide'))}")
    print(f"  Visualization: {bool(state.get('visualization'))}")
    print(f"  Running orchestrator_agent()...\n")

    updates = orchestrator_agent(state)
    state = apply_updates(state, updates)

    if state.get("final_report"):
        print("Final Report:")
        print(state["final_report"])

    if state.get("errors"):
        print(f"\nErrors: {state['errors']}")

    return state


def main():
    """Run individual agent tests."""
    print("\nGitBro - Individual Agent Testing Suite\n")

    if len(sys.argv) < 2:
        print("Error: Missing repository URL")
        print("Usage: python tests/test_agents.py <github_repo_url>")
        print("Example: python tests/test_agents.py https://github.com/tiangolo/fastapi")
        sys.exit(1)

    repo_url = sys.argv[1]
    print(f"Target Repository: {repo_url}\n")

    # Initialize GitHub client and fetch data
    print("Fetching GitHub data...")
    github_client = GitHubClient()
    owner, repo_name = github_client.parse_repo_url(repo_url)

    metadata = github_client.get_repo_metadata(owner, repo_name)
    branch = metadata["default_branch"]
    file_tree = github_client.get_file_tree(owner, repo_name, branch)
    code_samples = github_client.fetch_top_files(owner, repo_name, branch)

    # Fetch README
    readme_content = None
    for readme_file in ["README.md", "README.rst", "README.txt", "README"]:
        try:
            readme_content = github_client.get_raw_content(owner, repo_name, readme_file, branch)
            break
        except Exception:
            continue

    print(f"Fetched {len(file_tree)} files, {len(code_samples)} code samples\n")

    # Initialize state
    state: AgentState = {
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

    # Test each agent individually
    try:
        state = test_navigator(state)
        input("\n[Press Enter to test Context Agent...]")

        state = test_context(state)
        input("\n[Press Enter to test Mentor Agent...]")

        state = test_mentor(state)
        input("\n[Press Enter to test Visualizer Agent...]")

        state = test_visualizer(state)
        input("\n[Press Enter to test Orchestrator Agent...]")

        state = test_orchestrator(state)

        # Final summary
        print_separator("TEST SUMMARY")
        print("All agents tested!\n")
        print("Agent Messages:")
        for msg in state.get("messages", []):
            print(f"  - {msg}")

        if state.get("errors"):
            print("\nErrors encountered:")
            for err in state["errors"]:
                print(f"  - {err}")
        else:
            print("\nNo errors encountered")

    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
