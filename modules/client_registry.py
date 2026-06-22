"""
Cross-session client registry backed by st.cache_resource.
Every browser tab in the same Streamlit server process sees the same data.
"""
import copy
import streamlit as st
from datetime import datetime


@st.cache_resource
def _registry() -> dict:
    """Singleton dict shared across all sessions: {company_name -> record}."""
    return {}


def register_client(company_name: str, intent, step: str,
                    version: int, answers: dict) -> None:
    _registry()[company_name] = {
        "intent":     intent or "—",
        "step":       step,
        "version":    version,
        "answers":    copy.deepcopy(answers),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def all_clients() -> dict:
    """Return {name: record} sorted newest-updated first."""
    reg = _registry()
    return dict(sorted(reg.items(), key=lambda x: x[1]["updated_at"], reverse=True))


def get_client(company_name: str):
    return _registry().get(company_name)


def remove_client(company_name: str) -> None:
    _registry().pop(company_name, None)
