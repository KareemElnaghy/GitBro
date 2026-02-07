"""Navigator Agent - Maps repository structure and identifies entry points."""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from src.state import AgentState
from src.utils import extract_json
import os

# Set OpenAI configuration
os.environ["OPENAI_API_KEY"] = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhZXNKN2kxNGNidnVuTU40MTJrOU5yZ2ROeENhTlJudTNPbC1TU08ycFlJIn0.eyJleHAiOjE3NzA0NDI4MTIsImlhdCI6MTc3MDQ0MTAxMiwiYXV0aF90aW1lIjoxNzcwNDQxMDExLCJqdGkiOiJmZjUxMTdhNC04NGE2LTRjMjktYjk0OC0wMTg3NzY2MWZkODciLCJpc3MiOiJodHRwczovL2F1dGgubWNraW5zZXkuaWQvYXV0aC9yZWFsbXMvciIsImF1ZCI6ImJjZDIzNzI4LTNkMjctNDQ3Yy1hMGE5LWVhY2FmMzkzYTZmNSIsInN1YiI6IjZhZjEyNDMxLWUzYWMtNGM3Mi1hYjZhLTY5ZjI4ODlmYzZmYSIsInR5cCI6IklEIiwiYXpwIjoiYmNkMjM3MjgtM2QyNy00NDdjLWEwYTktZWFjYWYzOTNhNmY1Iiwic2Vzc2lvbl9zdGF0ZSI6ImRiNzUwODQ5LWJlMmUtNDk4NC04NmZkLWMyOGY3MThjZWFhZiIsImF0X2hhc2giOiIzMlVsT3dMMm8wUlNvUmVtX3gzUDlRIiwibmFtZSI6IlJpY2hhcmQgQ291cGVydGh3YWl0ZSIsImdpdmVuX25hbWUiOiJSaWNoYXJkIiwiZmFtaWx5X25hbWUiOiJDb3VwZXJ0aHdhaXRlIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYjJiZWVkNDk3YjdkYzRmZiIsImVtYWlsIjoiUmljaGFyZF9Db3VwZXJ0aHdhaXRlQG1ja2luc2V5LmNvbSIsImFjciI6IjEiLCJzaWQiOiJkYjc1MDg0OS1iZTJlLTQ5ODQtODZmZC1jMjhmNzE4Y2VhYWYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZm1ubyI6IjMxNjczNyIsImdyb3VwcyI6WyIyOTA3ZmExYy02ODNmLTRjZjctODU1NS04YzM0YTE2Yzg4ZDgiLCJBbGwgRmlybSBVc2VycyIsIjAzYjE1YTM0LTY1NWUtNGVjNC04MzRhLWI5ZGRhMTk3MjBmMCJdfQ.ZSSU7ZL8l5o3KFoU0fhBtwapRddVm5Nz9o1mnIBj_3XYifi77shBUsRVm2cVEL3uxLTwYpybBSet2Q64O4NZJYOlfjjlukZHUeiot79mL3iTDyprzns34ldBnWtIbUZD4S-VF7FCPbgsRmQIlPlm8BCR9UQhjgQ3Lt_fCOuyfQli5-RZU6ypESIzFsZ-X3ROKFzzmym1fif0paxcyfZiZx8gFrI_Py0fxa1pznuiSNGzJRcnSmuKQIARn0AfJGvm9VB07e5btuslRx4w1sexSy9vbJayPezt0EL3_-RDDsAUZ7u3Q3PjgVlcRfv0INgPpQjBncmSFvjsB-IPxkep8g"
os.environ["OPENAI_BASE_URL"] = "https://openai.prod.ai-gateway.quantumblack.com/2907fa1c-683f-4cf7-8555-8c34a16c88d8/v1"

# Initialize LLM (OpenAI)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
)


def _build_tree_view(file_tree: List[Dict]) -> str:
    """Build a nested directory tree view from flat file list."""
    tree = {}
    for f in file_tree:
        # Only include files (blobs), directories are inferred from paths
        if f.get("type") != "blob":
            continue
        parts = f["path"].split("/")
        node = tree
        for part in parts[:-1]:
            existing = node.get(part)
            if existing is None or not isinstance(existing, dict):
                node[part] = {}
            node = node[part]
        # Mark files with None (only if not already a directory)
        if parts[-1] not in node or node[parts[-1]] is None:
            node[parts[-1]] = None

    lines = []

    def _render(node: dict, prefix: str = ""):
        items = sorted(node.items(), key=lambda x: (x[1] is None, x[0]))
        for i, (name, children) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            if children is None:
                lines.append(f"{prefix}{connector}{name}")
            else:
                child_count = _count_files(children)
                lines.append(f"{prefix}{connector}{name}/ ({child_count} files)")
                extension = "    " if is_last else "│   "
                _render(children, prefix + extension)

    _render(tree)
    return "\n".join(lines)


def _count_files(node: dict) -> int:
    """Count total files in a nested tree node."""
    count = 0
    for v in node.values():
        if v is None:
            count += 1
        else:
            count += _count_files(v)
    return count


def navigator_agent(state: AgentState) -> Dict:
    """
    NAVIGATOR: Maps repo structure and identifies entry points.
    Reads file_tree, readme_content, and config_files from state.
    Returns navigator_map with architecture info.
    """
    file_tree = state["file_tree"]
    metadata = state["metadata"]
    readme_content = state.get("readme_content")
    config_files = state.get("config_files", {})
    total_files = len(file_tree)

    # Build full nested directory tree
    tree_view = _build_tree_view(file_tree)
    # Truncate if extremely large (keep first 200 lines)
    tree_lines = tree_view.split("\n")
    if len(tree_lines) > 200:
        tree_view = "\n".join(tree_lines[:200]) + f"\n... and {len(tree_lines) - 200} more entries"

    # README section
    readme_section = ""
    if readme_content:
        readme_section = f"\nREADME CONTENT:\n{readme_content[:3000]}\n"

    # Config/dependency files section
    config_section = ""
    if config_files:
        config_section = "\nCONFIG & DEPENDENCY FILES:\n"
        for fname, content in config_files.items():
            config_section += f"\n--- {fname} ---\n{content[:1500]}\n"

    prompt = f"""You are a repository structure analyst. Analyze this GitHub repository and output valid JSON only.

REPOSITORY: {metadata['full_name']}
LANGUAGE: {metadata['language']}
DESCRIPTION: {metadata['description']}
TOTAL FILES: {total_files}

COMPLETE FILE TREE:
{tree_view}
{readme_section}
{config_section}
Analyze the repository and identify:
1. Entry points - files that start the application (main.py, app.py, manage.py, index.js, server.js, etc.)
2. Core modules - ALL important directories and files with their purpose
3. Dependencies - ACTUAL libraries from the config/dependency files above (do NOT guess)
4. Architecture type - choose the MOST SPECIFIC type that fits

RESPOND WITH VALID JSON ONLY (no markdown, no code blocks):
{{
  "entry_points": ["list of entry point files with paths"],
  "core_modules": ["list of ALL important directories/files"],
  "core_modules_detailed": [
    {{"path": "src/models/", "purpose": "Database models and ORM definitions"}},
    {{"path": "app.py", "purpose": "Main Flask application entry point"}}
  ],
  "dependencies": ["actual dependencies from config files"],
  "architecture_type": "one of the types below",
  "project_summary": "2-3 sentence summary of what this project does and how it works",
  "confidence_score": 0.85
}}

ARCHITECTURE TYPES (pick the best match):
- "Web Application (Full-Stack)" - has both frontend and backend
- "Web API / REST Service" - backend API only (Flask, FastAPI, Express, etc.)
- "Desktop GUI Application" - uses tkinter, PyQt, Kivy, Electron, etc.
- "CLI Tool" - command-line only, no GUI, no web server
- "Data Science / ML Pipeline" - Jupyter notebooks, model training, data processing
- "Mobile Application" - React Native, Flutter, Swift, Kotlin
- "Library / Package" - meant to be imported by other projects
- "Microservices" - multiple independent services
- "Monolith" - single large application
- "Static Website" - HTML/CSS/JS only
- "DevOps / Infrastructure" - Terraform, Ansible, Docker configs

CRITICAL RULES:
- Look at the ACTUAL file tree and README - do not guess or assume
- If README says it's a GUI app or you see tkinter/PyQt/Kivy/wxPython imports, it is "Desktop GUI Application", NOT "CLI Tool"
- List ALL major directories in core_modules, not just a few
- Read dependencies from the config files provided, do not invent them
- Dependencies MUST be simple strings like "Flask==3.1.2" or "react ^19.2.0". Do NOT use key:value object format
- confidence_score: 0.0 to 1.0 based on how much data you have
"""

    try:
        response = llm.invoke(prompt)
        # Extract content from AIMessage object
        response_text = response.content if hasattr(response, 'content') else str(response)
        result = extract_json(response_text)

        # Add README summary from actual content (not LLM-generated)
        if readme_content:
            readme_summary = readme_content[:500].strip()
            if len(readme_content) > 500:
                readme_summary += "..."
            result["readme_summary"] = readme_summary
        else:
            result["readme_summary"] = "No README found"

        return {
            "navigator_map": result,
            "messages": [f"NAVIGATOR: Mapped {len(result.get('entry_points', []))} entry points, "
                         f"{len(result.get('core_modules', []))} modules, "
                         f"architecture: {result.get('architecture_type', 'unknown')}"],
        }
    except Exception as e:
        return {
            "navigator_map": {
                "entry_points": [],
                "core_modules": [],
                "core_modules_detailed": [],
                "dependencies": [],
                "architecture_type": "unknown",
                "confidence_score": 0.0,
                "project_summary": "Analysis failed",
                "readme_summary": "No README found",
            },
            "errors": [f"Navigator error: {e}"],
            "messages": [f"NAVIGATOR: Failed - {e}"],
        }
