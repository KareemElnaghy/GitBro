"""
Entry point detection module
"""

from typing import Dict, List, Any, Set


class EntryPointFinder:
    """Finds main entry points and key modules in a repository"""
    
    # Common entry point file names by technology
    ENTRY_POINT_PATTERNS = {
        # Python
        'main.py': 'Python main entry point',
        'app.py': 'Python application entry',
        'run.py': 'Python runner',
        'manage.py': 'Django management script',
        '__main__.py': 'Python package entry',
        'wsgi.py': 'WSGI application',
        'asgi.py': 'ASGI application',
        
        # JavaScript/Node.js
        'index.js': 'JavaScript main entry',
        'main.js': 'JavaScript main entry',
        'app.js': 'Application entry',
        'server.js': 'Server entry point',
        
        # TypeScript
        'index.ts': 'TypeScript main entry',
        'main.ts': 'TypeScript main entry',
        'server.ts': 'Server entry point',
        
        # React/Next.js
        'pages/index.tsx': 'Next.js home page',
        'pages/index.jsx': 'Next.js home page',
        'src/index.js': 'React entry point',
        'src/index.tsx': 'React entry point',
        'src/App.tsx': 'React App component',
        'src/App.jsx': 'React App component',
        
        # Java
        'Main.java': 'Java main class',
        'Application.java': 'Java application class',
        
        # Go
        'main.go': 'Go main package',
        'cmd/main.go': 'Go CLI entry',
        
        # Rust
        'src/main.rs': 'Rust main entry',
        'src/lib.rs': 'Rust library entry',
        
        # Ruby
        'application.rb': 'Ruby application',
        'config.ru': 'Rack configuration',
        
        # PHP
        'index.php': 'PHP entry point',
        'public/index.php': 'Laravel/Symfony entry',
        
        # Others
        'Makefile': 'Build entry point',
        'CMakeLists.txt': 'CMake build',
    }
    
    def find(
        self,
        directory_structure: Dict[str, Any],
        tech_stack: List[str],
        key_files: Dict[str, str]
    ) -> List[str]:
        """
        Find entry points in the repository
        
        Returns:
            List of entry point file paths with descriptions
        """
        entry_points = []
        
        # Step 1: Look for known entry point patterns
        all_files = self._get_all_files(directory_structure)
        
        for file_path in all_files:
            for pattern, description in self.ENTRY_POINT_PATTERNS.items():
                if file_path.endswith(pattern) or file_path == pattern:
                    entry_points.append(f"{file_path} - {description}")
        
        # Step 2: Check package.json for entry points
        if "package.json" in key_files:
            package_entries = self._find_npm_entry_points(key_files["package.json"])
            entry_points.extend(package_entries)
        
        # Step 3: Check setup.py for Python entry points
        if "setup.py" in key_files:
            python_entries = self._find_python_entry_points(key_files["setup.py"])
            entry_points.extend(python_entries)
        
        # Step 4: Look for files with main functions
        # This would require analyzing file contents - simplified here
        
        # Step 5: Detect based on tech stack
        tech_based_entries = self._infer_from_tech_stack(tech_stack, all_files)
        entry_points.extend(tech_based_entries)
        
        # Remove duplicates
        entry_points = list(set(entry_points))
        
        return entry_points if entry_points else ["No clear entry points detected"]
    
    def _get_all_files(self, structure: Dict[str, Any], prefix: str = "") -> List[str]:
        """Recursively get all file paths"""
        files = []
        
        for file_info in structure.get("files", []):
            file_path = f"{prefix}/{file_info['name']}" if prefix else file_info['name']
            files.append(file_path)
        
        for dir_info in structure.get("directories", []):
            dir_path = f"{prefix}/{dir_info['name']}" if prefix else dir_info['name']
            files.extend(self._get_all_files(dir_info.get("contents", {}), dir_path))
        
        return files
    
    def _find_npm_entry_points(self, package_json_content: str) -> List[str]:
        """Find entry points from package.json"""
        import json
        
        entry_points = []
        
        try:
            data = json.loads(package_json_content)
            
            # Check main field
            if "main" in data:
                entry_points.append(f"{data['main']} - npm main entry")
            
            # Check module field (ES modules)
            if "module" in data:
                entry_points.append(f"{data['module']} - ES module entry")
            
            # Check scripts
            if "scripts" in data:
                scripts = data["scripts"]
                if "start" in scripts:
                    entry_points.append(f"npm start - {scripts['start']}")
                if "dev" in scripts:
                    entry_points.append(f"npm run dev - {scripts['dev']}")
            
            # Check bin field (CLI tools)
            if "bin" in data:
                if isinstance(data["bin"], dict):
                    for cmd, path in data["bin"].items():
                        entry_points.append(f"{path} - CLI command '{cmd}'")
                else:
                    entry_points.append(f"{data['bin']} - CLI entry")
        
        except json.JSONDecodeError:
            pass
        
        return entry_points
    
    def _find_python_entry_points(self, setup_py_content: str) -> List[str]:
        """Find entry points from setup.py"""
        import re
        
        entry_points = []
        
        # Look for entry_points or console_scripts
        console_scripts_match = re.search(
            r"console_scripts.*?\[(.*?)\]",
            setup_py_content,
            re.DOTALL
        )
        
        if console_scripts_match:
            scripts = console_scripts_match.group(1)
            # Extract script definitions
            script_lines = [line.strip().strip("'\"") for line in scripts.split('\n') if '=' in line]
            for script in script_lines:
                entry_points.append(f"CLI command: {script}")
        
        return entry_points
    
    def _infer_from_tech_stack(self, tech_stack: List[str], all_files: List[str]) -> List[str]:
        """Infer entry points based on detected tech stack"""
        entry_points = []
        
        # Django
        if "Django" in tech_stack:
            if "manage.py" in all_files:
                entry_points.append("manage.py - Django management commands")
            wsgi_files = [f for f in all_files if 'wsgi.py' in f]
            entry_points.extend([f"{f} - Django WSGI application" for f in wsgi_files])
        
        # Flask
        if "Flask" in tech_stack:
            app_files = [f for f in all_files if f.endswith('app.py')]
            entry_points.extend([f"{f} - Flask application" for f in app_files])
        
        # FastAPI
        if "FastAPI" in tech_stack:
            main_files = [f for f in all_files if 'main.py' in f]
            entry_points.extend([f"{f} - FastAPI application" for f in main_files])
        
        # Next.js
        if "Next.js" in tech_stack:
            entry_points.append("pages/ - Next.js pages directory")
            entry_points.append("app/ - Next.js app directory (if using App Router)")
        
        # Docker
        if "Docker" in tech_stack:
            entry_points.append("Dockerfile - Container entry point")
        
        return entry_points
