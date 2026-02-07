"""Visualizer Agent - Creates Mermaid architecture diagrams."""
from typing import Dict
from langchain_openai import ChatOpenAI
from src.state import AgentState
from src.utils import extract_json
import os

# Set OpenAI configuration
os.environ["OPENAI_API_KEY"] = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhZXNKN2kxNGNidnVuTU40MTJrOU5yZ2ROeENhTlJudTNPbC1TU08ycFlJIn0.eyJleHAiOjE3NzA0NDI4MTIsImlhdCI6MTc3MDQ0MTAxMiwiYXV0aF90aW1lIjoxNzcwNDQxMDExLCJqdGkiOiJmZjUxMTdhNC04NGE2LTRjMjktYjk0OC0wMTg3NzY2MWZkODciLCJpc3MiOiJodHRwczovL2F1dGgubWNraW5zZXkuaWQvYXV0aC9yZWFsbXMvciIsImF1ZCI6ImJjZDIzNzI4LTNkMjctNDQ3Yy1hMGE5LWVhY2FmMzkzYTZmNSIsInN1YiI6IjZhZjEyNDMxLWUzYWMtNGM3Mi1hYjZhLTY5ZjI4ODlmYzZmYSIsInR5cCI6IklEIiwiYXpwIjoiYmNkMjM3MjgtM2QyNy00NDdjLWEwYTktZWFjYWYzOTNhNmY1Iiwic2Vzc2lvbl9zdGF0ZSI6ImRiNzUwODQ5LWJlMmUtNDk4NC04NmZkLWMyOGY3MThjZWFhZiIsImF0X2hhc2giOiIzMlVsT3dMMm8wUlNvUmVtX3gzUDlRIiwibmFtZSI6IlJpY2hhcmQgQ291cGVydGh3YWl0ZSIsImdpdmVuX25hbWUiOiJSaWNoYXJkIiwiZmFtaWx5X25hbWUiOiJDb3VwZXJ0aHdhaXRlIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYjJiZWVkNDk3YjdkYzRmZiIsImVtYWlsIjoiUmljaGFyZF9Db3VwZXJ0aHdhaXRlQG1ja2luc2V5LmNvbSIsImFjciI6IjEiLCJzaWQiOiJkYjc1MDg0OS1iZTJlLTQ5ODQtODZmZC1jMjhmNzE4Y2VhYWYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZm1ubyI6IjMxNjczNyIsImdyb3VwcyI6WyIyOTA3ZmExYy02ODNmLTRjZjctODU1NS04YzM0YTE2Yzg4ZDgiLCJBbGwgRmlybSBVc2VycyIsIjAzYjE1YTM0LTY1NWUtNGVjNC04MzRhLWI5ZGRhMTk3MjBmMCJdfQ.ZSSU7ZL8l5o3KFoU0fhBtwapRddVm5Nz9o1mnIBj_3XYifi77shBUsRVm2cVEL3uxLTwYpybBSet2Q64O4NZJYOlfjjlukZHUeiot79mL3iTDyprzns34ldBnWtIbUZD4S-VF7FCPbgsRmQIlPlm8BCR9UQhjgQ3Lt_fCOuyfQli5-RZU6ypESIzFsZ-X3ROKFzzmym1fif0paxcyfZiZx8gFrI_Py0fxa1pznuiSNGzJRcnSmuKQIARn0AfJGvm9VB07e5btuslRx4w1sexSy9vbJayPezt0EL3_-RDDsAUZ7u3Q3PjgVlcRfv0INgPpQjBncmSFvjsB-IPxkep8g"
os.environ["OPENAI_BASE_URL"] = "https://openai.prod.ai-gateway.quantumblack.com/2907fa1c-683f-4cf7-8555-8c34a16c88d8/v1"

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
)


def visualizer_agent(state: AgentState) -> Dict:
    """
    VISUALIZER: Creates Mermaid architecture diagrams.
    Reads navigator_map and context_output from state.
    """
    navigator_map = state.get("navigator_map", {})
    context_output = state.get("context_output", {})

    prompt = f"""You are a software architecture diagram generator. Return valid JSON only.

STRUCTURE:
- Entry points: {navigator_map.get('entry_points', [])}
- Core modules: {navigator_map.get('core_modules', [])}
- Architecture: {navigator_map.get('architecture_type', 'unknown')}

CODE COMPONENTS:
- Key functions: {[f['name'] for f in context_output.get('key_functions', [])[:5]]}
- Key classes: {[c['name'] for c in context_output.get('key_classes', [])[:5]]}

Create a Mermaid flowchart showing:
1. Entry points
2. Core modules/components
3. Data flow between components
4. External dependencies

Return valid JSON only (no markdown, no code blocks):
{{
  "mermaid_diagram": "graph TD\\n    A[Entry] --> B[Module]\\n    ...",
  "diagram_type": "flowchart TD",
  "component_count": 5,
  "relationships_mapped": 8
}}

Use valid Mermaid syntax. Keep diagram focused (max 15 nodes). Use proper node IDs without spaces.
"""

    try:
        response = llm.invoke(prompt)
        # Extract content from AIMessage object
        response_text = response.content if hasattr(response, 'content') else str(response)
        result = extract_json(response_text)

        return {
            "visualization": result["mermaid_diagram"],
            "messages": [f"VISUALIZER: {result['component_count']} components, {result['relationships_mapped']} relationships"],
        }
    except Exception as e:
        return {
            "visualization": "Error creating diagram",
            "errors": [f"Visualizer agent error: {e}"],
            "messages": [f"VISUALIZER: Failed - {e}"],
        }
