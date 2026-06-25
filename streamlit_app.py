# streamlit_app.py
import uuid
import json
import streamlit as st

from app.database.connection import SessionLocal
from app.database.repository import (
    get_or_create_session,
    get_all_sessions_for_user,
    get_latest_proposal_record,
    get_client_profile,
    get_messages,
    delete_session,
)

from app.services.proposal_service import (
    generate_proposal,
)
from app.services.qa_service import (
    answer_question,
)
from app.services.revision_service import (
    revise_proposal,
)

# Optional
try:
    from app.tools.docx_tool import (
        generate_proposal_docx,
    )
except Exception:
    generate_proposal_docx = None


# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Proposal Generator AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------
# SESSION STATE
# -----------------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = "consultant_1"

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "active_session_user_id" not in st.session_state:
    st.session_state.active_session_user_id = ""

if "proposal" not in st.session_state:
    st.session_state.proposal = None

if "profile" not in st.session_state:
    st.session_state.profile = None

if "docx_path" not in st.session_state:
    st.session_state.docx_path = None


# -----------------------------------
# HELPERS
# -----------------------------------

def get_db():
    return SessionLocal()


# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title(
    "📄 Proposal Generator AI"
)

# User ID Management
user_id_input = st.sidebar.text_input("User ID", value=st.session_state.user_id)
if user_id_input != st.session_state.user_id:
    st.session_state.user_id = user_id_input
    st.session_state.active_session_id = None
    st.session_state.active_session_user_id = ""
    st.session_state.proposal = None
    st.session_state.profile = None
    st.session_state.docx_path = None
    st.rerun()

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Generate Proposal",
        "Revise Proposal",
        "Q&A",
    ],
)

st.sidebar.divider()

# Load user's sessions from DB
db = get_db()
try:
    user_sessions = get_all_sessions_for_user(db, st.session_state.user_id)
finally:
    db.close()

# If no sessions exist for this user, create a new one automatically
if not user_sessions and not st.session_state.active_session_id:
    db = get_db()
    try:
        new_slack_user_id = f"{st.session_state.user_id}:{uuid.uuid4()}"
        session = get_or_create_session(db, slack_user_id=new_slack_user_id)
        st.session_state.active_session_id = session.id
        st.session_state.active_session_user_id = new_slack_user_id
    finally:
        db.close()
    st.rerun()

# Build session options
session_options = []
session_id_to_label = {}
label_to_session = {}

for s in user_sessions:
    display_suffix = s.slack_user_id.split(":")[-1] if ":" in s.slack_user_id else s.slack_user_id
    label = f"Session {s.id} ({display_suffix[:8]})"
    session_options.append(label)
    session_id_to_label[s.id] = label
    label_to_session[label] = s

session_options.append("➕ Create New Session")

# Determine selected session index
current_index = 0
if st.session_state.active_session_id in session_id_to_label:
    current_label = session_id_to_label[st.session_state.active_session_id]
    if current_label in session_options:
        current_index = session_options.index(current_label)

selected_label = st.sidebar.selectbox("Active Session", options=session_options, index=current_index)

if selected_label == "➕ Create New Session":
    if st.sidebar.button("Confirm Create New Session"):
        db = get_db()
        try:
            new_slack_user_id = f"{st.session_state.user_id}:{uuid.uuid4()}"
            session = get_or_create_session(db, slack_user_id=new_slack_user_id)
            st.session_state.active_session_id = session.id
            st.session_state.active_session_user_id = new_slack_user_id
            st.session_state.proposal = None
            st.session_state.profile = None
            st.session_state.docx_path = None
        finally:
            db.close()
        st.success("New session created!")
        st.rerun()
else:
    selected_session = label_to_session[selected_label]
    if st.session_state.active_session_id != selected_session.id:
        st.session_state.active_session_id = selected_session.id
        st.session_state.active_session_user_id = selected_session.slack_user_id
        # Hydrate session state from DB
        db = get_db()
        try:
            proposal_record = get_latest_proposal_record(db, selected_session.id)
            profile_record = get_client_profile(db, selected_session.id)
            st.session_state.proposal = json.loads(proposal_record.proposal_json) if proposal_record else None
            st.session_state.docx_path = proposal_record.docx_path if proposal_record else None
            st.session_state.profile = profile_record if profile_record else None
        finally:
            db.close()
        st.rerun()

    # Session Deletion Option in sidebar
    if st.sidebar.button("🗑️ Delete Session", use_container_width=True, type="secondary"):
        db = get_db()
        try:
            delete_session(db, selected_session.id)
            st.sidebar.success(f"Session {selected_session.id} deleted.")
            # Reset active session state
            st.session_state.active_session_id = None
            st.session_state.active_session_user_id = ""
            st.session_state.proposal = None
            st.session_state.profile = None
            st.session_state.docx_path = None
        finally:
            db.close()
        st.rerun()


# ===================================
# GENERATE PROPOSAL
# ===================================

if page == "Generate Proposal":

    st.title(
        "📄 Generate Proposal"
    )

    uploaded_file = st.file_uploader(
        "Upload Transcript",
        type=[
            "txt",
        ],
    )

    transcript = ""

    if uploaded_file:

        transcript = (
            uploaded_file.read()
            .decode("utf-8")
        )

        st.success(
            "Transcript loaded"
        )

    transcript = st.text_area(
        "Transcript",
        value=transcript,
        height=300,
    )

    if st.button(
        "Generate Proposal",
        use_container_width=True,
    ):

        if not transcript.strip():

            st.warning(
                "Please provide transcript."
            )

            st.stop()

        db = get_db()

        try:

            with st.status(
                "Generating proposal...",
                expanded=True,
            ) as status:

                st.write(
                    "Running LangGraph workflow..."
                )

                result = generate_proposal(
                    db=db,
                    session_id=st.session_state.active_session_id,
                    slack_user_id=st.session_state.active_session_user_id,
                    channel_id="streamlit_channel",
                    transcript=transcript,
                )

                status.update(
                    label=
                    "Proposal generated",
                    state=
                    "complete",
                )

            st.session_state.proposal = (
                result.get(
                    "proposal_sections"
                )
            )

            st.session_state.profile = (
                result.get(
                    "client_profile"
                )
            )

            st.session_state.docx_path = (
                result.get(
                    "docx_path"
                )
            )

            st.success(
                "Proposal generated successfully"
            )

        finally:
            db.close()

    if st.session_state.profile:

        st.subheader(
            "Client Profile"
        )

        st.json(
            st.session_state.profile
        )

    if st.session_state.proposal:

        st.subheader(
            "Proposal Sections"
        )

        proposal = (
            st.session_state.proposal
        )

        if isinstance(
            proposal,
            dict,
        ):

            for section, content in (
                proposal.items()
            ):

                with st.expander(
                    section.replace("_", " ").title(),
                    expanded=False,
                ):
                    st.write(content)

        else:
            st.write(proposal)

        docx_path = st.session_state.docx_path
        if not docx_path and generate_proposal_docx:
            try:
                docx_path = (
                    generate_proposal_docx.invoke(
                        {
                            "proposal_sections":
                            proposal
                        }
                    )
                )
                st.session_state.docx_path = docx_path
            except Exception as e:
                st.error(
                    f"DOCX generation error: {e}"
                )

        if docx_path:
            try:
                with open(
                    docx_path,
                    "rb",
                ) as file:

                    st.download_button(
                        "⬇ Download DOCX",
                        data=file,
                        file_name=
                        "proposal.docx",
                        mime=
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

            except Exception as e:

                st.error(
                    f"DOCX download error: {e}"
                )


# ===================================
# REVISION
# ===================================

elif page == "Revise Proposal":

    st.title(
        "✏️ Revise Proposal"
    )

    revision_request = (
        st.text_area(
            "Revision Request",
            height=200,
        )
    )

    if st.button(
        "Revise Proposal",
        use_container_width=True,
    ):

        db = get_db()

        try:
            result = revise_proposal(
                db=db,
                session_id=st.session_state.active_session_id,
                slack_user_id=st.session_state.active_session_user_id,
                channel_id="streamlit_channel",
                revision_request=revision_request,
            )

            st.session_state.proposal = result.get("proposal_sections")
            st.session_state.docx_path = result.get("docx_path")

            st.success(
                "Revision completed"
            )

        finally:
            db.close()

    # If proposal exists, display it and offer download
    if st.session_state.proposal:
        st.subheader("Revised Proposal Sections")
        proposal = st.session_state.proposal
        if isinstance(proposal, dict):
            for section, content in proposal.items():
                with st.expander(section.replace("_", " ").title(), expanded=False):
                    st.write(content)
        else:
            st.write(proposal)

        docx_path = st.session_state.docx_path
        if docx_path:
            try:
                with open(docx_path, "rb") as file:
                    st.download_button(
                        "⬇ Download Revised DOCX",
                        data=file,
                        file_name="revised_proposal.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"DOCX download error: {e}")


# ===================================
# QA
# ===================================

elif page == "Q&A":

    st.title("❓ Ask Questions")

    db = get_db()
    try:
        # Load and display conversation history for the active session
        messages = get_messages(db, st.session_state.active_session_id)
        for msg in messages:
            with st.chat_message(msg.role):
                st.write(msg.content)
    finally:
        db.close()

    question = st.chat_input("Ask anything...")

    if question:
        # Display the user's message immediately
        with st.chat_message("user"):
            st.write(question)

        db = get_db()
        try:
            result = answer_question(
                db=db,
                session_id=st.session_state.active_session_id,
                slack_user_id=st.session_state.active_session_user_id,
                channel_id="streamlit_channel",
                user_question=question,
            )

            answer = result.get("answer", str(result))
            with st.chat_message("assistant"):
                st.write(answer)
        finally:
            db.close()
        
        # Rerun to reload message history and keep input clean
        st.rerun()


