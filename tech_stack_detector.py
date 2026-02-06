"""
Technology stack detection module
"""

from typing import Dict, List, Set, Any


class TechStackDetector:
    """Detects the technology stack used in a repository"""
    
    # File patterns mapped to technologies
    TECH_INDICATORS = {
        # Python
        "requirements.txt": ["Python", "pip"],
        "Pipfile": ["Python", "pipenv"],
        "pyproject.toml": ["Python", "Poetry"],
        "setup.py": ["Python"],
        "conda.yml": ["Python", "Conda"],
        "environment.yml": ["Python", "Conda"],
        
        # JavaScript/Node.js
        "package.json": ["Node.js", "npm"],
        "package-lock.json": ["Node.js", "npm"],
        "yarn.lock": ["Node.js", "yarn"],
        "pnpm-lock.yaml": ["Node.js", "pnpm"],
        
        # TypeScript
        "tsconfig.json": ["TypeScript"],
        
        # Frontend frameworks
        "next.config.js": ["Next.js", "React"],
        "nuxt.config.js": ["Nuxt.js", "Vue.js"],
        "angular.json": ["Angular"],
        "vue.config.js": ["Vue.js"],
        "svelte.config.js": ["Svelte"],
        
        # Build tools
        "webpack.config.js": ["Webpack"],
        "vite.config.js": ["Vite"],
        "rollup.config.js": ["Rollup"],
        "esbuild.config.js": ["esbuild"],
        
        # Java
        "pom.xml": ["Java", "Maven"],
        "build.gradle": ["Java", "Gradle"],
        "build.gradle.kts": ["Kotlin", "Gradle"],
        
        # Go
        "go.mod": ["Go"],
        "go.sum": ["Go"],
        
        # Rust
        "Cargo.toml": ["Rust", "Cargo"],
        "Cargo.lock": ["Rust", "Cargo"],
        
        # Ruby
        "Gemfile": ["Ruby", "Bundler"],
        "Gemfile.lock": ["Ruby", "Bundler"],
        
        # PHP
        "composer.json": ["PHP", "Composer"],
        
        # C/C++
        "CMakeLists.txt": ["C++", "CMake"],
        "Makefile": ["C/C++", "Make"],
        
        # .NET
        ".csproj": ["C#", ".NET"],
        ".fsproj": ["F#", ".NET"],
        ".sln": [".NET"],
        
        # Infrastructure/DevOps
        "Dockerfile": ["Docker"],
        "docker-compose.yml": ["Docker", "Docker Compose"],
        ".dockerignore": ["Docker"],
        "Vagrantfile": ["Vagrant"],
        "terraform.tf": ["Terraform"],
        "ansible.cfg": ["Ansible"],
        
        # CI/CD
        ".github/workflows": ["GitHub Actions"],
        ".gitlab-ci.yml": ["GitLab CI"],
        ".travis.yml": ["Travis CI"],
        "Jenkinsfile": ["Jenkins"],
        ".circleci/config.yml": ["CircleCI"],
        
        # Databases
        "prisma/schema.prisma": ["Prisma", "Database ORM"],
        "sequelize-config.js": ["Sequelize", "Database ORM"],
        "alembic.ini": ["Alembic", "SQL Migrations"],
        
        # Testing
        "jest.config.js": ["Jest"],
        "pytest.ini": ["pytest"],
        "phpunit.xml": ["PHPUnit"],
        ".rspec": ["RSpec"],
        "karma.conf.js": ["Karma"],
    }
    
    # File extensions mapped to languages
    EXTENSION_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React',
        '.tsx': 'TypeScript React',
        '.java': 'Java',
        '.kt': 'Kotlin',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.c': 'C',
        '.cpp': 'C++',
        '.cs': 'C#',
        '.swift': 'Swift',
        '.dart': 'Dart',
        '.r': 'R',
        '.scala': 'Scala',
        '.vue': 'Vue.js',
    }
    
    def detect(
        self,
        directory_structure: Dict[str, Any],
        key_files: Dict[str, str],
        dependencies: Dict[str, List[str]]
    ) -> List[str]:
        """
        Detect the technology stack from repository structure
        
        Returns:
            List of detected technologies
        """
        tech_stack = set()
        
        # Step 1: Detect from key configuration files
        for filename in key_files.keys():
            if filename in self.TECH_INDICATORS:
                tech_stack.update(self.TECH_INDICATORS[filename])
            
            # Check for partial matches (e.g., .csproj files)
            for pattern, techs in self.TECH_INDICATORS.items():
                if pattern in filename:
                    tech_stack.update(techs)
        
        # Step 2: Detect from file extensions
        extensions = self._extract_extensions(directory_structure)
        for ext, count in extensions.items():
            if ext in self.EXTENSION_MAP:
                tech_stack.add(self.EXTENSION_MAP[ext])
        
        # Step 3: Detect from dependencies
        framework_deps = self._detect_frameworks_from_dependencies(dependencies)
        tech_stack.update(framework_deps)
        
        # Step 4: Analyze package.json for specific frameworks
        if "package.json" in key_files:
            package_techs = self._analyze_package_json(key_files["package.json"])
            tech_stack.update(package_techs)
        
        # Step 5: Analyze requirements.txt for Python frameworks
        if "requirements.txt" in key_files:
            python_techs = self._analyze_requirements_txt(key_files["requirements.txt"])
            tech_stack.update(python_techs)
        
        return sorted(list(tech_stack))
    
    def _extract_extensions(self, structure: Dict[str, Any]) -> Dict[str, int]:
        """Extract file extensions and their counts"""
        extensions = {}
        
        for file_info in structure.get("files", []):
            name = file_info["name"]
            if '.' in name:
                ext = '.' + name.split('.')[-1]
                extensions[ext] = extensions.get(ext, 0) + 1
        
        for dir_info in structure.get("directories", []):
            sub_extensions = self._extract_extensions(dir_info.get("contents", {}))
            for ext, count in sub_extensions.items():
                extensions[ext] = extensions.get(ext, 0) + count
        
        return extensions
    
    def _detect_frameworks_from_dependencies(
        self,
        dependencies: Dict[str, List[str]]
    ) -> Set[str]:
        """Detect frameworks from dependency imports"""
        frameworks = set()
        
        # Common framework indicators
        framework_map = {
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'express': 'Express.js',
            'fastapi': 'FastAPI',
            'flask': 'Flask',
            'django': 'Django',
            'spring': 'Spring Framework',
            'rails': 'Ruby on Rails',
            'laravel': 'Laravel',
            'gin': 'Gin (Go)',
            'fiber': 'Fiber (Go)',
            'actix': 'Actix (Rust)',
            'rocket': 'Rocket (Rust)',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'numpy': 'NumPy',
            'pandas': 'Pandas',
            'sklearn': 'scikit-learn',
        }
        
        # Check all dependencies
        all_deps = set()
        for deps in dependencies.values():
            all_deps.update(deps)
        
        for dep in all_deps:
            dep_lower = dep.lower()
            for key, framework in framework_map.items():
                # Exact match only (avoid false positives like "gin" matching "engine")
                if dep_lower == key:
                    frameworks.add(framework)
        
        return frameworks
    
    def _analyze_package_json(self, content: str) -> Set[str]:
        """Analyze package.json for specific frameworks and tools"""
        import json
        
        frameworks = set()
        
        try:
            data = json.loads(content)
            
            # Check dependencies and devDependencies
            all_deps = {}
            all_deps.update(data.get("dependencies", {}))
            all_deps.update(data.get("devDependencies", {}))
            
            # Map package names to frameworks
            package_map = {
                'react': 'React',
                'react-dom': 'React',
                'next': 'Next.js',
                'vue': 'Vue.js',
                'nuxt': 'Nuxt.js',
                '@angular/core': 'Angular',
                'svelte': 'Svelte',
                'express': 'Express.js',
                'koa': 'Koa.js',
                'fastify': 'Fastify',
                'nestjs': 'NestJS',
                'typescript': 'TypeScript',
                'webpack': 'Webpack',
                'vite': 'Vite',
                'jest': 'Jest',
                'mocha': 'Mocha',
                'cypress': 'Cypress',
                'playwright': 'Playwright',
                'tailwindcss': 'Tailwind CSS',
                'bootstrap': 'Bootstrap',
                'sass': 'Sass/SCSS',
                'graphql': 'GraphQL',
                'apollo': 'Apollo GraphQL',
                'redux': 'Redux',
                'mobx': 'MobX',
                'electron': 'Electron',
            }
            
            for package, framework in package_map.items():
                if package in all_deps:
                    frameworks.add(framework)
            
        except json.JSONDecodeError:
            pass
        
        return frameworks
    
    def _analyze_requirements_txt(self, content: str) -> Set[str]:
        """Analyze requirements.txt for Python frameworks"""
        frameworks = set()
        
        # Map package names to frameworks
        package_map = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'pyramid': 'Pyramid',
            'tornado': 'Tornado',
            'numpy': 'NumPy',
            'pandas': 'Pandas',
            'scipy': 'SciPy',
            'matplotlib': 'Matplotlib',
            'seaborn': 'Seaborn',
            'sklearn': 'scikit-learn',
            'scikit-learn': 'scikit-learn',
            'tensorflow': 'TensorFlow',
            'keras': 'Keras',
            'torch': 'PyTorch',
            'pytorch': 'PyTorch',
            'celery': 'Celery',
            'sqlalchemy': 'SQLAlchemy',
            'pytest': 'pytest',
            'requests': 'Requests',
            'beautifulsoup4': 'Beautiful Soup',
            'scrapy': 'Scrapy',
        }
        
        lines = content.lower().split('\n')
        for line in lines:
            # Remove version specifiers
            package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
            if package in package_map:
                frameworks.add(package_map[package])
        
        return frameworks
