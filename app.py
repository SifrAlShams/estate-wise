import streamlit as st
import requests

st.set_page_config(page_title="🏡 Real Estate Assistant", layout="wide")

st.markdown(
    """
    <style>
    .user-msg, .agent-msg {
        padding: 0.75em 1em;
        border-radius: 12px;
        margin-bottom: 0.5em;
        width: fit-content;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 18px;
    }
    .user-msg {
        background-color: black;
        margin-left: auto;
        text-align: right;
    }
    .agent-msg {
        background-color: black;
        margin-right: auto;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏡 Estate Wise")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display history in scrollable container
with st.container():
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='agent-msg'>{msg}</div>", unsafe_allow_html=True)

# User input at bottom
with st.form(key="chat_form"):
    user_input = st.text_input("Your message", placeholder="e.g., Show me 1 Kanal homes in DHA", label_visibility="collapsed")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip() != "":
    # Call the backend
    try:
        response = requests.post(
            "http://localhost:8000/get_agent_response/",
            json={"file_path": user_input}
        )
        if response.status_code == 200:
            agent_msg = response.json().get("agent_response")
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("agent", agent_msg))
            st.rerun()  # refresh to show new messages immediately
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"Connection error: {e}")

# Optional Clear Button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()
