"""Navigator Agent - Maps repository structure and identifies entry points."""
import json
from typing import Dict
from langchain_ollama import OllamaLLM
from src.state import AgentState

# Initialize LLM (Ollama)
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


def navigator_agent(state: AgentState) -> Dict:
    """
    NAVIGATOR: Maps repo structure and identifies entry points.
    Reads file_tree and readme_content from state, returns navigator_map.
    """
    file_tree = state["file_tree"]
    metadata = state["metadata"]
    readme_content = state.get("readme_content")
    total_files = len(file_tree)

    # Group files by top-level directory
    directories = {}
    for f in file_tree:
        parts = f["path"].split("/")
        dir_name = parts[0] if len(parts) > 1 else "root"
        if dir_name not in directories:
            directories[dir_name] = []
        directories[dir_name].append(f["path"])

    # Create concise directory structure for LLM
    dir_summary = []
    for dir_name, files in sorted(directories.items()):
        file_count = len(files)
        key_files = [f for f in files if any(f.endswith(ext) for ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".html", ".md", ".txt"])]
        sample_files = key_files[:10]

        dir_summary.append(f"\n{dir_name}/ ({file_count} files)")
        for file in sample_files:
            dir_summary.append(f"  - {file}")
        if len(key_files) > 10:
            dir_summary.append(f"  ... and {len(key_files) - 10} more files")

    file_tree_view = "\n".join(dir_summary)

    prompt = f"""You are a repository structure analyst. Analyze this GitHub repository and output valid JSON only.

REPOSITORY: {metadata['full_name']}
LANGUAGE: {metadata['language']}
DESCRIPTION: {metadata['description']}
TOTAL FILES: {total_files}

FILE TREE:
{file_tree_view}

Identify:
1. Entry points (main.py, app.py, index.js, server.js, etc.)
2. Core modules (ALL key directories/files)
3. Dependencies (external libraries from package files)
4. Architecture type: Client-Server, Microservices, Monolith, Library, CLI Tool, or Mobile App

RESPOND WITH VALID JSON ONLY (no markdown, no code blocks):
{{
  "entry_points": ["list of entry point files"],
  "core_modules": ["list of important directories/files"],
  "dependencies": ["detected dependencies"],
  "architecture_type": "specific architecture type",
  "confidence_score": 0.0
}}

RULES:
- Analyze ALL {total_files} files - do not skip directories
- If you see both frontend and backend folders, this is client-server architecture
- Include ALL major folders in core_modules
- confidence_score should be 0.0 to 1.0
"""

    try:
        response = llm.invoke(prompt)
        result = _extract_json(response)

        # Add README summary
        if readme_content:
            readme_summary = readme_content[:500].strip()
            if len(readme_content) > 500:
                readme_summary += "..."
            result["readme_summary"] = readme_summary
        else:
            result["readme_summary"] = "No README found"

        return {
            "navigator_map": result,
            "messages": [f"NAVIGATOR: Mapped {len(result.get('entry_points', []))} entry points, architecture: {result.get('architecture_type', 'unknown')}"],
        }
    except Exception as e:
        return {
            "navigator_map": {
                "entry_points": [],
                "core_modules": [],
                "dependencies": [],
                "architecture_type": "unknown",
                "confidence_score": 0.0,
                "readme_summary": "No README found",
            },
            "errors": [f"Navigator error: {e}"],
            "messages": [f"NAVIGATOR: Failed - {e}"],
        }
