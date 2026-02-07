"""Orchestrator Agent - Synthesizes all findings and creates final report."""
import json
from typing import Dict
from langchain_openai import ChatOpenAI
from src.state import AgentState
import os

# Set OpenAI configuration
os.environ["OPENAI_API_KEY"] = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhZXNKN2kxNGNidnVuTU40MTJrOU5yZ2ROeENhTlJudTNPbC1TU08ycFlJIn0.eyJleHAiOjE3NzA0NDI4MTIsImlhdCI6MTc3MDQ0MTAxMiwiYXV0aF90aW1lIjoxNzcwNDQxMDExLCJqdGkiOiJmZjUxMTdhNC04NGE2LTRjMjktYjk0OC0wMTg3NzY2MWZkODciLCJpc3MiOiJodHRwczovL2F1dGgubWNraW5zZXkuaWQvYXV0aC9yZWFsbXMvciIsImF1ZCI6ImJjZDIzNzI4LTNkMjctNDQ3Yy1hMGE5LWVhY2FmMzkzYTZmNSIsInN1YiI6IjZhZjEyNDMxLWUzYWMtNGM3Mi1hYjZhLTY5ZjI4ODlmYzZmYSIsInR5cCI6IklEIiwiYXpwIjoiYmNkMjM3MjgtM2QyNy00NDdjLWEwYTktZWFjYWYzOTNhNmY1Iiwic2Vzc2lvbl9zdGF0ZSI6ImRiNzUwODQ5LWJlMmUtNDk4NC04NmZkLWMyOGY3MThjZWFhZiIsImF0X2hhc2giOiIzMlVsT3dMMm8wUlNvUmVtX3gzUDlRIiwibmFtZSI6IlJpY2hhcmQgQ291cGVydGh3YWl0ZSIsImdpdmVuX25hbWUiOiJSaWNoYXJkIiwiZmFtaWx5X25hbWUiOiJDb3VwZXJ0aHdhaXRlIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYjJiZWVkNDk3YjdkYzRmZiIsImVtYWlsIjoiUmljaGFyZF9Db3VwZXJ0aHdhaXRlQG1ja2luc2V5LmNvbSIsImFjciI6IjEiLCJzaWQiOiJkYjc1MDg0OS1iZTJlLTQ5ODQtODZmZC1jMjhmNzE4Y2VhYWYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZm1ubyI6IjMxNjczNyIsImdyb3VwcyI6WyIyOTA3ZmExYy02ODNmLTRjZjctODU1NS04YzM0YTE2Yzg4ZDgiLCJBbGwgRmlybSBVc2VycyIsIjAzYjE1YTM0LTY1NWUtNGVjNC04MzRhLWI5ZGRhMTk3MjBmMCJdfQ.ZSSU7ZL8l5o3KFoU0fhBtwapRddVm5Nz9o1mnIBj_3XYifi77shBUsRVm2cVEL3uxLTwYpybBSet2Q64O4NZJYOlfjjlukZHUeiot79mL3iTDyprzns34ldBnWtIbUZD4S-VF7FCPbgsRmQIlPlm8BCR9UQhjgQ3Lt_fCOuyfQli5-RZU6ypESIzFsZ-X3ROKFzzmym1fif0paxcyfZiZx8gFrI_Py0fxa1pznuiSNGzJRcnSmuKQIARn0AfJGvm9VB07e5btuslRx4w1sexSy9vbJayPezt0EL3_-RDDsAUZ7u3Q3PjgVlcRfv0INgPpQjBncmSFvjsB-IPxkep8g"
os.environ["OPENAI_BASE_URL"] = "https://openai.prod.ai-gateway.quantumblack.com/2907fa1c-683f-4cf7-8555-8c34a16c88d8/v1"

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)


def orchestrator_agent(state: AgentState) -> Dict:
    """
    ORCHESTRATOR: Synthesizes all agent outputs into a final onboarding report.
    """
    metadata = state["metadata"]
    navigator_map = state.get("navigator_map", {})
    context_summary = state.get("context_summary", "N/A")
    mentor_guide = state.get("mentor_guide", "N/A")
    visualization = state.get("visualization", "N/A")
    errors = state.get("errors", [])

    prompt = f"""You are a technical documentation system. Be factual and concise.

Synthesize all agent findings into a comprehensive onboarding report.

REPOSITORY: {metadata['full_name']}
STARS: {metadata['stars']} | LANGUAGE: {metadata['language']}

AGENT FINDINGS:
1. NAVIGATOR: {json.dumps(navigator_map, indent=2)}
2. CONTEXT: {context_summary}
3. MENTOR: {mentor_guide}
4. VISUALIZER: Diagram generated

ERRORS: {errors if errors else "None"}

Create a structured markdown report with these sections:

# {metadata['full_name']} - Onboarding Report

## Executive Summary
[2-3 sentences about the project]

## Repository Overview
[Key facts from NAVIGATOR]

## Code Analysis
[Key findings from CONTEXT]

## Recommended Learning Path
[Summary from MENTOR]

## Architecture Visualization
[Note about diagram availability]

## Quality Assessment
- Confidence Score: X/10
- Data Quality: [Issues found]
- Recommendations: [Next steps]
"""

    try:
        response = llm.invoke(prompt)
        # Extract content from AIMessage object
        response_text = response.content if hasattr(response, 'content') else str(response)

        return {
            "final_report": response_text,
            "messages": ["ORCHESTRATOR: Final report synthesized"],
        }
    except Exception as e:
        return {
            "final_report": f"Error creating final report: {e}",
            "errors": [f"Orchestrator error: {e}"],
            "messages": [f"ORCHESTRATOR: Failed - {e}"],
        }
