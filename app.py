import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MBO Web App",
    layout="centered"
)

# Simple Header
st.header("MBO Web Application")

# Introduction text (optional, keeping it minimal as requested)
st.write("Welcome to the application.")

# Open App Button
if st.button("Open App"):
    st.success("App Opened! (This is a placeholder action)")
    # Logic to open the main app or redirect would go here
