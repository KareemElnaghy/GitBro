"""Context Agent - Analyzes source code and extracts key components."""
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


def context_agent(state: AgentState) -> Dict:
    """
    CONTEXT/CODE AGENT: Analyzes actual source code.
    Returns context_output (structured) and context_summary (human-readable).
    """
    code_samples = state["code_samples"]
    navigator_map = state.get("navigator_map", {})

    # Prepare code snippets summary
    code_summary = ""
    for filename, content in list(code_samples.items())[:10]:
        code_summary += f"\n=== {filename} ===\n{content[:500]}...\n"

    prompt = f"""You are a code analysis system. Analyze the provided source code and return valid JSON only.

REPOSITORY CONTEXT:
- Entry points: {navigator_map.get('entry_points', [])}
- Core modules: {navigator_map.get('core_modules', [])}

CODE SAMPLES:
{code_summary}

Extract:
1. Key functions (name, file, purpose)
2. Key classes (name, file, purpose)
3. Technologies used (frameworks, libraries)
4. Design patterns detected
5. Complexity score (0-1, based on code structure)

Return valid JSON only (no markdown, no code blocks):
{{
  "files_analyzed": 10,
  "key_functions": [{{"name": "func", "file": "path", "purpose": "desc"}}],
  "key_classes": [{{"name": "Class", "file": "path", "purpose": "desc"}}],
  "technologies": ["list"],
  "patterns": ["design patterns found"],
  "complexity_score": 0.5
}}

Extract only what is visible in the code. Limit to top 5 functions and 5 classes.
"""

    try:
        response = llm.invoke(prompt)
        result = _extract_json(response)

        summary = f"""Analyzed {result['files_analyzed']} files.
Technologies: {', '.join(result['technologies'][:5])}
Key Functions: {len(result['key_functions'])}
Key Classes: {len(result['key_classes'])}
Complexity: {result['complexity_score']:.1f}/1.0"""

        return {
            "context_output": result,
            "context_summary": summary,
            "messages": [f"CONTEXT: {result['files_analyzed']} files, {len(result['technologies'])} technologies"],
        }
    except Exception as e:
        return {
            "context_output": {},
            "context_summary": "Error analyzing code",
            "errors": [f"Context agent error: {e}"],
            "messages": [f"CONTEXT: Failed - {e}"],
        }
