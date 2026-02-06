"""GitHub API client for fetching repository data without cloning."""
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    """Client for GitHub API v3 and raw content access."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
    
    def parse_repo_url(self, url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL."""
        # Handle: https://github.com/owner/repo or github.com/owner/repo
        url = url.replace("https://", "").replace("http://", "")
        parts = url.split("github.com/")[-1].strip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        return parts[0], parts[1]
    
    def get_repo_metadata(self, owner: str, repo: str) -> Dict:
        """Fetch repository metadata (stars, language, description)."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description", "No description"),
            "language": data.get("language", "Unknown"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "homepage": data.get("homepage"),
            "topics": data.get("topics", []),
            "default_branch": data.get("default_branch", "main")
        }
    
    def get_file_tree(self, owner: str, repo: str, branch: str = None, max_files: int = None) -> List[Dict]:
        """
        Fetch repository file tree via Git Trees API.
        Returns list of {path, type, size} dicts.
        Set max_files to limit results (useful for large repos).
        """
        if branch is None:
            metadata = self.get_repo_metadata(owner, repo)
            branch = metadata["default_branch"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        
        tree_data = response.json()
        files = []
        
        items = tree_data.get("tree", [])
        if max_files:
            items = items[:max_files]
        
        for item in items:
            files.append({
                "path": item.get("path"),
                "type": item.get("type"),
                "size": item.get("size", 0),
                "sha": item.get("sha")
            })
        
        return files
    
    def get_raw_content(self, owner: str, repo: str, file_path: str, branch: str = "main") -> str:
        """
        Fetch raw file content from raw.githubusercontent.com.
        Limits to 200 lines to prevent token overflow.
        """
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        lines = content.split("\n")
        
        # Limit to 200 lines
        if len(lines) > 200:
            lines = lines[:200]
            content = "\n".join(lines) + "\n... [truncated]"
        
        return content
    
    def identify_source_files(self, file_tree: List[Dict]) -> List[str]:
        """
        Identify top 10 source files from file tree.
        Prioritizes: main.py, app.py, index.js, then .py/.js/.ts files.
        """
        priority_files = []
        source_files = []
        
        # Extensions to consider
        source_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".cpp", ".c"]
        
        for item in file_tree:
            if item["type"] != "blob":
                continue
            
            path = item["path"]
            
            # Priority files (entry points)
            if path in ["main.py", "app.py", "index.js", "index.ts", "main.go", "main.rs"]:
                priority_files.append(path)
            # Regular source files
            elif any(path.endswith(ext) for ext in source_extensions):
                # Skip test files and config files
                if "test" not in path.lower() and "config" not in path.lower():
                    source_files.append(path)
        
        # Return top 10: priority first, then others
        selected = priority_files + source_files
        return selected[:10]
    
    def fetch_top_files(self, owner: str, repo: str, branch: str = None, max_files: int = 10) -> Dict[str, str]:
        """
        Fetch content of top source files.
        Returns {filename: content} dict.
        """
        if branch is None:
            metadata = self.get_repo_metadata(owner, repo)
            branch = metadata["default_branch"]
        
        file_tree = self.get_file_tree(owner, repo, branch)
        source_files = self.identify_source_files(file_tree)[:max_files]
        
        code_samples = {}
        for file_path in source_files:
            try:
                content = self.get_raw_content(owner, repo, file_path, branch)
                code_samples[file_path] = content
            except Exception as e:
                code_samples[file_path] = f"[Error fetching file: {e}]"
        
        return code_samples
