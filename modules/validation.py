"""
Validation helpers for manifest field values.
"""
import re
from typing import Dict, List, Any


def validate_email(value: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value.strip()))


def validate_answers(answers: Dict[str, Any], questions: List[Dict]) -> Dict[str, str]:
    """
    Validate a set of answers against the question definitions.
    Returns {field_key: error_message} for every invalid field.
    """
    errors: Dict[str, str] = {}

    for q in questions:
        key   = q["key"]
        label = q["label"]
        value = str(answers.get(key, "")).strip()

        # Required check
        if q.get("required") and not value:
            errors[key] = f"'{label}' is required."
            continue

        if not value:
            continue  # optional and empty — skip type checks

        if q["type"] == "email" and not validate_email(value):
            errors[key] = f"'{label}' must be a valid email address (e.g. name@company.com)."

        if q["type"] == "number":
            try:
                if int(value) <= 0:
                    errors[key] = f"'{label}' must be a positive whole number."
            except ValueError:
                errors[key] = f"'{label}' must be a valid number."

        if q["type"] == "date":
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                errors[key] = f"'{label}' must be in YYYY-MM-DD format."

    return errors
