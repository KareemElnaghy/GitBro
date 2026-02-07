"""Orchestrator Agent - Synthesizes all findings and creates final report."""
import json
from typing import Dict
from langchain_ollama import OllamaLLM
from src.state import AgentState

# Initialize LLM
llm = OllamaLLM(
    model="qwen2.5-coder:7b",
    temperature=0.1,
    base_url="http://localhost:11434"
)


def orchestrator_agent(state: AgentState) -> Dict:
    """
    ORCHESTRATOR: Synthesizes all agent outputs into a final onboarding report.
    """
    metadata = state["metadata"]
    navigator_map = state.get("navigator_map", {})
    context_summary = state.get("context_summary", "N/A")
    mentor_guide = state.get("mentor_guide", "N/A")
    visualization = state.get("visualization", "N/A")
    errors = state.get("errors", [])

    prompt = f"""You are a technical documentation system. Be factual and concise.

Synthesize all agent findings into a comprehensive onboarding report.

REPOSITORY: {metadata['full_name']}
STARS: {metadata['stars']} | LANGUAGE: {metadata['language']}

AGENT FINDINGS:
1. NAVIGATOR: {json.dumps(navigator_map, indent=2)}
2. CONTEXT: {context_summary}
3. MENTOR: {mentor_guide}
4. VISUALIZER: Diagram generated

ERRORS: {errors if errors else "None"}

Create a structured markdown report with these sections:

# {metadata['full_name']} - Onboarding Report

## Executive Summary
[2-3 sentences about the project]

## Repository Overview
[Key facts from NAVIGATOR]

## Code Analysis
[Key findings from CONTEXT]

## Recommended Learning Path
[Summary from MENTOR]

## Architecture Visualization
[Note about diagram availability]

## Quality Assessment
- Confidence Score: X/10
- Data Quality: [Issues found]
- Recommendations: [Next steps]
"""

    try:
        response = llm.invoke(prompt)

        return {
            "final_report": response,
            "messages": ["ORCHESTRATOR: Final report synthesized"],
        }
    except Exception as e:
        return {
            "final_report": f"Error creating final report: {e}",
            "errors": [f"Orchestrator error: {e}"],
            "messages": [f"ORCHESTRATOR: Failed - {e}"],
        }
