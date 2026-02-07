# GitBro 🤖

**AI-Powered GitHub Repository Analysis & Onboarding Assistant**

Multi-agent system that analyzes GitHub repositories using LangGraph and specialized AI agents to map structure, analyze code, create learning paths, and generate architecture diagrams.

## ✨ Features

- 🗺️ **Repository Navigation** - Identifies entry points, core modules, and architecture patterns
- 🔍 **Code Analysis** - Extracts key functions, classes, APIs, and data models
- 📚 **Smart Onboarding** - Generates personalized learning paths
- 📊 **Architecture Diagrams** - Mermaid, Graphviz, and ASCII visualizations
- 💬 **Interactive Chat** - Context-aware Q&A about the codebase

## 🏗️ Architecture

**5-Agent Pipeline**: Navigator → Context → Mentor → Visualizer → Orchestrator

1. **Navigator** - Maps structure and entry points
2. **Context** - Analyzes code patterns
3. **Mentor** - Creates onboarding guides
4. **Visualizer** - Generates diagrams
5. **Orchestrator** - Synthesizes final report

---

## 📁 Repository Structure

```
GitBro/
├── app.py                  # Streamlit web UI
├── main.py                 # CLI interface
├── requirements.txt        # Dependencies
└── src/
    ├── github_client.py   # GitHub API client
    ├── graph.py           # LangGraph workflow
    ├── state.py           # Agent state management
    └── agents/            # 5 AI agents
```

## 🛠️ Tech Stack

- **LangGraph** - Agent orchestration and workflow
- **LangChain** - LLM interactions and abstractions
- **OpenAI GPT-4** - Language model
- **Streamlit** - Web UI with chat interface
- **Pydantic** - Data validation
- **Graphviz/Mermaid** - Diagram generation

## 🚀 How to Run

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure API Key**
```

**3. Run the Application**

**Web Interface (Recommended):**
```bash
streamlit run app.py
```
Then enter a GitHub repo URL and click "Analyze Repository"
```

---

## 🐛 Known Issues

**Visualizer Rendering Bug**

Previous issue with Mermaid diagram rendering resolved by implementing:
- Programmatic diagram generation (no LLM dependency)
- Multi-format support (Mermaid/Graphviz/ASCII)
- Automatic fallback mechanisms

---

## 🎓 Project Presentation

[**View Presentation Slides →**](https://www.canva.com/design/DAHAkLHJGRw/9Q79sGUtyMSJOZXVGh1Mew/edit?utm_content=DAHAkLHJGRw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

---

