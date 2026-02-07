#!/usr/bin/env python3
"""
GitBro - A multi-agent system for analyzing GitHub repositories
and generating onboarding guides.
"""
import sys
import time
from src.github_client import GitHubClient
from src.graph import run_analysis


def print_repo_info(metadata: dict):
    """Display repository metadata."""
    print("\n" + "-" * 80)
    print("REPOSITORY INFORMATION")
    print("-" * 80)
    print(f"Name: {metadata['full_name']}")
    print(f"Language: {metadata['language']}")
    print(f"Stars: {metadata['stars']:,}")
    print(f"Forks: {metadata['forks']:,}")
    desc = metadata["description"] or "No description"
    if len(desc) > 80:
        desc = desc[:80] + "..."
    print(f"Description: {desc}")
    print("-" * 80)


def print_agent_outputs(state: dict):
    """Display analysis results from all agents."""
    if state.get("navigator_map"):
        nav = state["navigator_map"]
        print("\n[NAVIGATOR]")
        print(f"  Entry Points: {', '.join(nav.get('entry_points', [])[:5])}")
        print(f"  Core Modules: {', '.join(nav.get('core_modules', [])[:5])}")
        print(f"  Architecture: {nav.get('architecture_type', 'unknown')}")
        print(f"  Confidence: {nav.get('confidence_score', 0):.0%}")

    if state.get("context_summary"):
        print("\n[CONTEXT AGENT]")
        print(state["context_summary"])

    if state.get("mentor_guide"):
        print("\n[MENTOR AGENT]")
        print(state["mentor_guide"])

    if state.get("visualization"):
        print("\n[VISUALIZER]")
        print("Mermaid diagram generated:")
        vis = state["visualization"]
        if len(vis) > 200:
            print(vis[:200] + "...")
        else:
            print(vis)


def print_final_report(report: str):
    """Display final orchestrator report."""
    print("\n" + "=" * 80)
    print("FINAL ONBOARDING REPORT")
    print("=" * 80)
    print(report)
    print("=" * 80)


def print_agent_log(messages: list):
    """Display agent execution log."""
    if not messages:
        return
    print("\nAgent Execution Log:")
    for i, msg in enumerate(messages, 1):
        print(f"  {i}. {msg}")


def main():
    print("\n" + "=" * 80)
    print("GitBro - Repository Analysis")

    if len(sys.argv) < 2:
        print("Error: Missing GitHub repository URL")
        print("\nUsage: python main.py <github_repo_url>")
        print("Example: python main.py https://github.com/tiangolo/fastapi")
        sys.exit(1)

    repo_url = sys.argv[1]
    print(f"Analyzing: {repo_url}\n")

    try:
        github_client = GitHubClient()
    except Exception as e:
        print(f"Error: Failed to initialize GitHub client: {e}")
        sys.exit(1)

    start_time = time.time()

    try:
        print("Running multi-agent analysis...")
        final_state = run_analysis(repo_url, github_client)

        elapsed_time = time.time() - start_time
        print(f"\nAnalysis complete in {elapsed_time:.1f}s")

        print_repo_info(final_state["metadata"])
        print_agent_outputs(final_state)

        if final_state.get("final_report"):
            print_final_report(final_state["final_report"])

        print_agent_log(final_state.get("messages", []))

        if final_state.get("errors"):
            print("\nErrors encountered:")
            for error in final_state["errors"]:
                print(f"  - {error}")

        print(f"\nExecution time: {elapsed_time:.1f}s")
        print(f"Agents executed: {len(final_state.get('messages', []))}")

    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
