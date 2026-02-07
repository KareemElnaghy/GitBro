"""
GitBro - Streamlit Chat UI for GitHub repository analysis.
Run with: streamlit run app.py
"""
import json
import streamlit as st
from langchain_ollama import OllamaLLM
from src.github_client import GitHubClient
from src.graph import run_analysis

# --- Page config ---
st.set_page_config(page_title="GitBro", page_icon="🔍", layout="wide")

# --- LLM for chat follow-ups ---
llm = OllamaLLM(
    model="qwen2.5-coder:7b",
    temperature=0.3,
    base_url="http://localhost:11434",
)


def build_context(analysis: dict) -> str:
    """Build a context string from analysis results for the chat LLM."""
    nav = analysis.get("navigator_map", {})
    ctx = analysis.get("context_output", {})
    meta = analysis.get("metadata", {})

    # Include actual code samples so the LLM can reference them
    code_section = ""
    for filename, content in list(analysis.get("code_samples", {}).items()):
        code_section += f"\n### {filename}\n```\n{content[:1500]}\n```\n"

    # Include config file contents
    config_section = ""
    for fname, content in list(analysis.get("config_files", {}).items()):
        config_section += f"\n### {fname}\n```\n{content[:800]}\n```\n"

    # Include file tree for structure questions
    file_tree = analysis.get("file_tree", [])
    tree_paths = "\n".join(f["path"] for f in file_tree[:150])
    if len(file_tree) > 150:
        tree_paths += f"\n... and {len(file_tree) - 150} more files"

    # Include recent commits
    commits_section = ""
    for c in analysis.get("recent_commits", [])[:10]:
        commits_section += f"- {c.get('sha', '')[:7]} {c.get('message', '')} (by {c.get('author', 'unknown')})\n"

    # Include PRs
    prs_section = ""
    for pr in analysis.get("pull_requests", [])[:10]:
        prs_section += f"- #{pr.get('number', '')} {pr.get('title', '')} [{pr.get('state', '')}] by {pr.get('author', 'unknown')}\n"

    # Core modules detailed
    modules_detailed = ""
    for m in nav.get("core_modules_detailed", []):
        modules_detailed += f"- {m.get('path', '')}: {m.get('purpose', '')}\n"

    # API endpoints from context
    endpoints_section = ""
    for ep in ctx.get("api_endpoints", []):
        endpoints_section += f"- {ep.get('method', '')} {ep.get('path', '')} ({ep.get('file', '')}) - {ep.get('purpose', '')}\n"

    # Data models from context
    models_section = ""
    for dm in ctx.get("data_models", []):
        models_section += f"- {dm.get('name', '')} ({dm.get('file', '')}): {', '.join(dm.get('fields', []))}\n"

    return f"""You are GitBro, an AI assistant that helps developers understand GitHub repositories.
You have analyzed the repository "{meta.get('full_name', 'unknown')}" and have the following information.
Answer questions based ONLY on this data. Be specific and reference actual file names and code.

## Repository Info
- Name: {meta.get('full_name')}
- Language: {meta.get('language')}
- Stars: {meta.get('stars', 0)}
- Description: {meta.get('description', 'N/A')}

## Architecture (from Navigator Agent)
- Entry Points: {nav.get('entry_points', [])}
- Core Modules: {nav.get('core_modules', [])}
- Dependencies: {nav.get('dependencies', [])}
- Architecture Type: {nav.get('architecture_type', 'unknown')}
- Confidence: {nav.get('confidence_score', 0)}
- Project Summary: {nav.get('project_summary', 'N/A')}
- README Summary: {nav.get('readme_summary', 'N/A')}

### Core Modules Detail
{modules_detailed if modules_detailed else 'N/A'}

## Code Analysis (from Context Agent)
- Files Analyzed: {ctx.get('files_analyzed', 0)}
- Technologies: {ctx.get('technologies', [])}
- Patterns: {ctx.get('patterns', [])}
- Complexity: {ctx.get('complexity_score', 'N/A')}
- Key Functions: {json.dumps(ctx.get('key_functions', []), indent=2)}
- Key Classes: {json.dumps(ctx.get('key_classes', []), indent=2)}

### API Endpoints
{endpoints_section if endpoints_section else 'None detected'}

### Data Models
{models_section if models_section else 'None detected'}

## Onboarding Guide (from Mentor Agent)
{analysis.get('mentor_guide', 'N/A')}

## Architecture Diagram (from Visualizer Agent)
```mermaid
{analysis.get('visualization', 'No diagram available')}
```

## Complete File Tree ({len(file_tree)} files)
{tree_paths}

## Recent Commits
{commits_section if commits_section else 'None available'}

## Pull Requests
{prs_section if prs_section else 'None available'}

## Config Files
{config_section if config_section else 'None found'}

## Code Samples
{code_section}

## Instructions
- When asked about code structure, reference the COMPLETE FILE TREE and core modules above
- When asked about a specific file, look it up in the code samples above
- When asked for a diagram or visualization, output the mermaid diagram
- When asked about onboarding, reference the learning path
- When asked about commits or PRs, reference the recent commits and pull requests above
- When asked about dependencies, reference the config files and dependencies list
- Be concise, specific, and reference actual file names
"""


def get_chat_response(context: str, chat_history: list, user_msg: str) -> str:
    """Send user question to LLM with full analysis context."""
    # Build conversation with context
    conversation = context + "\n\n## Conversation\n"
    for role, msg in chat_history[-6:]:  # Keep last 6 messages for context window
        prefix = "User" if role == "user" else "GitBro"
        conversation += f"{prefix}: {msg}\n\n"
    conversation += f"User: {user_msg}\n\nGitBro:"

    return llm.invoke(conversation)


# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""
if "context" not in st.session_state:
    st.session_state.context = ""

# --- Sidebar ---
with st.sidebar:
    st.title("GitBro 🔍")
    st.caption("AI-powered repository analysis & onboarding")

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/owner/repo",
    )

    analyze_btn = st.button("Analyze Repository", type="primary", use_container_width=True)

    if analyze_btn and repo_url:
        # Reset state for new analysis
        st.session_state.chat_history = []
        st.session_state.analysis = None
        st.session_state.repo_url = repo_url

        with st.status("Analyzing repository...", expanded=True) as status:
            try:
                st.write("Initializing GitHub client...")
                github_client = GitHubClient()

                st.write("Fetching repository data...")
                final_state = run_analysis(repo_url, github_client)

                st.session_state.analysis = final_state
                st.session_state.context = build_context(final_state)

                status.update(label="Analysis complete!", state="complete")
            except Exception as e:
                status.update(label=f"Error: {e}", state="error")

    # Show repo info after analysis
    if st.session_state.analysis:
        meta = st.session_state.analysis["metadata"]
        nav = st.session_state.analysis.get("navigator_map", {})
        ctx = st.session_state.analysis.get("context_output", {})

        st.divider()
        st.subheader(meta.get("full_name", ""))
        st.caption(meta.get("description", ""))

        col1, col2 = st.columns(2)
        col1.metric("Stars", f"{meta.get('stars', 0):,}")
        col2.metric("Language", meta.get("language", "?"))

        st.text(f"Architecture: {nav.get('architecture_type', 'unknown')}")
        st.text(f"Confidence: {nav.get('confidence_score', 0):.0%}")

        if nav.get("entry_points"):
            with st.expander("Entry Points"):
                for ep in nav["entry_points"]:
                    st.code(ep, language=None)

        if nav.get("core_modules_detailed"):
            with st.expander("Core Modules"):
                for m in nav["core_modules_detailed"]:
                    st.text(f"{m.get('path', '')} - {m.get('purpose', '')}")

        if ctx.get("technologies"):
            with st.expander("Technologies"):
                st.write(", ".join(ctx["technologies"]))

        if st.session_state.analysis.get("errors"):
            with st.expander("Errors", expanded=False):
                for err in st.session_state.analysis["errors"]:
                    st.warning(err)

        # Agent log
        msgs = st.session_state.analysis.get("messages", [])
        if msgs:
            with st.expander("Agent Log"):
                for m in msgs:
                    st.text(m)

# --- Main chat area ---
st.title("GitBro Chat")

if not st.session_state.analysis:
    st.info("Enter a GitHub repository URL in the sidebar and click **Analyze Repository** to get started.")
else:
    # Show welcome message on first load
    if not st.session_state.chat_history:
        meta = st.session_state.analysis["metadata"]
        nav = st.session_state.analysis.get("navigator_map", {})
        ctx = st.session_state.analysis.get("context_output", {})

        welcome = f"""I've finished analyzing **{meta.get('full_name')}**! Here's what I found:

- **Architecture**: {nav.get('architecture_type', 'unknown')}
- **Project Summary**: {nav.get('project_summary', 'N/A')}
- **Technologies**: {', '.join(ctx.get('technologies', [])[:5])}
- **Entry Points**: {', '.join(nav.get('entry_points', [])[:3])}
- **Complexity**: {ctx.get('complexity_score', 'N/A')}/1.0
- **Files in repo**: {len(st.session_state.analysis.get('file_tree', []))}
- **Commits analyzed**: {len(st.session_state.analysis.get('recent_commits', []))}

You can ask me anything about this repository. For example:
- "Explain the project structure"
- "What does main.py do?"
- "Show me the architecture diagram"
- "What should I learn first?"
- "What design patterns are used?"
- "What are the recent commits?"
- "List all the dependencies"
"""
        st.session_state.chat_history.append(("assistant", welcome))

    # Render chat history
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    # Chat input
    if user_input := st.chat_input("Ask about the repository..."):
        # Show user message
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_response(
                    st.session_state.context,
                    st.session_state.chat_history,
                    user_input,
                )

            st.markdown(response)
            st.session_state.chat_history.append(("assistant", response))
