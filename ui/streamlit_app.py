import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/enhance"

st.set_page_config(page_title="AI Content Enhancer", layout="wide")

st.title("AI Content Enhancer")

# Initialize session state
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""

col1, col2 = st.columns(2)

with col1:
    user_input = st.text_area(
        "Enter Content",
        height=350,
        placeholder="Write your content here..."
    )

with col2:
    st.text_area(
        "Preview",
        value=st.session_state.generated_content,
        height=350
    )

button_col1, button_col2, button_col3 = st.columns([3, 1, 1])

def generate_content(platform):
    payload = {
        "context": user_input,
        "platform": platform
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        st.session_state.generated_content = response.json()["enhanced_content"]
    else:
        st.error(response.text)

with button_col2:
    if st.button("Instagram"):
        generate_content("instagram")
        st.rerun()

with button_col3:
    if st.button("LinkedIn"):
        generate_content("linkedin")
        st.rerun()