"""
Test script for the Navigator Agent
"""

import os
from dotenv import load_dotenv
from navigator_agent import NavigatorAgent

# Load environment variables
load_dotenv()

def test_navigator():
    """Test the Navigator Agent on a sample repository"""
    
    # Get API keys
    github_token = os.getenv("GITHUB_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found in environment variables")
        print("Please create a .env file with your GitHub token")
        return
    
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("Please get a free API key from: https://console.groq.com/keys")
        return
    
    print("🚀 Initializing Navigator Agent...")
    navigator = NavigatorAgent(
        github_token=github_token,
        groq_api_key=groq_api_key
    )
    
    # Test with a small, well-known repository
    test_repo = "https://github.com/mohamadassaf96/WIFI_Jammer"
    print(f"\n📊 Analyzing repository: {test_repo}")
    print("This may take a minute...\n")
    
    try:
        report = navigator.analyze_repository(test_repo)
        
        print("=" * 80)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 80)
        print(report)
        print("=" * 80)
        
        # Generate unique filename based on repo name and timestamp
        from datetime import datetime
        repo_name = test_repo.split('/')[-1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"navigator_report_{repo_name}_{timestamp}"
        
        # Save report to markdown file
        md_filename = f"{base_filename}.md"
        with open(md_filename, "w") as f:
            f.write(report)
        print(f"\n💾 Report saved to: {md_filename}")
        
        # Save report to PDF
        try:
            import markdown
            from weasyprint import HTML
            
            # Convert markdown to HTML
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
                    code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                {markdown.markdown(report, extensions=['extra', 'nl2br'])}
            </body>
            </html>
            """
            
            # Generate PDF with unique name
            pdf_filename = f"{base_filename}.pdf"
            HTML(string=html_content).write_pdf(pdf_filename)
            print(f"📄 Report also saved as PDF: {pdf_filename}")
        except Exception as e:
            print(f"⚠️  Could not generate PDF: {e}")
            print("   Markdown report is still available.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_navigator()
