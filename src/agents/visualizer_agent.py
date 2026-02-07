"""Visualizer Agent - Creates Mermaid architecture diagrams."""
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


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, stripping markdown code blocks if present."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def visualizer_agent(state: AgentState) -> Dict:
    """
    VISUALIZER: Creates Mermaid architecture diagrams.
    Reads navigator_map and context_output from state.
    """
    navigator_map = state.get("navigator_map", {})
    context_output = state.get("context_output", {})

    prompt = f"""You are a software architecture diagram generator. Return valid JSON only.

STRUCTURE:
- Entry points: {navigator_map.get('entry_points', [])}
- Core modules: {navigator_map.get('core_modules', [])}
- Architecture: {navigator_map.get('architecture_type', 'unknown')}

CODE COMPONENTS:
- Key functions: {[f['name'] for f in context_output.get('key_functions', [])[:5]]}
- Key classes: {[c['name'] for c in context_output.get('key_classes', [])[:5]]}

Create a Mermaid flowchart showing:
1. Entry points
2. Core modules/components
3. Data flow between components
4. External dependencies

Return valid JSON only (no markdown, no code blocks):
{{
  "mermaid_diagram": "graph TD\\n    A[Entry] --> B[Module]\\n    ...",
  "diagram_type": "flowchart TD",
  "component_count": 5,
  "relationships_mapped": 8
}}

Use valid Mermaid syntax. Keep diagram focused (max 15 nodes). Use proper node IDs without spaces.
"""

    try:
        response = llm.invoke(prompt)
        result = _extract_json(response)

        return {
            "visualization": result["mermaid_diagram"],
            "messages": [f"VISUALIZER: {result['component_count']} components, {result['relationships_mapped']} relationships"],
        }
    except Exception as e:
        return {
            "visualization": "Error creating diagram",
            "errors": [f"Visualizer agent error: {e}"],
            "messages": [f"VISUALIZER: Failed - {e}"],
        }
