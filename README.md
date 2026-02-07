# GitBro 🤖

**AI-Powered GitHub Repository Analysis & Onboarding Assistant**

GitBro is an intelligent multi-agent system that analyzes GitHub repositories and generates comprehensive onboarding guides for developers. Using LangGraph and specialized AI agents, it maps repository structure, analyzes code patterns, creates learning paths, and generates interactive architecture diagrams.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Repository Structure](#-repository-structure)
- [Tech Stack & Dependencies](#-tech-stack--dependencies)
- [Installation](#-installation)
- [Usage](#-usage)
- [Known Issues](#-known-issues)
- [Project Documentation](#-project-documentation)

---

## ✨ Features

- **🗺️ Repository Navigation**: Automatically identifies entry points, core modules, and architecture patterns
- **🔍 Code Analysis**: Extracts key functions, classes, API endpoints, and data models
- **📚 Smart Onboarding**: Generates personalized learning paths based on repository complexity
- **📊 Architecture Diagrams**: Creates visual representations in Mermaid, Graphviz, and ASCII formats
- **💬 Interactive Chat**: Ask questions about the codebase with context-aware responses
- **📥 Export Capabilities**: Download diagrams and documentation in multiple formats

---

## 🏗️ Architecture

GitBro uses a **multi-agent architecture** powered by LangGraph, where 5 specialized AI agents work sequentially to analyze repositories:

```
Navigator Agent → Context Agent → Mentor Agent → Visualizer Agent → Orchestrator Agent
```

### Agent Responsibilities

1. **Navigator Agent**: Maps repository structure, identifies entry points and core modules
2. **Context Agent**: Analyzes code samples, extracts patterns and key components
3. **Mentor Agent**: Creates learning paths and onboarding recommendations
4. **Visualizer Agent**: Generates architecture diagrams in multiple formats
5. **Orchestrator Agent**: Synthesizes all agent outputs into a final report

---

## 📁 Repository Structure

```
GitBro/
├── app.py                      # Streamlit web UI with chat interface
├── main.py                     # CLI interface for repository analysis
├── requirements.txt            # Python dependencies
├── test_diagrams.py           # Diagram generation test script
│
├── src/                        # Core source code
│   ├── __init__.py
│   ├── github_client.py       # GitHub API client & repository operations
│   ├── graph.py               # LangGraph workflow orchestration
│   ├── state.py               # Shared state definition for agents
│   ├── utils.py               # Utility functions (JSON parsing, etc.)
│   ├── diagram_generator.py   # Multi-format diagram generator
│   │
│   └── agents/                # AI agent implementations
│       ├── navigator_agent.py      # Repository structure mapping
│       ├── context_agent.py        # Code analysis & pattern extraction
│       ├── mentor_agent.py         # Learning path generation
│       ├── visualizer_agent.py     # Architecture diagram creation
│       └── orchestrator_agent.py   # Final report synthesis
│
├── docs/                       # Documentation
│   └── VISUALIZATION.md       # Visualization features guide
│
├── diagrams/                   # Generated architecture diagrams
│   ├── *.mmd                  # Mermaid flowcharts
│   ├── *.dot                  # Graphviz DOT files
│   ├── *.txt                  # ASCII text diagrams
│   └── *.png                  # Exported PNG images
│
└── repo/                       # Sample repository for testing
    └── Oscars-Database-Client/
```

---

## 🛠️ Tech Stack & Dependencies

### Core Framework

| Technology | Version | Justification |
|-----------|---------|---------------|
| **LangGraph** | ≥1.0.0 | Orchestrates sequential agent workflow with state management. Provides graph-based agent coordination superior to simple chains. |
| **LangChain Core** | ≥1.2.0 | Foundation for LLM interactions, prompt management, and agent abstractions. Industry standard for building LLM applications. |
| **LangChain OpenAI** | ≥0.1.0 | OpenAI API integration for GPT-4 models. Provides reliable, high-quality language model responses. |

### User Interface

| Technology | Version | Justification |
|-----------|---------|---------------|
| **Streamlit** | ≥1.31.0 | Rapid web UI development with minimal boilerplate. Perfect for data science and AI applications with built-in chat components. |
| **streamlit-mermaid** | Latest | Native Mermaid diagram rendering in Streamlit. Enables interactive architecture visualization. |

### Diagram Generation

| Technology | Version | Justification |
|-----------|---------|---------------|
| **Graphviz** | ≥0.20.0 | Industry-standard graph visualization toolkit. Generates professional diagrams with customizable layouts. |
| **pydot** | ≥1.4.2 | Python interface to Graphviz. Allows programmatic DOT graph creation and PNG export. |
| **Matplotlib** | ≥3.7.0 | Flexible plotting library for potential future visualization enhancements. |

### API & Data Processing

| Technology | Version | Justification |
|-----------|---------|---------------|
| **Requests** | ≥2.31.0 | Simple, elegant HTTP library for GitHub API calls. More intuitive than urllib. |
| **Pydantic** | ≥2.7.4 | Data validation and settings management. Ensures type safety for agent state and API responses. |

### Document Processing

| Technology | Version | Justification |
|-----------|---------|---------------|
| **Markdown** | Latest | Parse and process README files and documentation. |
| **WeasyPrint** | Latest | HTML to PDF conversion for potential report exports. |
| **pypdf** | Latest | PDF manipulation for document generation. |
| **python-docx** | Latest | DOCX file creation for Word document exports. |

### Utilities

| Technology | Version | Justification |
|-----------|---------|---------------|
| **Pillow** | ≥10.0.0 | Image processing library for diagram manipulation. |
| **pytesseract** | Latest | OCR capabilities for potential future image-to-text features. |
| **python-dotenv** | ≥1.0.0 | Environment variable management for API keys and configuration. |

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key (or compatible API endpoint)
- Graphviz (optional, for PNG diagram export)

### Install Graphviz (Optional)

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**Windows:**
Download from [graphviz.org](https://graphviz.org/download/)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/GitBro.git
   cd GitBro
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials:**
   
   Edit the API key in `app.py` and `src/agents/visualizer_agent.py`:
   ```python
   os.environ["OPENAI_API_KEY"] = "your-api-key-here"
   os.environ["OPENAI_BASE_URL"] = "your-api-endpoint"  # Optional
   ```

---

## 💻 Usage

### Web Interface (Recommended)

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Then:
1. Enter a GitHub repository URL (e.g., `https://github.com/owner/repo`)
2. Click **Analyze Repository**
3. Wait for the 5-agent analysis to complete
4. Explore the results and chat with GitBro about the codebase

### Command Line Interface

Analyze a repository from the terminal:

```bash
python3 main.py https://github.com/owner/repo
```

Output includes:
- Repository metadata and statistics
- Navigator map with entry points and core modules
- Context analysis with key functions and classes
- Mentor onboarding guide
- Architecture diagram (Mermaid format)
- Agent execution log

### Test Diagram Generation

Test the diagram generator independently:

```bash
python3 test_diagrams.py
```

This generates sample diagrams in all formats (Mermaid, Graphviz, ASCII) and saves them to the `diagrams/` directory.

---

## 🐛 Known Issues

### ~~Visualizer Rendering Bug~~ ✅ **FIXED**

**Status**: Resolved in latest version

**Previous Issue**: The visualizer agent was generating Mermaid diagrams that failed to render in the Streamlit UI due to:
- Inconsistent LLM outputs for diagram syntax
- Missing validation for Mermaid code blocks
- No fallback mechanisms for rendering failures

**Solution Implemented**:
- Created dedicated `DiagramGenerator` class ([src/diagram_generator.py](src/diagram_generator.py))
- Added programmatic diagram generation (no LLM involved)
- Implemented multi-format support: Mermaid, Graphviz DOT, ASCII, and PNG
- Added syntax validation for Mermaid diagrams
- Implemented automatic fallback: Mermaid → Graphviz → ASCII
- Enhanced UI with tabbed diagram viewer and download options

**Current Behavior**:
- ✅ Diagrams now reliably render in all supported formats
- ✅ Users can switch between Mermaid, Graphviz, ASCII, and PNG views
- ✅ All diagrams are exportable to files
- ✅ Graceful degradation if dependencies missing

See [docs/VISUALIZATION.md](docs/VISUALIZATION.md) for detailed visualization documentation.

---

## 📖 Project Documentation

### How It Works

1. **Repository Cloning**: GitBro clones the target repository locally for file access
2. **Data Collection**: Extracts file tree, source code, README, config files, commits, and PRs
3. **Agent Pipeline**: Five specialized agents analyze the data sequentially
4. **State Management**: LangGraph maintains shared state across all agents
5. **Report Generation**: Final report synthesizes all agent outputs
6. **Interactive Chat**: Users can ask follow-up questions with full repository context

### Agent Pipeline Details

```python
# Graph flow defined in src/graph.py
workflow.set_entry_point("navigator")
workflow.add_edge("navigator", "context")
workflow.add_edge("context", "mentor")
workflow.add_edge("mentor", "visualizer")
workflow.add_edge("visualizer", "orchestrator")
workflow.add_edge("orchestrator", END)
```

Each agent:
- Receives the current state (TypedDict)
- Performs its specialized analysis
- Updates state with its findings
- Passes control to the next agent

### Key Design Decisions

1. **Sequential vs Parallel Agents**: Sequential chosen for logical dependencies (navigator must run before context agent)
2. **LangGraph vs LangChain Chains**: LangGraph provides better state management and visualization
3. **Local Cloning vs API-Only**: Local cloning enables full file access for comprehensive analysis
4. **Multi-Format Diagrams**: Ensures compatibility across different rendering environments
5. **Streamlit UI**: Rapid prototyping with built-in chat components and minimal frontend code

---

## 🎓 Project Presentation

**Presentation Slides**: 

<!-- Add your slide link here -->
[Link to Presentation Slides](ADD_YOUR_LINK_HERE)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **LangChain Team** for the excellent LLM framework
- **LangGraph** for agent orchestration capabilities
- **Streamlit** for the intuitive UI framework
- **OpenAI** for GPT-4 model access
- **Graphviz** and **Mermaid** for visualization tools

---

## 📞 Contact

For questions, issues, or suggestions, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ using LangGraph, OpenAI, and Streamlit**