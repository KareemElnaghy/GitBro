"""Shared utilities for GitBro agents."""
import json
import re


def _fix_arrays_with_object_entries(text: str) -> str:
    """
    Fix a common LLM mistake: putting "key": "value" object entries inside JSON arrays.
    E.g. the LLM copies package.json format into a dependencies array:
      ["flask", "@emotion/react": "^11.14.0"]
    This converts them to flat strings: ["flask", "@emotion/react ^11.14.0"]
    """
    stack = []  # tracks '[' and '{' nesting
    result = []
    i = 0

    while i < len(text):
        ch = text[i]

        if ch == "[":
            stack.append("[")
            result.append(ch)
            i += 1
        elif ch == "]":
            if stack and stack[-1] == "[":
                stack.pop()
            result.append(ch)
            i += 1
        elif ch == "{":
            stack.append("{")
            result.append(ch)
            i += 1
        elif ch == "}":
            if stack and stack[-1] == "{":
                stack.pop()
            result.append(ch)
            i += 1
        elif stack and stack[-1] == "[" and ch == '"':
            # Directly inside an array (not inside a nested object)
            # Check if this is a "key": "value" pattern that needs fixing
            end_quote = text.find('"', i + 1)
            if end_quote == -1:
                result.append(ch)
                i += 1
                continue

            key = text[i:end_quote + 1]
            after = text[end_quote + 1:end_quote + 10].lstrip()

            if after.startswith(":"):
                # Found "key": ... pattern inside array
                colon_idx = text.index(":", end_quote + 1)
                rest = text[colon_idx + 1:].lstrip()
                if rest.startswith('"'):
                    val_start = text.index('"', colon_idx + 1)
                    val_end = text.find('"', val_start + 1)
                    if val_end != -1:
                        value = text[val_start + 1:val_end]
                        key_text = key[1:-1]
                        result.append(f'"{key_text} {value}"')
                        i = val_end + 1
                        continue

            # Normal string in array - pass through
            result.append(key)
            i = end_quote + 1
        else:
            result.append(ch)
            i += 1

    return "".join(result)


def extract_json(text: str) -> dict:
    """
    Extract JSON from LLM response, handling common formatting issues:
    - Markdown code blocks
    - Trailing commas before } or ]
    - "key": "value" entries inside arrays (package.json format leak)
    - Extra text before/after the JSON object
    """
    text = text.strip()

    # Strip markdown code blocks
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find a JSON object in the text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group(0)

        # Remove trailing commas
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # Fix object-style entries inside arrays
        candidate = _fix_arrays_with_object_entries(candidate)
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("Could not extract valid JSON from LLM response", text, 0)
