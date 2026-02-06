"""
Dependency analysis module for understanding code relationships
"""

from typing import Dict, List, Set
import re


class DependencyAnalyzer:
    """Analyzes code dependencies and import relationships"""
    
    def __init__(self, github_token: str):
        from github_tools import GitHubClient
        self.github_client = GitHubClient(github_token)
    
    def analyze(self, owner: str, repo: str, directory_structure: Dict) -> Dict[str, List[str]]:
        """
        Analyze dependencies across the repository
        
        Returns:
            Dictionary mapping file paths to their dependencies
        """
        dependencies = {}
        
        # Extract all code files
        code_files = self._extract_code_files(directory_structure)
        
        for file_info in code_files:
            file_path = file_info["path"]
            
            try:
                content = self.github_client.get_file_content(owner, repo, file_path)
                file_deps = self._extract_dependencies(content, file_path)
                dependencies[file_path] = file_deps
            except Exception as e:
                # Silently skip files that can't be accessed (404, etc.)
                if "404" not in str(e):
                    print(f"Error analyzing {file_path}: {e}")
        
        return dependencies
    
    def _extract_code_files(self, structure: Dict, code_files: List = None) -> List[Dict]:
        """Recursively extract all code files from directory structure"""
        if code_files is None:
            code_files = []
        
        # Add files with code extensions
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala',
            '.r', '.jl', '.m', '.mm', '.sh', '.bash', '.dart', '.vue'
        }
        
        for file_info in structure.get("files", []):
            file_ext = '.' + file_info["name"].split('.')[-1] if '.' in file_info["name"] else ''
            if file_ext.lower() in code_extensions:
                code_files.append(file_info)
        
        # Recurse into subdirectories
        for dir_info in structure.get("directories", []):
            print(f"Extracting from directory: {dir_info.get('path', 'unknown')}")
            self._extract_code_files(dir_info.get("contents", {}), code_files)
        
        print(f"Total code files found: {len(code_files)}")
        return code_files
    
    def _extract_dependencies(self, content: str, file_path: str) -> List[str]:
        """Extract dependencies from file content based on file type"""
        file_ext = '.' + file_path.split('.')[-1] if '.' in file_path else ''
        
        if file_ext == '.py':
            return self._extract_python_imports(content)
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            return self._extract_javascript_imports(content)
        elif file_ext == '.java':
            return self._extract_java_imports(content)
        elif file_ext == '.go':
            return self._extract_go_imports(content)
        else:
            return []
    
    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python import statements"""
        imports = set()
        
        # Match: import module
        # Match: from module import something
        patterns = [
            r'^import\s+([\w\.]+)',
            r'^from\s+([\w\.]+)\s+import',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # Get the top-level module
                    module = match.group(1).split('.')[0]
                    imports.add(module)
        
        return sorted(list(imports))
    
    def _extract_javascript_imports(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript import statements"""
        imports = set()
        
        # Match: import ... from 'module'
        # Match: import('module')
        # Match: require('module')
        patterns = [
            r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
            r"import\s*\(['\"]([^'\"]+)['\"]\)",
            r"require\s*\(['\"]([^'\"]+)['\"]\)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                module = match.group(1)
                # Extract package name (before first /)
                if module.startswith('.'):
                    continue  # Skip relative imports
                package = module.split('/')[0]
                # Handle scoped packages (@org/package)
                if package.startswith('@') and '/' in module:
                    package = '/'.join(module.split('/')[:2])
                imports.add(package)
        
        return sorted(list(imports))
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Extract Java import statements"""
        imports = set()
        
        # Match: import package.Class;
        pattern = r'^import\s+([\w\.]+);'
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                # Get the package (everything before the last dot)
                full_import = match.group(1)
                if '.' in full_import:
                    package = '.'.join(full_import.split('.')[:-1])
                    imports.add(package)
        
        return sorted(list(imports))
    
    def _extract_go_imports(self, content: str) -> List[str]:
        """Extract Go import statements"""
        imports = set()
        
        # Match single import: import "package"
        # Match multi import block
        single_pattern = r'import\s+"([^"]+)"'
        
        # Find all single imports
        matches = re.finditer(single_pattern, content)
        for match in matches:
            imports.add(match.group(1))
        
        # Find import blocks
        block_pattern = r'import\s+\((.*?)\)'
        blocks = re.finditer(block_pattern, content, re.DOTALL)
        for block in blocks:
            lines = block.group(1).split('\n')
            for line in lines:
                line = line.strip()
                match = re.match(r'"([^"]+)"', line)
                if match:
                    imports.add(match.group(1))
        
        return sorted(list(imports))
