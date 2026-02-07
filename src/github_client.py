"""GitHub client: clones repos locally for file reading, uses API for metadata/commits/PRs."""
import os
import subprocess
import tempfile
import shutil
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract

load_dotenv()

# Config/dependency files to read when present
CONFIG_FILE_NAMES = {
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile",
    "package.json", "tsconfig.json",
    "go.mod", "Cargo.toml", "Gemfile", "pom.xml", "build.gradle",
    "Makefile", "CMakeLists.txt", "Dockerfile", "docker-compose.yml",
    "docker-compose.yaml", ".env.example", "tox.ini", "pytest.ini",
}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".cs", ".rb", ".php", ".swift", ".kt",
}

# Document/image extensions we can parse
DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".doc",  # Documents
    ".png", ".jpg", ".jpeg", ".gif", ".bmp",  # Images with text
}

# Directories to skip when walking the local clone
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".egg-info", ".tox", ".mypy_cache", ".pytest_cache",
    ".next", ".nuxt", "vendor", "target", ".idea", ".vscode",
}

# Binary extensions to skip when reading file content (removed parseable docs/images)
BINARY_EXTENSIONS = {
    ".ico", ".svg",  # Kept some image formats
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib", ".class", ".jar",
    ".pyc", ".pyo", ".whl", ".egg",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".ttf", ".woff", ".woff2", ".eot",
    ".sqlite", ".db",
}


class GitHubClient:
    """Clones repos locally for file access. Uses GitHub API for metadata, commits, PRs."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = "https://api.github.com"

    # ---- URL parsing ----

    def parse_repo_url(self, url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL."""
        url = url.replace("https://", "").replace("http://", "")
        parts = url.split("github.com/")[-1].strip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        return parts[0], parts[1]

    # ---- GitHub API methods (metadata, commits, PRs) ----

    def get_repo_metadata(self, owner: str, repo: str) -> Dict:
        """Fetch repository metadata via GitHub API."""
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
            "default_branch": data.get("default_branch", "main"),
        }

    def get_recent_commits(self, owner: str, repo: str, max_commits: int = 15) -> List[Dict]:
        """Fetch recent commits via GitHub API."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": max_commits}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            commits = []
            for c in response.json():
                commits.append({
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"].split("\n")[0][:120],
                    "author": c["commit"]["author"]["name"],
                    "date": c["commit"]["author"]["date"][:10],
                })
            return commits
        except Exception:
            return []

    def get_pull_requests(self, owner: str, repo: str, max_prs: int = 10) -> List[Dict]:
        """Fetch recent pull requests via GitHub API."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": "all", "per_page": max_prs, "sort": "updated", "direction": "desc"}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            prs = []
            for pr in response.json():
                prs.append({
                    "number": pr["number"],
                    "title": pr["title"][:120],
                    "state": pr["state"],
                    "author": pr["user"]["login"],
                    "created": pr["created_at"][:10],
                    "labels": [l["name"] for l in pr.get("labels", [])],
                })
            return prs
        except Exception:
            return []

    # ---- Local clone operations ----

    def clone_repo(self, repo_url: str) -> str:
        """Shallow clone a repo into a temp directory. Returns the directory path."""
        temp_dir = tempfile.mkdtemp(prefix="gitbro_")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"git clone failed: {result.stderr.strip()}")
        return temp_dir

    def cleanup_clone(self, repo_dir: str):
        """Remove the cloned repo directory."""
        if repo_dir and os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, ignore_errors=True)

    def walk_local_repo(self, repo_dir: str) -> List[Dict]:
        """Walk a local repo directory and return file tree (same format agents expect)."""
        file_tree = []
        for root, dirs, files in os.walk(repo_dir):
            # Skip ignored directories in-place so os.walk doesn't descend
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))

            for filename in sorted(files):
                if filename.startswith("."):
                    continue

                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, repo_dir).replace(os.sep, "/")

                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0

                file_tree.append({
                    "path": rel_path,
                    "type": "blob",
                    "size": size,
                })

        return file_tree

    def read_local_file(self, repo_dir: str, file_path: str, max_lines: int = 500) -> Optional[str]:
        """Read a text file from the local clone. Returns None if unreadable."""
        full_path = os.path.join(repo_dir, file_path)
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"\n... [truncated at {max_lines} lines]")
                        break
                    lines.append(line)
                return "".join(lines)
        except (OSError, UnicodeDecodeError):
            return None

    def extract_pdf_text(self, repo_dir: str, file_path: str, max_pages: int = 20) -> Optional[str]:
        """Extract text from a PDF file."""
        full_path = os.path.join(repo_dir, file_path)
        try:
            reader = PdfReader(full_path)
            text_parts = []
            num_pages = min(len(reader.pages), max_pages)
            
            for i in range(num_pages):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {i+1} ---\n{text}\n")
            
            if len(reader.pages) > max_pages:
                text_parts.append(f"\n... [truncated: {len(reader.pages) - max_pages} more pages]")
            
            return "".join(text_parts) if text_parts else None
        except Exception as e:
            print(f"Error extracting PDF {file_path}: {e}")
            return None

    def extract_docx_text(self, repo_dir: str, file_path: str) -> Optional[str]:
        """Extract text from a Word document (.docx)."""
        full_path = os.path.join(repo_dir, file_path)
        try:
            doc = Document(full_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs) if paragraphs else None
        except Exception as e:
            print(f"Error extracting DOCX {file_path}: {e}")
            return None

    def extract_image_text(self, repo_dir: str, file_path: str) -> Optional[str]:
        """Extract text from an image using OCR."""
        full_path = os.path.join(repo_dir, file_path)
        try:
            image = Image.open(full_path)
            text = pytesseract.image_to_string(image)
            return text.strip() if text.strip() else None
        except Exception as e:
            print(f"Error extracting text from image {file_path}: {e}")
            return None

    def read_document_file(self, repo_dir: str, file_path: str) -> Optional[str]:
        """Read a document file (PDF, DOCX, or image) and extract its text content."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return self.extract_pdf_text(repo_dir, file_path)
        elif ext in {".docx", ".doc"}:
            return self.extract_docx_text(repo_dir, file_path)
        elif ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
            return self.extract_image_text(repo_dir, file_path)
        
        return None

    def read_all_source_files(self, repo_dir: str, file_tree: List[Dict], max_lines: int = 500) -> Dict[str, str]:
        """Read all source code files and documents from the local clone."""
        code_samples = {}

        for item in file_tree:
            path = item["path"]
            ext = os.path.splitext(path)[1].lower()

            # Skip binary files we can't parse
            if ext in BINARY_EXTENSIONS:
                continue

            # Skip very large files (likely generated/minified)
            if item.get("size", 0) > 200_000:
                continue

            # Read source code files
            if ext in SOURCE_EXTENSIONS:
                content = self.read_local_file(repo_dir, path, max_lines)
                if content:
                    code_samples[path] = content
            
            # Read document files (PDFs, Word docs, images)
            elif ext in DOCUMENT_EXTENSIONS:
                content = self.read_document_file(repo_dir, path)
                if content:
                    code_samples[path] = content

        return code_samples

    def read_local_config_files(self, repo_dir: str, file_tree: List[Dict]) -> Dict[str, str]:
        """Read config/dependency files from the local clone."""
        config_files = {}

        for item in file_tree:
            filename = item["path"].split("/")[-1]
            if filename in CONFIG_FILE_NAMES:
                content = self.read_local_file(repo_dir, item["path"], max_lines=150)
                if content:
                    config_files[item["path"]] = content

        return config_files

    def read_local_readme(self, repo_dir: str) -> Optional[str]:
        """Read the README file from the local clone."""
        for name in ["README.md", "README.rst", "README.txt", "README"]:
            content = self.read_local_file(repo_dir, name, max_lines=500)
            if content:
                return content
        return None
