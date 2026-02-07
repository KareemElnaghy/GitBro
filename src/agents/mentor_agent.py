"""Mentor Agent - Creates onboarding guide and learning path."""
from typing import Dict
from langchain_ollama import OllamaLLM
from src.state import AgentState
from src.utils import extract_json

# Initialize LLM
llm = OllamaLLM(
    model="qwen2.5-coder:7b",
    temperature=0.1,
    base_url="http://localhost:11434"
)


def mentor_agent(state: AgentState) -> Dict:
    """
    MENTOR: Creates onboarding guide and learning path.
    Reads navigator_map and context_output from state.
    """
    navigator_map = state.get("navigator_map", {})
    context_output = state.get("context_output", {})
    metadata = state["metadata"]

    prompt = f"""You are an engineering onboarding system. Create a learning path and return valid JSON only.

REPOSITORY: {metadata['full_name']}
LANGUAGE: {metadata['language']}

STRUCTURE:
- Entry points: {navigator_map.get('entry_points', [])}
- Core modules: {navigator_map.get('core_modules', [])}
- Architecture: {navigator_map.get('architecture_type', 'unknown')}

CODE ANALYSIS:
- Technologies: {context_output.get('technologies', [])}
- Key patterns: {context_output.get('patterns', [])}
- Complexity: {context_output.get('complexity_score', 0.5)}

Provide:
1. Learning path (ordered steps with time estimates)
2. Prerequisites (required knowledge)
3. Total estimated hours
4. Difficulty level
5. Key concepts to understand

Return valid JSON only (no markdown, no code blocks):
{{
  "learning_path": [
    {{"step": 1, "file": "main.py", "estimated_time": "30min", "concepts": ["FastAPI", "routing"]}}
  ],
  "prerequisites": ["Python basics", "REST APIs"],
  "estimated_total_hours": 3.0,
  "difficulty": "intermediate",
  "key_concepts": ["concept1", "concept2"]
}}

Base time estimates on actual code complexity. Use realistic estimates.
"""

    try:
        response = llm.invoke(prompt)
        result = extract_json(response)

        # Create human-readable guide
        guide = f"""ONBOARDING GUIDE - {metadata['full_name']}

DIFFICULTY: {result['difficulty'].upper()}
ESTIMATED TIME: {result['estimated_total_hours']} hours

PREREQUISITES:
"""
        for p in result["prerequisites"]:
            guide += f"  - {p}\n"

        guide += "\nLEARNING PATH:\n"
        for step in result["learning_path"]:
            guide += f"  {step['step']}. {step['file']} ({step['estimated_time']}) - {', '.join(step['concepts'])}\n"

        guide += f"\nKEY CONCEPTS: {', '.join(result['key_concepts'])}"

        return {
            "mentor_guide": guide,
            "messages": [f"MENTOR: {len(result['learning_path'])} steps, {result['estimated_total_hours']}h total"],
        }
    except Exception as e:
        return {
            "mentor_guide": "Error creating onboarding guide",
            "errors": [f"Mentor agent error: {e}"],
            "messages": [f"MENTOR: Failed - {e}"],
        }
