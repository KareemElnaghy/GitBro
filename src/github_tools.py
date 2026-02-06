"""
GitHub API integration tools for the Navigator Agent
"""

import requests
from typing import Dict, List, Any, Optional
import base64


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_repo_structure(self, owner: str, repo: str, path: str = "") -> Dict[str, Any]:
        """
        Recursively fetch the complete directory structure
        
        Returns:
            Dictionary containing files, directories, and their metadata
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        contents = response.json()
        structure = {
            "path": path,
            "files": [],
            "directories": []
        }
        
        for item in contents:
            if item["type"] == "file":
                structure["files"].append({
                    "name": item["name"],
                    "path": item["path"],
                    "size": item["size"],
                    "url": item["url"]
                })
            elif item["type"] == "dir":
                # Recursively get subdirectory structure
                try:
                    print(f"Fetching directory: {item['path']}")
                    subdir = self.get_repo_structure(owner, repo, item["path"])
                    structure["directories"].append({
                        "name": item["name"],
                        "path": item["path"],
                        "contents": subdir
                    })
                except Exception as e:
                    print(f"Error accessing {item['path']}: {e}")
        
        return structure
    
    def get_file_content(self, owner: str, repo: str, file_path: str) -> str:
        """Fetch the content of a specific file"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Decode base64 content
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
    
    def get_key_files(self, owner: str, repo: str) -> Dict[str, str]:
        """
        Identify and fetch key files (README, docs, config files)
        
        Returns:
            Dictionary mapping file names to their contents
        """
        key_file_patterns = [
            "README.md", "README.rst", "README.txt", "README",
            "CONTRIBUTING.md", "LICENSE", "LICENSE.md",
            "package.json", "requirements.txt", "Pipfile", "pyproject.toml",
            "setup.py", "setup.cfg", "Cargo.toml", "go.mod",
            "pom.xml", "build.gradle", "Gemfile",
            ".gitignore", "Dockerfile", "docker-compose.yml",
            "Makefile", "CMakeLists.txt",
            "tsconfig.json", "webpack.config.js", "vite.config.js"
        ]
        
        key_files = {}
        
        # Get root directory contents
        root_structure = self.get_repo_structure(owner, repo)
        
        for file_info in root_structure.get("files", []):
            if file_info["name"] in key_file_patterns:
                try:
                    content = self.get_file_content(owner, repo, file_info["path"])
                    key_files[file_info["name"]] = content
                except Exception as e:
                    print(f"Error fetching {file_info['name']}: {e}")
        
        # Also check common documentation directories
        doc_dirs = ["docs", "documentation", ".github"]
        for doc_dir in doc_dirs:
            try:
                doc_structure = self.get_repo_structure(owner, repo, doc_dir)
                for file_info in doc_structure.get("files", []):
                    if file_info["name"].endswith((".md", ".rst", ".txt")):
                        try:
                            content = self.get_file_content(owner, repo, file_info["path"])
                            key_files[f"{doc_dir}/{file_info['name']}"] = content
                        except Exception as e:
                            print(f"Error fetching {file_info['path']}: {e}")
            except Exception:
                # Directory doesn't exist, continue
                pass
        
        return key_files
    
    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get programming languages used in the repository"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/languages"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_repo_topics(self, owner: str, repo: str) -> List[str]:
        """Get repository topics/tags"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/topics"
        headers = {**self.headers, "Accept": "application/vnd.github.mercy-preview+json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("names", [])
    
    def search_files(self, owner: str, repo: str, query: str) -> List[Dict[str, Any]]:
        """Search for files in the repository"""
        url = f"{self.BASE_URL}/search/code"
        params = {
            "q": f"{query} repo:{owner}/{repo}"
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
