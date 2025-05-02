import streamlit as st
import requests

st.title("💬 Text Input Mode")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for role, msg in st.session_state.chat_history:
    if role == 'user':
        st.markdown(
            f"""
            <div style='width: 100%; display: flex; justify-content: flex-end; margin: 8px 0;'>
                <div style='background-color: #d6d6d6; color: #000; 
                            padding: 10px 15px; border-radius: 15px 15px 0 15px; 
                            max-width: 70%; font-size: 15px; line-height: 1.4;'>
                    {msg}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='width: 100%; display: flex; justify-content: flex-start; margin: 8px 0;'>
                <div style='background-color: #2d2d2d; color: #fff; 
                            padding: 10px 15px; border-radius: 15px 15px 15px 0; 
                            max-width: 70%; font-size: 15px; line-height: 1.4;'>
                    {msg}
                </div>
            </div>
            """, unsafe_allow_html=True
        )


# Input form
with st.form("text_input_form"):
    user_input = st.text_input("Your message", placeholder="e.g., Show me 1 Kanal homes in DHA")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    try:
        response = requests.post(
            "http://localhost:8000/get_agent_response/",
            json={"file_path": user_input}
        )
        if response.status_code == 200:
            agent_msg = response.json().get("agent_response")
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("agent", agent_msg))
            st.rerun()
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"Connection error: {e}")

if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()
