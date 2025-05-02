import streamlit as st

st.set_page_config(page_title="🏡 Real Estate Assistant", layout="wide")
st.title("🏡 Estate Wise")

option = st.selectbox("Choose input method", ["-- Select --", "Text Input", "Speech Input"])

if option == "Text Input":
    st.switch_page("pages/text_input.py")
elif option == "Speech Input":
    st.switch_page("pages/speech_input.py")

