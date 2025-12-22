import streamlit as st
import utils
st.set_page_config(page_title="MBO Home", page_icon="🏠", layout="wide")
utils.set_design()
st.title("🏠 Üdvözöllek az MBO Rendszerben!")
st.markdown("""
### Válassz a bal oldali menüből:
*   **📂 Riportok**: A korábbi fájlböngésző, ahol a 'Reports_category' mappában navigálhatsz.
*   **📈 Eredmények**: A Google Sheet táblázatok megtekintése.
*   **📘 Model Help**: Segítség és leírások (`Model Help` mappa).
*   **🧠 Stratégia Elemző**: Képek és elemzések galériája.
*   **🚀 App Start**: (Hamarosan) Az éles program indítása.
""")
st.info("👈 Kattints balra a menüben a kívánt funkcióhoz!")
