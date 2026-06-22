"""
AI-powered SDLC Platform — floating chat console over a full dashboard.
Run with:  streamlit run app.py
"""
import streamlit as st
from modules.session_manager import (
    init_session, reset_session, add_message, push_manifest_version, load_client,
)
from modules.client_registry import register_client, all_clients
from modules.intents import INTENTS
from modules.validation import validate_answers
from modules.file_parser import parse_uploaded_file
from modules.manifest_generator import (
    generate_excel, generate_docx, generate_txt,
    generate_template_excel, generate_template_docx, generate_template_txt,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI-powered SDLC",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

for _k, _v in [("chat_open", True), ("chat_maximized", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Sync active session into the cross-tab client registry on every rerun
if st.session_state.get("company_name"):
    register_client(
        company_name=st.session_state.company_name,
        intent=st.session_state.selected_intent,
        step=st.session_state.step,
        version=st.session_state.manifest_version,
        answers=st.session_state.answers,
    )

# ── Base CSS (always applied) ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Light theme palette ─────────────────────────────────────────────────────
   Page bg  : #f0f5ff   (soft periwinkle-white)
   Panel bg : #ffffff   (pure white)
   Primary  : #2563eb   (blue-600)
   Light    : #dbeafe   (blue-100)
   Lighter  : #eff6ff   (blue-50)
   Border   : #d1ddf5
   Text     : #1e293b
   Muted    : #64748b
─────────────────────────────────────────────────────────────────────────── */

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Page background */
[data-testid="stAppViewContainer"] {
    background: #f0f5ff !important;
}
[data-testid="stMain"] .block-container {
    background: transparent !important;
}

/* Hide Streamlit's built-in sidebar toggle arrows — we provide our own */
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* Allow sidebar content to scroll */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    overflow-y: auto !important;
    height: 100%    !important;
    padding: 0      !important;
}

/* ── Dashboard styles ────────────────────────────────────── */
.dash-banner {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border: 1px solid #bfdbfe;
    border-radius: 14px; padding: 1.4rem 2rem; margin-bottom: 1rem;
}
.dash-banner h1 { margin: 0; font-size: 1.75rem; letter-spacing: -.4px; color: #1e3a8a; }
.dash-banner p  { margin: .25rem 0 0; color: #3b82f6; font-size: .92rem; }

.kpi-card {
    background: #ffffff;
    border: 1px solid #d1ddf5;
    border-left: 4px solid #60a5fa;
    border-radius: 12px; padding: 1rem 1.3rem;
    box-shadow: 0 1px 6px rgba(37,99,235,.07);
}
.kpi-label { font-size:.73rem; color:#64748b; font-weight:600;
             text-transform:uppercase; letter-spacing:.6px; }
.kpi-value { font-size:1.3rem; font-weight:700; color:#1e3a8a; margin-top:.25rem; }

.manifest-table { width:100%; border-collapse:collapse; font-size:.9rem; margin:.5rem 0; }
.manifest-table th {
    background: #dbeafe; color: #1e3a8a;
    padding:.5rem 1rem; text-align:left;
    border-bottom: 2px solid #93c5fd;
}
.manifest-table td { padding:.42rem 1rem; border-bottom:1px solid #e8eefb; color:#1e293b; }
.manifest-table tr:nth-child(even) td { background: #f5f8ff; }
.diff-added   td { background: #dcfce7 !important; }
.diff-changed td { background: #fef9c3 !important; }

/* ── Chat-window chrome ──────────────────────────────────── */
.chat-header {
    background: linear-gradient(90deg, #dbeafe 0%, #eff6ff 100%);
    border-bottom: 1px solid #bfdbfe;
    color: #1e3a8a;
    padding: .7rem 1rem;
    display: flex; justify-content: space-between; align-items: center;
    font-weight: 700; font-size: .95rem;
    letter-spacing: -.1px;
}

/* Tint Streamlit's native progress bar */
[data-testid="stProgressBar"] > div > div { background: #3b82f6 !important; }
[data-testid="stProgressBar"] { background: #dbeafe !important; }

/* Lighten Streamlit's default button outlines */
button[kind="secondary"] {
    border-color: #bfdbfe !important;
    color: #1e3a8a !important;
    background: #f0f7ff !important;
}
button[kind="secondary"]:hover {
    background: #dbeafe !important;
    border-color: #93c5fd !important;
}

/* Force dark text on all native Streamlit text nodes (belt-and-suspenders
   on top of the config.toml theme, covers edge-cases like injected HTML) */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] span { color: #1e293b !important; }

/* Caption text — Streamlit renders these as muted but they must stay visible */
[data-testid="stCaptionContainer"] p { color: #475569 !important; }

/* Alert / info / success / warning boxes */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span { color: #1e293b !important; }

/* Input placeholders */
::placeholder { color: #94a3b8 !important; }

/* ── Client info bar ─────────────────────────────────────── */
.client-info-bar {
    background: #ffffff;
    border: 1px solid #bfdbfe;
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: .5rem 1.1rem;
    margin-bottom: .8rem;
    display: flex;
    align-items: center;
    gap: .5rem;
    flex-wrap: wrap;
}
.ci-tag {
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 20px;
    padding: .18rem .8rem;
}
.ci-tag-label {
    color: #64748b;
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .5px;
}
.ci-tag-value { color: #1e3a8a; font-weight: 700; font-size: .87rem; }

/* ── "New Client Onboarding" link-button ─────────────────── */
a.new-ob-btn {
    display: inline-block;
    background: #2563eb;
    color: #ffffff !important;
    padding: .42rem 1rem;
    border-radius: 8px;
    text-decoration: none !important;
    font-weight: 600;
    font-size: .84rem;
    white-space: nowrap;
    line-height: 1.5;
}
a.new-ob-btn:hover { background: #1d4ed8 !important; }

/* ── Section titles ──────────────────────────────────────── */
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1e3a8a;
    padding: .35rem 0; margin: .3rem 0 .1rem;
    border-bottom: 2px solid #bfdbfe;
    letter-spacing: -.2px;
}

/* ── Status badges ───────────────────────────────────────── */
.badge {
    display: inline-block; padding: .15rem .65rem;
    border-radius: 12px; font-size: .74rem; font-weight: 700;
}
.badge-complete   { background: #dcfce7; color: #166534; }
.badge-inprogress { background: #fef3c7; color: #92400e; }
.badge-review     { background: #fce7f3; color: #9d174d; }
.badge-started    { background: #dbeafe; color: #1e40af; }
</style>
""", unsafe_allow_html=True)

# ── Dynamic CSS — repositions sidebar based on chat state ─────────────────────
def _chat_css() -> str:
    if not st.session_state.chat_open:
        return """<style>
section[data-testid="stSidebar"] { display:none !important; }
section[data-testid="stMain"]    { margin-left:0 !important; }
</style>"""
    if st.session_state.chat_maximized:
        return """<style>
section[data-testid="stSidebar"] {
    position:fixed !important; top:0 !important; left:0 !important;
    width:100vw !important; min-width:100vw !important;
    height:100vh !important; border-radius:0 !important;
    z-index:9999 !important; background:#f0f5ff !important;
    box-shadow:none !important; overflow-y:auto !important;
}
section[data-testid="stMain"] { display:none !important; }
</style>"""
    # Default: floating window at bottom-right
    return """<style>
section[data-testid="stSidebar"] {
    position:fixed     !important;
    bottom:20px        !important; right:20px !important;
    top:auto           !important; left:auto  !important;
    width:400px        !important; min-width:0 !important;
    height:580px       !important;
    border-radius:16px !important;
    overflow:hidden    !important;
    box-shadow:0 6px 32px rgba(37,99,235,.15) !important;
    border:1px solid #bfdbfe !important;
    z-index:999        !important;
    background:#f8fbff !important;
}
section[data-testid="stMain"] { margin-left:0 !important; }
</style>"""

st.markdown(_chat_css(), unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FLOATING CHAT CONSOLE
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Chat window title bar ────────────────────────────────────────────────
    st.markdown('<div class="chat-header">🤝&nbsp; Onboarding Assistant</div>',
                unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns([3, 1, 1])
    with ctrl1:
        step_label = {
            "greeting":"Welcome","client_name":"Client Name",
            "intent_select":"Select Intent",
            "mode_select":"Choose Mode","collecting":"Collecting Data",
            "review":"Review","finalized":"Complete ✅",
        }.get(st.session_state.step, "")
        st.caption(f"Step: **{step_label}**")
    with ctrl2:
        max_icon = "⛶" if not st.session_state.chat_maximized else "⊡"
        if st.button(max_icon, key="btn_max",
                     help="Maximize" if not st.session_state.chat_maximized else "Restore"):
            st.session_state.chat_maximized = not st.session_state.chat_maximized
            st.rerun()
    with ctrl3:
        if st.button("✕", key="btn_close", help="Close chat"):
            st.session_state.chat_open     = False
            st.session_state.chat_maximized = False
            st.rerun()

    st.divider()

    # ── Chat history ─────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Step-specific interactive UI ──────────────────────────────────────────
    step = st.session_state.step

    # GREETING
    if step == "greeting":
        if not st.session_state.messages:
            add_message("assistant",
                "👋 **Welcome!** Type **Start Client Onboarding Process** to begin.")
            st.rerun()
        prompt = st.chat_input("Type your message…")
        if prompt:
            add_message("user", prompt)
            if "start" in prompt.lower() and "onboarding" in prompt.lower():
                add_message("assistant",
                    "Great! 🚀 Please enter the **client / company name** to continue:")
                st.session_state.step = "client_name"
            else:
                add_message("assistant",
                    "Please type: **Start Client Onboarding Process**")
            st.rerun()

    # CLIENT NAME
    elif step == "client_name":
        prompt = st.chat_input("Enter client / company name…")
        if prompt and prompt.strip():
            name = prompt.strip()
            add_message("user", name)
            st.session_state.company_name = name
            add_message("assistant",
                f"✅ Client set to **{name}**.\n\n"
                "Now please select an **Onboarding Intent** below:")
            st.session_state.step = "intent_select"
            st.rerun()

    # INTENT SELECT
    elif step == "intent_select":
        for intent_key, intent_data in INTENTS.items():
            if st.button(intent_data["label"], key=f"i_{intent_key}",
                         use_container_width=True):
                st.session_state.selected_intent = intent_key
                add_message("user", f"Selected: **{intent_data['label']}**")
                add_message("assistant",
                    f"✅ **{intent_data['label']}** — _{intent_data['description']}_\n\n"
                    "**How would you like to provide the information?**")
                st.session_state.step = "mode_select"
                st.rerun()

    # MODE SELECT
    elif step == "mode_select":
        if st.button("💬 Answer one by one", key="m_obo", use_container_width=True):
            questions = INTENTS[st.session_state.selected_intent]["questions"]
            st.session_state.collection_mode  = "one_by_one"
            st.session_state.current_q_index  = 0
            add_message("user", "One by one.")
            add_message("assistant",
                f"**Q1/{len(questions)}:** {questions[0]['label']}"
                + ("  *(required)*" if questions[0].get("required") else ""))
            st.session_state.step = "collecting"
            st.rerun()

        if st.button("📋 Show all questions", key="m_all", use_container_width=True):
            st.session_state.collection_mode = "show_all"
            add_message("user", "All questions at once.")
            add_message("assistant", "Fill in the form below and submit:")
            st.session_state.step = "collecting"
            st.rerun()

        if st.button("📥 Download & fill template", key="m_tpl", use_container_width=True):
            st.session_state.collection_mode = "download_template"
            add_message("user", "Download template.")
            add_message("assistant",
                "Download a template below, fill it in, then upload it:")
            st.session_state.step = "collecting"
            st.rerun()

    # COLLECTING
    elif step == "collecting":
        intent_data = INTENTS[st.session_state.selected_intent]
        questions   = intent_data["questions"]
        mode        = st.session_state.collection_mode

        def _input_widget(q, current_val):
            """Render the right widget for a question type."""
            t = q["type"]
            lv = "collapsed"
            if t == "select":
                opts = q.get("options", [])
                return st.selectbox(q["label"], opts,
                    index=opts.index(current_val) if current_val in opts else 0,
                    label_visibility=lv)
            if t == "textarea":
                return st.text_area(q["label"], value=current_val,
                    label_visibility=lv, height=80)
            ph = {"number":"Positive integer","date":"YYYY-MM-DD",
                  "email":"name@company.com"}.get(t,"")
            return st.text_input(q["label"], value=current_val,
                placeholder=ph, label_visibility=lv)

        # ── Mode A: one by one ────────────────────────────────────────────
        if mode == "one_by_one":
            idx   = st.session_state.current_q_index
            q     = questions[idx]
            total = len(questions)
            cur   = st.session_state.answers.get(q["key"], "")

            with st.form(key=f"obo_{idx}"):
                st.markdown(f"**Q{idx+1}/{total}:  {q['label']}**"
                            + ("  *(required)*" if q.get("required") else ""))
                ans = _input_widget(q, cur)
                c1, c2 = st.columns(2)
                prev = c1.form_submit_button("← Prev", disabled=(idx == 0))
                nxt  = c2.form_submit_button(
                    "Review →" if idx == total - 1 else "Next →", type="primary")

            if prev:
                st.session_state.answers[q["key"]] = ans
                st.session_state.current_q_index   = idx - 1
                st.rerun()
            if nxt:
                errs = validate_answers({q["key"]: ans}, [q])
                if errs:
                    st.error(list(errs.values())[0])
                else:
                    st.session_state.answers[q["key"]] = ans
                    add_message("user", f"**{q['label']}:** {ans}")
                    if idx < total - 1:
                        nq = questions[idx + 1]
                        st.session_state.current_q_index = idx + 1
                        add_message("assistant",
                            f"**Q{idx+2}/{total}:** {nq['label']}"
                            + ("  *(required)*" if nq.get("required") else ""))
                    else:
                        push_manifest_version(st.session_state.answers)
                        add_message("assistant",
                            "✅ All done! Check the **dashboard** to review your manifest →")
                        st.session_state.step = "review"
                    st.rerun()

        # ── Mode B: show all ──────────────────────────────────────────────
        elif mode == "show_all":
            with st.form("all_form"):
                tmp: dict = {}
                for q in questions:
                    st.markdown(f"**{q['label']}**"
                                + ("  *(required)*" if q.get("required") else ""))
                    tmp[q["key"]] = _input_widget(q, st.session_state.answers.get(q["key"], ""))
                    st.markdown("")
                submitted = st.form_submit_button("Submit →", type="primary",
                                                  use_container_width=True)
            if submitted:
                errs = validate_answers(tmp, questions)
                if errs:
                    for m in errs.values():
                        st.error(m)
                else:
                    st.session_state.answers = tmp
                    push_manifest_version(tmp)
                    add_message("user", "Submitted all answers.")
                    add_message("assistant",
                        "✅ Manifest ready! Check the **dashboard** to review →")
                    st.session_state.step = "review"
                    st.rerun()

        # ── Mode C: download template ─────────────────────────────────────
        elif mode == "download_template":
            iname = st.session_state.selected_intent
            st.markdown("**⬇ Download a blank template:**")
            st.download_button("Excel (.xlsx)",
                data=generate_template_excel(questions, iname),
                file_name=f"template_{iname.replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
            st.download_button("Word (.docx)",
                data=generate_template_docx(questions, iname),
                file_name=f"template_{iname.replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True)
            st.download_button("Text (.txt)",
                data=generate_template_txt(questions, iname),
                file_name=f"template_{iname.replace(' ','_')}.txt",
                mime="text/plain", use_container_width=True)

            st.divider()
            st.markdown("**📤 Upload your filled template:**")
            up = st.file_uploader("Choose file", type=["xlsx","docx","txt"],
                                  key="tpl_up")
            if up:
                parsed = parse_uploaded_file(up, questions)
                if not parsed:
                    st.error("Cannot parse file — use the downloaded template.")
                else:
                    missing = [q["label"] for q in questions
                               if q.get("required")
                               and not str(parsed.get(q["key"], "")).strip()]
                    errs = validate_answers(parsed, questions)
                    if missing:
                        st.warning(f"Missing required: {', '.join(missing)}")
                    if errs:
                        for m in errs.values():
                            st.error(m)
                    if not errs and not missing:
                        st.session_state.answers = parsed
                        push_manifest_version(parsed)
                        add_message("user", f"Uploaded: **{up.name}**")
                        add_message("assistant",
                            "✅ Parsed! Check the **dashboard** to review →")
                        st.session_state.step = "review"
                        st.rerun()

    # REVIEW
    elif step == "review":
        questions = INTENTS[st.session_state.selected_intent]["questions"]
        answers   = st.session_state.answers
        st.markdown("**Manifest is ready on the dashboard. Confirm or edit:**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Confirm", type="primary", use_container_width=True,
                         key="chat_confirm"):
                push_manifest_version(answers)
                add_message("user", "Confirmed.")
                add_message("assistant",
                    "🎉 **Onboarding complete!** Download your files from the dashboard →")
                st.session_state.step = "finalized"
                st.rerun()
        with c2:
            if st.button("✏️ Edit", use_container_width=True, key="chat_edit"):
                st.session_state.step = "collecting"
                st.rerun()

        st.divider()
        st.markdown("**Or upload a corrected file:**")
        reup = st.file_uploader("Upload corrected",
                                type=["xlsx","docx","txt"],
                                key=f"reup_{st.session_state.manifest_version}")
        if reup:
            parsed = parse_uploaded_file(reup, questions)
            if not parsed:
                st.error("Cannot parse file.")
            else:
                errs = validate_answers(parsed, questions)
                if errs:
                    for m in errs.values(): st.error(m)
                else:
                    st.session_state.answers = parsed
                    push_manifest_version(parsed)
                    add_message("user", f"Uploaded corrected: **{reup.name}**")
                    add_message("assistant",
                        f"✅ Updated to v{st.session_state.manifest_version}. "
                        "Dashboard shows the diff →")
                    st.rerun()

    # FINALIZED
    elif step == "finalized":
        st.success("🎉 Onboarding complete!")
        st.markdown("Download your manifest files from the **dashboard** →")
        if st.button("🔄 Start New Onboarding", use_container_width=True,
                     key="chat_restart"):
            reset_session()
            st.rerun()

    # ── Bottom of chat: reset ─────────────────────────────────────────────────
    st.markdown("")
    st.divider()
    if st.button("🔄 Reset / Start Over", key="chat_reset", use_container_width=True):
        reset_session()
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# MAIN AREA — DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
STEP_LABELS = {
    "greeting":"Welcome","client_name":"Client Name",
    "intent_select":"Intent Selection",
    "mode_select":"Collection Mode","collecting":"Collecting Data",
    "review":"Review & Confirm","finalized":"Complete ✅",
}
STEP_PROGRESS = {
    "greeting":5,"client_name":12,
    "intent_select":20,"mode_select":35,
    "collecting":55,"review":80,"finalized":100,
}

step     = st.session_state.step
pct      = STEP_PROGRESS.get(step, 5)

# ── Dashboard header ──────────────────────────────────────────────────────────
left, right = st.columns([5, 1])
with left:
    st.markdown("""
<div class="dash-banner">
  <h1>🤖 AI-powered SDLC</h1>
  <p>Client onboarding · Manifest management · Software delivery lifecycle</p>
</div>""", unsafe_allow_html=True)
with right:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.chat_open:
        if st.button("✕ Close Chat", use_container_width=True, key="d_close"):
            st.session_state.chat_open      = False
            st.session_state.chat_maximized = False
            st.rerun()
    else:
        if st.button("💬 Open Chat", type="primary",
                     use_container_width=True, key="d_open"):
            st.session_state.chat_open = True
            st.rerun()

# ── Active session indicator ──────────────────────────────────────────────────
_company = st.session_state.get("company_name", "")
_intent_lbl = (INTENTS[st.session_state.selected_intent]["label"]
               if st.session_state.selected_intent else "—")
if _company:
    st.markdown(f"""
<div class="client-info-bar">
  <span style="font-size:.77rem;color:#64748b;font-weight:700;text-transform:uppercase;
               letter-spacing:.5px;margin-right:.4rem">Active Chat ·</span>
  <div class="ci-tag">
    <span class="ci-tag-label">Client</span>
    <span class="ci-tag-value">{_company}</span>
  </div>
  <div class="ci-tag">
    <span class="ci-tag-label">Intent</span>
    <span class="ci-tag-value">{_intent_lbl}</span>
  </div>
  <div class="ci-tag">
    <span class="ci-tag-label">Status</span>
    <span class="ci-tag-value">{STEP_LABELS.get(step, '—')}</span>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("")

# ── Dashboard KPI cards (registry-wide stats) ─────────────────────────────────
_clients_reg = all_clients()
_total_c     = len(_clients_reg)
_complete_c  = sum(1 for c in _clients_reg.values() if c["step"] == "finalized")
_inprog_c    = _total_c - _complete_c

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Total Clients</div>
      <div class="kpi-value">{_total_c or '—'}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Completed</div>
      <div class="kpi-value">{_complete_c or '—'}</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">In Progress</div>
      <div class="kpi-value">{_inprog_c or '—'}</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Intents Available</div>
      <div class="kpi-value">{len(INTENTS)}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Manifest & diff table helpers ─────────────────────────────────────────────

def _manifest_table(answers: dict, questions: list) -> str:
    rows = "".join(
        f"<tr><td><strong>{q['label']}</strong></td>"
        f"<td>{answers.get(q['key'],'—')}</td></tr>"
        for q in questions
    )
    return (f'<table class="manifest-table">'
            f"<tr><th>Field</th><th>Value</th></tr>{rows}</table>")

def _diff_table(old: dict, new: dict, questions: list) -> str:
    rows = []
    for q in questions:
        ov = old.get(q["key"],""); nv = new.get(q["key"],"")
        css = "diff-added" if not ov and nv else ("diff-changed" if ov!=nv else "")
        rows.append(f'<tr class="{css}"><td><strong>{q["label"]}</strong></td>'
                    f"<td>{ov or '—'}</td><td>{nv or '—'}</td></tr>")
    return (f'<table class="manifest-table">'
            f"<tr><th>Field</th><th>Previous</th><th>Current</th></tr>"
            + "".join(rows) + "</table>")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CLIENT CATALOG
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">👥 Client Catalog</div>', unsafe_allow_html=True)
st.markdown("")

_btn_col, _ = st.columns([2.8, 4.2])
with _btn_col:
    if st.button("🚀 Start New Client Onboarding", type="primary",
                 use_container_width=True, key="dash_new_ob"):
        reset_session()
        st.session_state.chat_open      = True
        st.session_state.chat_maximized = False
        st.rerun()

st.markdown("")

_STATUS_MAP = {
    "finalized":     ("badge-complete",    "Complete ✅"),
    "review":        ("badge-review",      "Review"),
    "collecting":    ("badge-inprogress",  "Collecting"),
    "client_name":   ("badge-started",     "Starting"),
    "intent_select": ("badge-started",     "Intent Select"),
    "mode_select":   ("badge-started",     "Mode Select"),
    "greeting":      ("badge-started",     "Started"),
}

if not _clients_reg:
    st.info("No clients yet — click **Start New Client Onboarding** to begin.", icon="ℹ️")
else:
    _hdr = st.columns([2.5, 2.8, 1.6, 0.7, 1.8, 1.4])
    for _col, _lbl in zip(_hdr, ["Client / Company", "Intent", "Status",
                                  "Ver", "Last Updated", "Action"]):
        _col.markdown(f"<small><b>{_lbl}</b></small>", unsafe_allow_html=True)
    st.divider()
    for _cname, _rec in _clients_reg.items():
        _c = st.columns([2.5, 2.8, 1.6, 0.7, 1.8, 1.4])
        _c[0].markdown(f"**{_cname}**")
        _c[1].write(_rec["intent"] if _rec["intent"] != "—" else "—")
        _bcls, _blbl = _STATUS_MAP.get(_rec["step"], ("badge-started", _rec["step"].title()))
        _c[2].markdown(f'<span class="badge {_bcls}">{_blbl}</span>',
                       unsafe_allow_html=True)
        _c[3].write(str(_rec["version"]) if _rec["version"] else "—")
        _c[4].write(_rec["updated_at"])
        if _c[5].button("💬 Chat", key=f"cat_{_cname}", use_container_width=True):
            load_client(_cname, _rec)
            st.session_state.chat_open      = True
            st.session_state.chat_maximized = False
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INTENT CATALOG
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📋 Intent Catalog</div>', unsafe_allow_html=True)
st.markdown("")

_icols = st.columns(len(INTENTS))
for _icol, (_ik, _iv) in zip(_icols, INTENTS.items()):
    _n = len(_iv["questions"])
    with _icol:
        st.markdown(f"""<div class="kpi-card" style="min-height:118px">
          <div class="kpi-label">{_ik}</div>
          <div style="font-weight:700;font-size:.9rem;margin:.35rem 0 .25rem;color:#1e3a8a">
            {_iv['label'].split('—',1)[-1].strip()}</div>
          <div style="font-size:.78rem;color:#64748b;line-height:1.4">{_iv['description']}</div>
          <div style="margin-top:.45rem;font-size:.77rem;color:#3b82f6;font-weight:600">
            {_n} field{'s' if _n != 1 else ''}</div>
        </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CURRENT ONBOARDING SESSION (only when active)
# ═════════════════════════════════════════════════════════════════════════════
if _company and step not in ("greeting", "client_name", "intent_select", "mode_select"):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔄 Current Onboarding Session</div>',
                unsafe_allow_html=True)
    st.markdown("")
    _questions = (INTENTS[st.session_state.selected_intent]["questions"]
                  if st.session_state.selected_intent else [])
    _answers   = st.session_state.answers

    if step == "collecting":
        _answered = sum(1 for q in _questions
                        if str(_answers.get(q["key"], "")).strip())
        _fill_pct = int(_answered / len(_questions) * 100) if _questions else 0
        st.progress(_fill_pct / 100)
        st.caption(f"{_answered} of {len(_questions)} fields filled — {_fill_pct}%")
        st.markdown("")
        _rows = "".join(
            f"<tr><td><strong>{q['label']}</strong></td>"
            f"<td>{_answers.get(q['key']) or '<span style=\"color:#94a3b8\">—</span>'}</td></tr>"
            for q in _questions
        )
        st.markdown(
            f'<table class="manifest-table"><tr><th>Field</th><th>Value</th></tr>{_rows}</table>',
            unsafe_allow_html=True)
        st.caption("Answers appear here as you fill them in the chat panel →")

    elif step == "review":
        _versions = st.session_state.manifest_versions
        _ver_num  = st.session_state.manifest_version
        if len(_versions) >= 2:
            st.markdown(f"**Changes — v{_ver_num-1} → v{_ver_num}**")
            st.markdown(_diff_table(_versions[-2], _versions[-1], _questions),
                        unsafe_allow_html=True)
            st.markdown("")
        st.markdown(f"**Manifest Summary  (v{_ver_num})**")
        st.markdown(_manifest_table(_answers, _questions), unsafe_allow_html=True)
        st.caption("Confirm or edit using the **chat panel** →")

    elif step == "finalized":
        _ver_num   = st.session_state.manifest_version
        _iname     = st.session_state.selected_intent or ""
        _safe_name = _company.replace(" ", "_")
        st.success(f"🎉 **Onboarding Complete!**  {_company}  ·  {_iname}  ·  v{_ver_num}")
        st.markdown(f"**Final Manifest  (v{_ver_num})**")
        st.markdown(_manifest_table(_answers, _questions), unsafe_allow_html=True)
        st.markdown("**Download Final Manifest**")
        _fc1, _fc2, _fc3 = st.columns(3)
        with _fc1:
            st.download_button("⬇ Excel (.xlsx)",
                data=generate_excel(_answers, _questions, _iname, _ver_num),
                file_name=f"manifest_{_safe_name}_v{_ver_num}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with _fc2:
            st.download_button("⬇ Word (.docx)",
                data=generate_docx(_answers, _questions, _iname, _ver_num),
                file_name=f"manifest_{_safe_name}_v{_ver_num}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True)
        with _fc3:
            st.download_button("⬇ Text (.txt)",
                data=generate_txt(_answers, _questions, _iname, _ver_num),
                file_name=f"manifest_{_safe_name}_v{_ver_num}.txt",
                mime="text/plain", use_container_width=True)
        if len(st.session_state.manifest_versions) > 1:
            with st.expander(
                    f"📚 Version History ({len(st.session_state.manifest_versions)} versions)"):
                for _i, _v in enumerate(st.session_state.manifest_versions, 1):
                    st.markdown(f"**Version {_i}**")
                    st.markdown(_manifest_table(_v, _questions), unsafe_allow_html=True)
                    st.markdown("")
