"""
Test script for the Navigator Agent
"""
import os
from dotenv import load_dotenv
from src.agents.navigator_agent import navigator_agent
from src.github_client import GitHubClient
from src.state import AgentState

load_dotenv()


def test_navigator():
    """Test the Navigator Agent on a sample repository"""

    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("Error: GITHUB_TOKEN not found in environment variables")
        return

    print("Initializing test...")
    github_client = GitHubClient(token=github_token)

    # add here the repo to test
    test_repo = "https://github.com/JanaElfeky/CustomerChurnPredictor"
    print(f"Analyzing repository: {test_repo}\n")

    try:
        owner, repo_name = github_client.parse_repo_url(test_repo)
        metadata = github_client.get_repo_metadata(owner, repo_name)
        branch = metadata["default_branch"]
        file_tree = github_client.get_file_tree(owner, repo_name, branch)

        # Fetch README
        readme_content = None
        for readme_file in ["README.md", "README.rst", "README.txt", "README"]:
            try:
                readme_content = github_client.get_raw_content(owner, repo_name, readme_file, branch)
                break
            except Exception:
                continue

        print(f"Fetched {len(file_tree)} files from repository")

        initial_state: AgentState = {
            "repo_url": test_repo,
            "owner": owner,
            "repo_name": repo_name,
            "metadata": metadata,
            "file_tree": file_tree,
            "code_samples": {},
            "readme_content": readme_content,
            "navigator_map": None,
            "context_output": None,
            "context_summary": None,
            "mentor_guide": None,
            "visualization": None,
            "final_report": None,
            "messages": [],
            "errors": [],
        }

        result = navigator_agent(initial_state)

        print("\n" + "-" * 80)
        print("ANALYSIS COMPLETE")
        print("-" * 80)

        nav_map = result.get("navigator_map")
        if nav_map:
            print(f"\nEntry Points: {nav_map.get('entry_points', [])}")
            print(f"Core Modules: {nav_map.get('core_modules', [])}")
            print(f"Dependencies: {nav_map.get('dependencies', [])}")
            print(f"Architecture: {nav_map.get('architecture_type', 'unknown')}")
            print(f"Confidence: {nav_map.get('confidence_score', 0):.0%}")

        if result.get("errors"):
            print("\nErrors:")
            for error in result["errors"]:
                print(f"  - {error}")

        print("-" * 80)

        # Generate PDF report
        if nav_map:
            try:
                from datetime import datetime
                import markdown
                from weasyprint import HTML

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"navigator_report_{repo_name}_{timestamp}"

                readme_summary = nav_map.get("readme_summary", "No README found")

                report_content = f"""# Navigator Agent Report
## Repository: {metadata['full_name']}

### Repository Information
- Language: {metadata['language']}
- Stars: {metadata['stars']}
- Description: {metadata['description']}

### README Summary
{readme_summary}

### Analysis Results

#### Entry Points
{chr(10).join(f'- {ep}' for ep in nav_map.get('entry_points', []))}

#### Core Modules
{chr(10).join(f'- {cm}' for cm in nav_map.get('core_modules', []))}

#### Dependencies
{chr(10).join(f'- {dep}' for dep in nav_map.get('dependencies', []))}

#### Architecture
- Type: {nav_map.get('architecture_type', 'unknown')}
- Confidence: {nav_map.get('confidence_score', 0):.0%}
"""

                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                        h2 {{ color: #34495e; margin-top: 30px; }}
                        h3 {{ color: #7f8c8d; }}
                        ul {{ margin-left: 20px; }}
                    </style>
                </head>
                <body>
                    {markdown.markdown(report_content, extensions=['extra', 'nl2br'])}
                </body>
                </html>
                """

                pdf_filename = f"{base_filename}.pdf"
                HTML(string=html_content).write_pdf(pdf_filename)
                print(f"\nPDF report saved: {pdf_filename}")
            except Exception as e:
                print(f"\nWarning: Could not generate PDF: {e}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_navigator()
