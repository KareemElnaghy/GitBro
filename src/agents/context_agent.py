"""Context Agent - Analyzes source code and extracts key components."""
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


def _select_priority_files(code_samples: Dict[str, str], navigator_map: Dict, max_files: int = 25) -> Dict[str, str]:
    """Pick the most important files for the LLM prompt, guided by navigator output."""
    entry_points = set(navigator_map.get("entry_points", []))
    core_modules = navigator_map.get("core_modules", [])

    priority = {}
    rest = {}

    for path, content in code_samples.items():
        # Entry points go first
        if path in entry_points:
            priority[path] = content
        # Files inside core module directories
        elif any(path.startswith(m.rstrip("/")) for m in core_modules):
            priority[path] = content
        else:
            rest[path] = content

    # Take all priority files (up to max), then fill remaining slots
    selected = dict(list(priority.items())[:max_files])
    remaining = max_files - len(selected)
    if remaining > 0:
        selected.update(dict(list(rest.items())[:remaining]))

    return selected


def context_agent(state: AgentState) -> Dict:
    """
    CONTEXT/CODE AGENT: Analyzes actual source code in depth.
    Reads code_samples, config_files, and navigator_map from state.
    Selects the most important files to fit in the LLM prompt.
    Returns context_output (structured) and context_summary (human-readable).
    """
    code_samples = state["code_samples"]
    config_files = state.get("config_files", {})
    navigator_map = state.get("navigator_map", {})

    # Select top files guided by navigator output
    selected = _select_priority_files(code_samples, navigator_map, max_files=25)

    code_section = ""
    for filename, content in selected.items():
        code_section += f"\n=== {filename} ===\n{content[:2000]}\n"

    files_included = len(selected)
    total_files = len(code_samples)

    # Include config files so the LLM can see actual dependencies
    config_section = ""
    if config_files:
        config_section = "\n\nCONFIG & DEPENDENCY FILES:\n"
        for fname, content in config_files.items():
            config_section += f"\n--- {fname} ---\n{content[:1000]}\n"

    prompt = f"""You are a code analysis system. Analyze the provided source code thoroughly and return valid JSON only.

REPOSITORY CONTEXT:
- Entry points: {navigator_map.get('entry_points', [])}
- Core modules: {navigator_map.get('core_modules', [])}
- Architecture: {navigator_map.get('architecture_type', 'unknown')}
- Project summary: {navigator_map.get('project_summary', 'N/A')}
- Total source files in repo: {total_files}

SOURCE CODE ({files_included} most important files shown):
{code_section}
{config_section}

Analyze the code and extract:
1. Key functions - important functions with their file, purpose, and parameters
2. Key classes - important classes with their file, purpose, and methods
3. Technologies - ACTUAL frameworks and libraries (from imports AND config files)
4. Design patterns detected in the code
5. Complexity score based on code structure, nesting, and coupling
6. API endpoints if any (REST routes, GraphQL, etc.)
7. Data models if any (database models, schemas)

Return valid JSON only (no markdown, no code blocks):
{{
  "files_analyzed": {files_included},
  "key_functions": [
    {{"name": "function_name", "file": "path/to/file.py", "purpose": "what it does", "params": ["param1", "param2"]}}
  ],
  "key_classes": [
    {{"name": "ClassName", "file": "path/to/file.py", "purpose": "what it represents", "methods": ["method1", "method2"]}}
  ],
  "technologies": ["list of actual technologies from imports and config files"],
  "patterns": ["design patterns found in the code"],
  "complexity_score": 0.5,
  "api_endpoints": [
    {{"method": "GET", "path": "/api/users", "file": "routes.py", "purpose": "List all users"}}
  ],
  "data_models": [
    {{"name": "User", "file": "models.py", "fields": ["id", "name", "email"]}}
  ]
}}

RULES:
- Extract ONLY what you can see in the actual code above - do not invent or guess
- Include up to 10 key functions and 10 key classes
- Technologies must come from actual import statements or config files
- If no API endpoints or data models exist, use empty lists
- complexity_score: 0.0 (simple scripts) to 1.0 (highly complex system)
"""

    try:
        response = llm.invoke(prompt)
        result = extract_json(response)

        summary = f"""Analyzed {files_included} of {total_files} source files.
Technologies: {', '.join(result.get('technologies', [])[:8])}
Key Functions: {len(result.get('key_functions', []))}
Key Classes: {len(result.get('key_classes', []))}
Patterns: {', '.join(result.get('patterns', [])[:5])}
API Endpoints: {len(result.get('api_endpoints', []))}
Data Models: {len(result.get('data_models', []))}
Complexity: {result.get('complexity_score', 0):.1f}/1.0"""

        return {
            "context_output": result,
            "context_summary": summary,
            "messages": [f"CONTEXT: {files_included}/{total_files} files analyzed, "
                         f"{len(result.get('technologies', []))} technologies, "
                         f"{len(result.get('key_functions', []))} functions, "
                         f"{len(result.get('key_classes', []))} classes"],
        }
    except Exception as e:
        return {
            "context_output": {},
            "context_summary": "Error analyzing code",
            "errors": [f"Context agent error: {e}"],
            "messages": [f"CONTEXT: Failed - {e}"],
        }
