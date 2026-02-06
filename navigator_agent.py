"""
Navigator Agent - Repository Structure Analysis
Responsible for understanding and documenting GitHub repository structure
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import operator


class NavigatorState(TypedDict):
    """State for the Navigator Agent"""
    repo_url: str
    repo_owner: str
    repo_name: str
    messages: Annotated[List, operator.add]
    directory_structure: Dict[str, Any]
    key_files: Dict[str, str]
    dependencies: Dict[str, List[str]]
    tech_stack: List[str]
    architecture_insights: Dict[str, Any]
    entry_points: List[str]
    final_report: str


class NavigatorAgent:
    """
    Navigator Agent for analyzing GitHub repository structure.
    Uses LangGraph to orchestrate the analysis workflow.
    """
    
    def __init__(self, github_token: str, groq_api_key: str):
        self.github_token = github_token
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_api_key,
            temperature=0
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for repository analysis"""
        workflow = StateGraph(NavigatorState)
        
        # Add nodes for each analysis step
        workflow.add_node("fetch_structure", self.fetch_directory_structure)
        workflow.add_node("identify_key_files", self.identify_key_files)
        workflow.add_node("analyze_dependencies", self.analyze_dependencies)
        workflow.add_node("detect_tech_stack", self.detect_tech_stack)
        workflow.add_node("analyze_architecture", self.analyze_architecture)
        workflow.add_node("find_entry_points", self.find_entry_points)
        workflow.add_node("generate_report", self.generate_report)
        
        # Define the workflow
        workflow.set_entry_point("fetch_structure")
        workflow.add_edge("fetch_structure", "identify_key_files")
        workflow.add_edge("identify_key_files", "analyze_dependencies")
        workflow.add_edge("analyze_dependencies", "detect_tech_stack")
        workflow.add_edge("detect_tech_stack", "analyze_architecture")
        workflow.add_edge("analyze_architecture", "find_entry_points")
        workflow.add_edge("find_entry_points", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
    
    def fetch_directory_structure(self, state: NavigatorState) -> NavigatorState:
        """Fetch and analyze the directory structure from GitHub"""
        from github_tools import GitHubClient
        
        client = GitHubClient(self.github_token)
        structure = client.get_repo_structure(state["repo_owner"], state["repo_name"])
        
        state["directory_structure"] = structure
        state["messages"].append(
            HumanMessage(content=f"Fetched directory structure with {len(structure.get('files', []))} files")
        )
        return state
    
    def identify_key_files(self, state: NavigatorState) -> NavigatorState:
        """Identify and extract key files (README, docs, configs)"""
        from github_tools import GitHubClient
        
        client = GitHubClient(self.github_token)
        key_files = client.get_key_files(state["repo_owner"], state["repo_name"])
        
        state["key_files"] = key_files
        state["messages"].append(
            HumanMessage(content=f"Identified {len(key_files)} key files")
        )
        return state
    
    def analyze_dependencies(self, state: NavigatorState) -> NavigatorState:
        """Analyze code dependencies and imports"""
        from dependency_analyzer import DependencyAnalyzer
        
        analyzer = DependencyAnalyzer(self.github_token)
        dependencies = analyzer.analyze(
            state["repo_owner"],
            state["repo_name"],
            state["directory_structure"]
        )
        
        state["dependencies"] = dependencies
        state["messages"].append(
            HumanMessage(content=f"Analyzed dependencies across {len(dependencies)} files")
        )
        return state
    
    def detect_tech_stack(self, state: NavigatorState) -> NavigatorState:
        """Detect the technology stack used in the repository"""
        from tech_stack_detector import TechStackDetector
        
        detector = TechStackDetector()
        tech_stack = detector.detect(
            state["directory_structure"],
            state["key_files"],
            state["dependencies"]
        )
        
        state["tech_stack"] = tech_stack
        state["messages"].append(
            HumanMessage(content=f"Detected tech stack: {', '.join(tech_stack[:5])}")
        )
        return state
    
    def analyze_architecture(self, state: NavigatorState) -> NavigatorState:
        """Analyze architecture patterns and code organization"""
        # Use LLM to analyze architecture patterns
        system_prompt = """You are an expert software architect. Analyze the repository structure 
        and identify architectural patterns, code organization principles, and design patterns used."""
        
        analysis_prompt = f"""
        Repository: {state['repo_name']}
        
        Directory Structure:
        {self._format_structure(state['directory_structure'])}
        
        Technology Stack: {', '.join(state['tech_stack'])}
        
        Identify:
        1. Architectural patterns (MVC, microservices, monolith, etc.)
        2. Code organization principles
        3. Design patterns observed
        4. Module/component structure
        """
        
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=analysis_prompt)
        ])
        
        state["architecture_insights"] = {
            "analysis": response.content,
            "patterns": self._extract_patterns(response.content)
        }
        state["messages"].append(
            HumanMessage(content="Analyzed architecture patterns")
        )
        return state
    
    def find_entry_points(self, state: NavigatorState) -> NavigatorState:
        """Find main entry points and key modules"""
        from entry_point_finder import EntryPointFinder
        
        finder = EntryPointFinder()
        entry_points = finder.find(
            state["directory_structure"],
            state["tech_stack"],
            state["key_files"]
        )
        
        state["entry_points"] = entry_points
        state["messages"].append(
            HumanMessage(content=f"Found {len(entry_points)} entry points")
        )
        return state
    
    def generate_report(self, state: NavigatorState) -> NavigatorState:
        """Generate a comprehensive structured report"""
        system_prompt = """You are a technical documentation expert. Create a comprehensive, 
        well-structured onboarding report for new developers joining this project."""
        
        report_prompt = f"""
        Generate a detailed onboarding report for repository: {state['repo_name']}
        
        Include the following information:
        
        ## Repository Overview
        - Purpose and description
        - Technology Stack: {', '.join(state['tech_stack'])}
        
        ## Project Structure
        {self._format_structure(state['directory_structure'])}
        
        ## Key Files
        {self._format_key_files(state['key_files'])}
        
        ## Architecture
        {state['architecture_insights'].get('analysis', 'N/A')}
        
        ## Entry Points
        {', '.join(state['entry_points'])}
        
        ## Dependencies
        {self._format_dependencies(state['dependencies'])}
        
        Create a clear, actionable report that helps new developers understand the codebase quickly.
        """
        
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=report_prompt)
        ])
        
        state["final_report"] = response.content
        state["messages"].append(
            HumanMessage(content="Generated final onboarding report")
        )
        return state
    
    def _format_structure(self, structure: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
        """Format directory structure as a tree for display"""
        lines = []
        
        # Add files
        files = structure.get("files", [])
        directories = structure.get("directories", [])
        
        for i, file_info in enumerate(files):
            is_last_file = (i == len(files) - 1) and len(directories) == 0
            connector = "└── " if is_last_file else "├── "
            lines.append(f"{prefix}{connector}{file_info['name']}")
        
        # Add directories recursively
        for i, dir_info in enumerate(directories):
            is_last_dir = (i == len(directories) - 1)
            connector = "└── " if is_last_dir else "├── "
            lines.append(f"{prefix}{connector}{dir_info['name']}/")
            
            # Recursively format subdirectory
            extension = "    " if is_last_dir else "│   "
            subdir_content = self._format_structure(
                dir_info.get("contents", {}), 
                prefix + extension, 
                is_last_dir
            )
            if subdir_content:
                lines.append(subdir_content)
        
        return "\n".join(lines)
    
    def _format_key_files(self, key_files: Dict[str, str]) -> str:
        """Format key files for display"""
        return "\n".join([f"- {name}: {content[:100]}..." for name, content in key_files.items()])
    
    def _format_dependencies(self, dependencies: Dict[str, List[str]]) -> str:
        """Format dependencies for display"""
        return "\n".join([f"- {file}: {len(deps)} dependencies" for file, deps in dependencies.items()])
    
    def _extract_patterns(self, analysis: str) -> List[str]:
        """Extract architectural patterns from LLM analysis"""
        # Simple pattern extraction - can be enhanced with more sophisticated parsing
        patterns = []
        common_patterns = ["MVC", "MVVM", "microservices", "monolith", "layered", "hexagonal"]
        for pattern in common_patterns:
            if pattern.lower() in analysis.lower():
                patterns.append(pattern)
        return patterns
    
    def analyze_repository(self, repo_url: str) -> str:
        """
        Main entry point to analyze a repository
        
        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
            
        Returns:
            Structured onboarding report
        """
        # Parse repo URL
        parts = repo_url.rstrip('/').split('/')
        repo_owner = parts[-2]
        repo_name = parts[-1]
        
        # Initialize state
        initial_state = NavigatorState(
            repo_url=repo_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            messages=[],
            directory_structure={},
            key_files={},
            dependencies={},
            tech_stack=[],
            architecture_insights={},
            entry_points=[],
            final_report=""
        )
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state["final_report"]


if __name__ == "__main__":
    import os
    
    # Example usage
    navigator = NavigatorAgent(
        github_token=os.getenv("GITHUB_TOKEN"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    report = navigator.analyze_repository("https://github.com/example/repo")
    print(report)
