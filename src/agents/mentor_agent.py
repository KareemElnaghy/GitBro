"""Mentor Agent - Creates onboarding guide and learning path."""
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


def mentor_agent(state: AgentState) -> Dict:
    """
    MENTOR: Creates onboarding guide and learning path.
    Reads navigator_map and context_output from state.
    """
    navigator_map = state.get("navigator_map", {})
    context_output = state.get("context_output", {})
    metadata = state["metadata"]

    prompt = f"""You are an engineering onboarding system. Create a learning path and return valid JSON only.

REPOSITORY: {metadata['full_name']}
LANGUAGE: {metadata['language']}

STRUCTURE:
- Entry points: {navigator_map.get('entry_points', [])}
- Core modules: {navigator_map.get('core_modules', [])}
- Architecture: {navigator_map.get('architecture_type', 'unknown')}

CODE ANALYSIS:
- Technologies: {context_output.get('technologies', [])}
- Key patterns: {context_output.get('patterns', [])}
- Complexity: {context_output.get('complexity_score', 0.5)}

Provide:
1. Learning path (ordered steps with time estimates)
2. Prerequisites (required knowledge)
3. Total estimated hours
4. Difficulty level
5. Key concepts to understand

Return valid JSON only (no markdown, no code blocks):
{{
  "learning_path": [
    {{"step": 1, "file": "main.py", "estimated_time": "30min", "concepts": ["FastAPI", "routing"]}}
  ],
  "prerequisites": ["Python basics", "REST APIs"],
  "estimated_total_hours": 3.0,
  "difficulty": "intermediate",
  "key_concepts": ["concept1", "concept2"]
}}

Base time estimates on actual code complexity. Use realistic estimates.
"""

    try:
        response = llm.invoke(prompt)
        # Extract content from AIMessage object
        response_text = response.content if hasattr(response, 'content') else str(response)
        result = extract_json(response_text)

        # Create human-readable guide
        guide = f"""ONBOARDING GUIDE - {metadata['full_name']}

DIFFICULTY: {result['difficulty'].upper()}
ESTIMATED TIME: {result['estimated_total_hours']} hours

PREREQUISITES:
"""
        for p in result["prerequisites"]:
            guide += f"  - {p}\n"

        guide += "\nLEARNING PATH:\n"
        for step in result["learning_path"]:
            guide += f"  {step['step']}. {step['file']} ({step['estimated_time']}) - {', '.join(step['concepts'])}\n"

        guide += f"\nKEY CONCEPTS: {', '.join(result['key_concepts'])}"

        return {
            "mentor_guide": guide,
            "messages": [f"MENTOR: {len(result['learning_path'])} steps, {result['estimated_total_hours']}h total"],
        }
    except Exception as e:
        return {
            "mentor_guide": "Error creating onboarding guide",
            "errors": [f"Mentor agent error: {e}"],
            "messages": [f"MENTOR: Failed - {e}"],
        }
