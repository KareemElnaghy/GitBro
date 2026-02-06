"""Navigator Agent - Maps repository structure and identifies entry points."""
import os
import json
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import AgentState
from src.github_client import GitHubClient
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)


def navigator_agent(state: AgentState) -> Dict:
    """
    NAVIGATOR: Maps repo structure and identifies entry points.
    Returns structured NavigatorOutput including README summary.
    """
    file_tree = state["file_tree"]
    metadata = state["metadata"]
    owner = state["owner"]
    repo_name = state["repo_name"]
    
    # Fetch README content
    github_client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    readme_content = None
    readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
    for readme_file in readme_files:
        try:
            readme_content = github_client.get_raw_content(owner, repo_name, readme_file, metadata["default_branch"])
            break
        except:
            continue
    
    # Prepare file tree summary for LLM
    file_list = "\n".join([
        f"- {f['path']} ({f['type']}, {f['size']} bytes)" 
        for f in file_tree[:50]
    ])
    
    prompt = f"""You are a repository NAVIGATOR agent. Analyze this GitHub repository structure.

REPOSITORY: {metadata['full_name']}
LANGUAGE: {metadata['language']}
DESCRIPTION: {metadata['description']}

FILE TREE (All Files):
{file_list}

YOUR TASK: Create a navigation map by identifying:
1. Entry points (main.py, app.py, index.js, etc.)
2. Core modules (key directories/files)
3. Dependencies (external libraries mentioned in file names)
4. Architecture type (monolith, microservices, library, CLI tool, etc.)

RESPOND WITH VALID JSON ONLY (no markdown):
{{
  "entry_points": ["list of entry point files"],
  "core_modules": ["list of important directories or files"],
  "dependencies": ["detected dependencies from filenames"],
  "architecture_type": "description",
  "confidence_score": 0.0-1.0
}}

RULES:
- Base analysis ONLY on the file tree provided
- No hallucinations - if unsure, mark confidence low
- Focus on facts, not assumptions
"""
    
    messages = [
        SystemMessage(content="You are a repository structure analyst. Output valid JSON only."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        result = json.loads(response.content)
        
        # Add README summary to result (first 500 characters)
        if readme_content:
            readme_summary = readme_content[:500].strip()
            if len(readme_content) > 500:
                readme_summary += "..."
            result["readme_summary"] = readme_summary
        else:
            result["readme_summary"] = "No README found"
        
        state["navigator_map"] = result
        state["messages"].append(f"NAVIGATOR: Mapped {len(result.get('entry_points', []))} entry points")
        
        return state
    except Exception as e:
        state["errors"].append(f"Navigator error: {e}")
        state["navigator_map"] = {
            "entry_points": [],
            "core_modules": [],
            "dependencies": [],
            "architecture_type": "unknown",
            "confidence_score": 0.0,
            "readme_summary": "No README found"
        }
        return state
