"""
Session state initialisation, reset, and convenience helpers.
"""
import copy
import streamlit as st

# All top-level session keys and their default values
_DEFAULTS: dict = {
    "messages":          [],   # chat history: [{"role": "user"|"assistant", "content": str}]
    "step":              "greeting",
    # Steps: greeting | intent_select | mode_select | collecting | review | finalized
    "selected_intent":   None,
    "collection_mode":   None,
    # Modes: one_by_one | show_all | download_template
    "answers":           {},   # {field_key: value}
    "current_q_index":  0,    # pointer for one_by_one mode
    "manifest_versions": [],   # list of answer snapshots, newest last
    "manifest_version":  0,    # 1-based count
    "confirmed":         False,
    "uploaded_parsed":   None,
    "company_name":      "",    # client / company name entered at onboarding start
}


def init_session() -> None:
    """Set missing session keys to their defaults (safe to call on every rerun)."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(default)


def reset_session() -> None:
    """Reset all keys to defaults (used by the Reset button)."""
    for key, default in _DEFAULTS.items():
        st.session_state[key] = copy.deepcopy(default)


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def push_manifest_version(answers: dict) -> None:
    """Save a deep-copy snapshot of the current answers and bump the version counter."""
    st.session_state.manifest_versions.append(copy.deepcopy(answers))
    st.session_state.manifest_version = len(st.session_state.manifest_versions)


def load_client(company_name: str, record: dict) -> None:
    """Load a client registry record into the current session state."""
    answers = copy.deepcopy(record.get("answers", {}))
    version = record.get("version", 0)
    intent  = record.get("intent")
    if intent == "—":
        intent = None
    step = record.get("step", "review")
    # Snap un-resumable steps to review (can't resume mid-collection without mode)
    if step not in ("review", "finalized"):
        step = "review"

    st.session_state.company_name      = company_name
    st.session_state.selected_intent   = intent
    st.session_state.answers           = answers
    st.session_state.manifest_version  = version
    st.session_state.manifest_versions = [copy.deepcopy(answers)] if answers else []
    st.session_state.step              = step
    st.session_state.collection_mode   = None
    st.session_state.current_q_index   = 0
    st.session_state.confirmed         = False
    st.session_state.uploaded_parsed   = None
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            f"Resuming onboarding for **{company_name}**"
            + (f" — _{intent}_" if intent else "")
            + ".\n\nUse the buttons below to confirm, edit, or download the manifest."
        ),
    }]
