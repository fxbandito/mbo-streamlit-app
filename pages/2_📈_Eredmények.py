import streamlit as st
import streamlit.components.v1 as components
import utils
st.set_page_config(page_title="Eredmények", page_icon="📈", layout="wide")
utils.set_design()
st.title("📈 Eredmények és Statisztikák")
# Cseréld ki a saját Sheet URL-edre!
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR0OF5cHgusupJvTu0hfTRKvJ5CoguBvKurxHOF6GPCRcr6V5HMoOVwH2Erk1mFgiLWib32fRw6gq0M/pubhtml?widget=true&headers=false"
components.html(f"""
<iframe src="{SHEET_URL}" width="100%" height="800" frameborder="0" style="border-radius: 10px; background: rgba(255,255,255,0.05);"></iframe>
""", height=820)
