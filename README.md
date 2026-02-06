# GitBro - Navigator Agent

An agentic AI solution for onboarding new employees by intelligently analyzing GitHub repositories.

## Overview

The **Navigator Agent** is responsible for understanding the structure of any GitHub repository and generating comprehensive onboarding reports. It uses LangChain and LangGraph to orchestrate a multi-step analysis workflow.

## Features

- **Repository Structure Analysis**: Maps out the complete directory structure
- **Key File Identification**: Finds and extracts important files (README, configs, docs)
- **Dependency Analysis**: Analyzes code dependencies and import relationships
- **Technology Stack Detection**: Automatically detects languages, frameworks, and tools
- **Architecture Insights**: Uses LLM to identify architectural patterns and design principles
- **Entry Point Discovery**: Finds main entry points and key modules
- **Structured Reports**: Generates comprehensive onboarding documentation

## Architecture

The Navigator Agent uses a **LangGraph workflow** with the following nodes:

```
fetch_structure → identify_key_files → analyze_dependencies → 
detect_tech_stack → analyze_architecture → find_entry_points → generate_report
```

### Components

- **navigator_agent.py**: Main agent orchestration with LangGraph
- **github_tools.py**: GitHub API integration for fetching repository data
- **dependency_analyzer.py**: Extracts and analyzes code dependencies
- **tech_stack_detector.py**: Detects technologies from files and dependencies
- **entry_point_finder.py**: Identifies main entry points and key modules

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd gitbro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Required API Keys

- **GitHub Token**: Create at https://github.com/settings/tokens
  - Required scopes: `repo` (for private repos) or public access
- **OpenAI API Key**: Get from https://platform.openai.com/api-keys

## Usage

### Basic Example

```python
from navigator_agent import NavigatorAgent
import os

# Initialize the agent
navigator = NavigatorAgent(
    github_token=os.getenv("GITHUB_TOKEN"),
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Analyze a repository
report = navigator.analyze_repository("https://github.com/owner/repo")
print(report)
```

### Command Line Usage

```bash
python navigator_agent.py
```

## Output Example

The Navigator generates a structured report including:

- **Repository Overview**: Purpose, description, tech stack
- **Project Structure**: Directory organization and file layout
- **Key Files**: Important configuration and documentation files
- **Architecture**: Patterns, design principles, and code organization
- **Entry Points**: Main modules and startup files
- **Dependencies**: External packages and internal relationships

## API Reference

### NavigatorAgent

Main class for repository analysis.

#### Methods

- `analyze_repository(repo_url: str) -> str`: Analyzes a GitHub repository and returns onboarding report
- Individual node methods can be called separately for granular analysis

### GitHubClient

Client for GitHub API interactions.

#### Methods

- `get_repo_structure(owner, repo, path="")`: Get directory structure
- `get_file_content(owner, repo, file_path)`: Fetch file contents
- `get_key_files(owner, repo)`: Identify and fetch key files
- `get_repo_languages(owner, repo)`: Get programming languages used

## Configuration

### Customizing the Analysis

You can modify the workflow by editing `navigator_agent.py`:

```python
# Add custom nodes
workflow.add_node("custom_analysis", self.custom_analysis_func)

# Modify workflow edges
workflow.add_edge("detect_tech_stack", "custom_analysis")
workflow.add_edge("custom_analysis", "analyze_architecture")
```

### Tech Stack Detection

Add custom technology indicators in `tech_stack_detector.py`:

```python
TECH_INDICATORS = {
    "your-config.yml": ["Your Framework"],
    # ... add more
}
```

## Limitations

- GitHub API rate limits apply (5000 requests/hour for authenticated users)
- Large repositories may take longer to analyze
- Private repos require appropriate token permissions
- OpenAI API costs apply based on usage

## Future Enhancements

- [ ] Support for other version control systems (GitLab, Bitbucket)
- [ ] Caching mechanism for faster re-analysis
- [ ] Interactive chat interface for Q&A about the codebase
- [ ] Code quality metrics and recommendations
- [ ] Diagram generation (architecture diagrams, dependency graphs)
- [ ] Support for monorepos with multiple projects

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
