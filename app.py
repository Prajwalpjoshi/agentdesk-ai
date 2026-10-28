import html
from datetime import datetime

import streamlit as st
from pydantic import ValidationError

from agent import AgentDesk
from schemas import TicketRequest
from tools import check_service_status


st.set_page_config(
    page_title="AgentDesk AI",
    page_icon="🤖",
    layout="wide",
)

CATEGORIES = ["Authentication", "API Access", "Service Outage", "General IT"]
PRIORITIES = ["Low", "Medium", "High"]

FIELD_LABELS = {
    "requester": "Your name",
    "title": "Issue title",
    "description": "Issue description",
    "category": "Category",
    "priority": "Priority",
}

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --primary: #2563EB; --primary-light: #DBEAFE;
    --success: #10B981; --warning: #F59E0B; --danger: #EF4444;
    --bg: #F8FAFC; --surface: #FFFFFF; --border: #E2E8F0;
    --text: #0F172A; --muted: #64748B;
}

/* Set the font on containers only; a blanket [class*="st-"] rule also hits
   Material Symbols spans and turns icon ligatures into raw text. */
.stApp, .stApp button, .stApp input, .stApp textarea {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}
.stApp { background: var(--bg); }
.block-container { padding-top: 5.25rem;  /* clears the 60px sticky header */ padding-bottom: 5rem; max-width: 1100px; }
#MainMenu, footer { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
.sidebar-note { font-size: 12px; color: var(--muted); line-height: 1.5; }

/* Page header */
.page-title { font-size: 30px; font-weight: 700; color: var(--text); margin: 0; line-height: 1.2; }
.page-desc { font-size: 15px; color: var(--muted); margin: 6px 0 20px; }

/* Cards */
.card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 20px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); margin-bottom: 12px;
}
.card-title { font-size: 18px; font-weight: 600; color: var(--text); margin: 0 0 4px; }
.card-text { font-size: 14px; color: var(--muted); margin: 10px 0 0; }
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 999px;
    font-size: 12px; font-weight: 600;
}
.badge.ok { background: #D1FAE5; color: #047857; }
.badge.warn { background: #FEF3C7; color: #B45309; }
.badge.down { background: #FEE2E2; color: #B91C1C; }
.card-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.card.ok { border-top: 3px solid var(--success); }
.card.warn { border-top: 3px solid var(--warning); }
.card.down { border-top: 3px solid var(--danger); }

.svc-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.svc-table th {
    text-align: left; font-size: 12px; color: var(--muted); font-weight: 600;
    padding: 10px 12px; border-bottom: 1px solid var(--border); background: var(--bg);
}
.svc-table td { padding: 12px; border-bottom: 1px solid var(--border); color: var(--text); }
.svc-table tr:last-child td { border-bottom: none; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 14px;
    background: var(--surface); }

.receipt-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-top: 14px; }
.receipt-label { font-size: 12px; color: var(--muted); }
.receipt-value { font-size: 15px; font-weight: 600; color: var(--text); word-break: break-word; }

/* Native widgets */
.stButton > button, .stFormSubmitButton > button {
    height: 44px; border-radius: 10px; font-weight: 600; border: 1px solid var(--border);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: var(--primary); border-color: var(--primary); color: #fff;
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
    background: #1D4ED8; border-color: #1D4ED8;
}
[data-testid="stForm"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 24px;
}
[data-testid="stChatMessage"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 14px 16px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--primary-light); border-color: #BFDBFE;
}
[data-testid="stExpander"] { border-radius: 10px; background: var(--bg); }

@media (max-width: 768px) {
    .block-container { padding-left: 16px; padding-right: 16px; }
    .page-title { font-size: 24px; }
}
@media (max-width: 640px) {
    .block-container { padding-top: 1rem; }
}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)


@st.cache_resource
def get_agent():
    return AgentDesk()


def page_header(title: str, description: str) -> None:
    st.markdown(
        f'<h1 class="page-title">{html.escape(title)}</h1>'
        f'<p class="page-desc">{html.escape(description)}</p>',
        unsafe_allow_html=True,
    )


try:
    agent = get_agent()
except Exception as exc:
    st.error(f"Could not initialize the AI agent: {exc}")
    st.stop()


# ---------------------------------------------------------------- Chat
def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        render_sources(message.get("sources"))


def render_sources(sources) -> None:
    if sources:
        with st.expander(f"📖 Knowledge Base Sources ({len(sources)})"):
            for source in sources:
                st.markdown(f"- `{source}`")


SUGGESTIONS = [
    "What should I check when an API returns HTTP 403?",
    "How do I troubleshoot an SSO login issue?",
    "How do I fix a database connection error?",
]


def start_new_chat() -> None:
    """Clear only the conversation state; tickets and other state stay."""
    for key in ("chat_history", "pending_question"):
        st.session_state.pop(key, None)
    st.session_state.chat_history = []


def ask_suggestion(text: str) -> None:
    st.session_state.pending_question = text


def chat_page() -> None:
    head, action = st.columns([4, 1], vertical_alignment="top")
    with head:
        page_header(
            "AI Support Chat",
            "Get help with API access, authentication, HTTP errors, SSO, "
            "and more using our knowledge base.",
        )
    with action:
        st.button(
            "New Chat", type="primary", icon=":material/add:",
            use_container_width=True, on_click=start_new_chat,
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history and not st.session_state.get(
            "pending_question"):
        st.caption("Try a suggested question or type your own below:")
        for text in SUGGESTIONS:
            st.button(
                text, key=f"sugg_{text}", icon=":material/chat_bubble:",
                on_click=ask_suggestion, args=(text,),
            )

    for message in st.session_state.chat_history:
        render_message(message)

    question = st.chat_input(
        'Describe your IT issue... (e.g., "API 403", "SSO login")'
    ) or st.session_state.pop("pending_question", None)
    if not question:
        return

    user_message = {"role": "user", "content": question}
    st.session_state.chat_history.append(user_message)
    render_message(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Searching documentation and generating an answer..."):
            try:
                result = agent.answer_question(question)
            except Exception as exc:
                st.error(
                    "The AI request failed. Please try again in a moment."
                )
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")
                return
        st.markdown(result.answer)
        render_sources(result.sources)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result.answer,
        "sources": result.sources,
    })


# ------------------------------------------------------------- Health
STATUS_CLASS = {"operational": "ok", "degraded": "warn", "down": "down"}


def health_page() -> None:
    head, action = st.columns([4, 1], vertical_alignment="top")
    with head:
        page_header(
            "Service Health",
            "Status of core services (simulated demo data).",
        )
    with action:
        if st.button("Refresh", type="primary", icon=":material/refresh:", use_container_width=True):
            st.rerun()

    st.info(
        "Service statuses are simulated for demonstration purposes and are "
        "not connected to any production monitoring system."
    )

    services = check_service_status("all")["services"]
    checked = datetime.now().strftime("%b %d, %Y %H:%M")

    cols = st.columns(len(services))
    for col, (name, details) in zip(cols, services.items()):
        status = details["status"]
        css = STATUS_CLASS.get(status, "warn")
        label = "API" if name == "api" else name.title()
        with col:
            st.markdown(
                f'<div class="card {css}"><div class="card-head">'
                f'<div class="card-title">{html.escape(label)}</div>'
                f'<span class="badge {css}">{html.escape(status.title())}</span>'
                f'</div><p class="card-text">'
                f'{html.escape(details["message"])}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">Service Details</div>', unsafe_allow_html=True)
    rows = "".join(
        f"<tr><td>{html.escape('API' if n == 'api' else n.title())}</td>"
        f'<td><span class="badge {STATUS_CLASS.get(d["status"], "warn")}">'
        f'{html.escape(d["status"].title())}</span></td>'
        f'<td>{html.escape(d["message"])}</td><td>{checked}</td></tr>'
        for n, d in services.items()
    )
    st.markdown(
        '<div class="table-wrap"><table class="svc-table"><thead><tr>'
        "<th>Service</th><th>Status</th><th>Message</th><th>Last refreshed</th>"
        f"</tr></thead><tbody>{rows}</tbody></table></div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------- Ticket
def reset_ticket_form() -> None:
    st.session_state.t_requester = ""
    st.session_state.t_title = ""
    st.session_state.t_description = ""
    st.session_state.t_category = CATEGORIES[0]
    st.session_state.t_priority = "Medium"
    st.session_state.pop("ticket_result", None)
    st.session_state.pop("ticket_errors", None)


def ticket_page() -> None:
    page_header(
        "Create Support Ticket",
        "Submit a new IT support request.",
    )

    for key, default in {
        "t_requester": "", "t_title": "", "t_description": "",
        "t_category": CATEGORIES[0], "t_priority": "Medium",
    }.items():
        st.session_state.setdefault(key, default)

    form_col, tips_col = st.columns([2, 1])

    with form_col:
        with st.form("ticket_form"):
            st.text_input(
                "Your name *", key="t_requester",
                placeholder="Enter your name",
            )
            st.text_input(
                "Issue title *", key="t_title",
                placeholder="Brief description of the issue",
                help="5–120 characters.",
            )
            st.text_area(
                "Describe the issue *", key="t_description", height=150,
                placeholder="Include any error messages, steps to reproduce, "
                            "and expected behavior.",
                help="10–1000 characters.",
            )
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("Category *", CATEGORIES, key="t_category")
            with c2:
                st.selectbox("Priority *", PRIORITIES, key="t_priority")

            b1, b2, _ = st.columns([2, 1, 2])
            submitted = b1.form_submit_button(
                "Create Ticket", type="primary", use_container_width=True
            )
            b2.form_submit_button(
                "Clear", on_click=reset_ticket_form, use_container_width=True
            )

        if submitted:
            ticket_data = {
                "requester": st.session_state.t_requester,
                "title": st.session_state.t_title,
                "description": st.session_state.t_description,
                "category": st.session_state.t_category,
                "priority": st.session_state.t_priority,
            }
            try:
                TicketRequest.model_validate(ticket_data)
            except ValidationError as exc:
                st.session_state.ticket_errors = exc.errors(include_input=False)
                st.session_state.pop("ticket_result", None)
            else:
                response = agent.submit_ticket(ticket_data)
                st.session_state.pop("ticket_errors", None)
                if response.ticket_id:
                    st.session_state.ticket_result = {
                        "id": response.ticket_id,
                        "title": ticket_data["title"].strip(),
                        "priority": ticket_data["priority"],
                        "status": "Open",
                    }
                else:
                    st.session_state.ticket_errors = [
                        {"loc": ("ticket",), "msg": response.answer}
                    ]

        errors = st.session_state.get("ticket_errors")
        if errors:
            lines = []
            for err in errors:
                field = str(err["loc"][0]) if err.get("loc") else "ticket"
                lines.append(
                    f"- **{FIELD_LABELS.get(field, field)}**: {err['msg']}"
                )
            st.error("Please fix the following:\n\n" + "\n".join(lines))

        ticket = st.session_state.get("ticket_result")
        if ticket:
            st.markdown(
                '<div class="card ok"><div class="card-head">'
                '<div class="card-title">✅ Ticket created successfully</div>'
                '<span class="badge ok">Open</span></div>'
                '<div class="receipt-grid">'
                f'<div><div class="receipt-label">Incident ID</div>'
                f'<div class="receipt-value">{html.escape(ticket["id"])}</div></div>'
                f'<div><div class="receipt-label">Title</div>'
                f'<div class="receipt-value">{html.escape(ticket["title"])}</div></div>'
                f'<div><div class="receipt-label">Priority</div>'
                f'<div class="receipt-value">{html.escape(ticket["priority"])}</div></div>'
                f'<div><div class="receipt-label">Status</div>'
                f'<div class="receipt-value">{html.escape(ticket["status"])}</div></div>'
                "</div></div>",
                unsafe_allow_html=True,
            )

    with tips_col:
        st.markdown(
            '<div class="card"><div class="card-title">💡 Before submitting</div>'
            '<ul class="card-text" style="padding-left:18px;line-height:1.7">'
            "<li>Search the knowledge base first</li>"
            "<li>Provide clear and detailed information</li>"
            "<li>Include error messages and timestamps</li>"
            "<li>Mention the environment (e.g., UAT, PROD)</li>"
            "</ul></div>",
            unsafe_allow_html=True,
        )


PAGE_OBJECTS = [
    st.Page(chat_page, title="AI Support Chat", icon=":material/chat:",
            url_path="chat", default=True),
    st.Page(health_page, title="Service Health", icon=":material/monitor_heart:",
            url_path="health"),
    st.Page(ticket_page, title="Create Ticket", icon=":material/confirmation_number:",
            url_path="ticket"),
]


st.logo("assets/logo.svg", size="large")

with st.sidebar:
    st.markdown(
        f'<div class="sidebar-note">Model: {html.escape(str(agent.model))}<br>'
        "Demo project — service status is simulated.</div>",
        unsafe_allow_html=True,
    )


st.navigation(PAGE_OBJECTS).run()
