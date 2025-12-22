import streamlit as st
import streamlit.components.v1 as components
import utils
# KONFIGURÁCIÓ
ROOT_FOLDER_ID = "1XZ4ZkFzVP2eHouy6CweJI6Hx1fGAF51m"
st.set_page_config(page_title="Riportok", page_icon="📂", layout="wide")
utils.set_design()
st.title("📂 Riportok Böngészése")
if 'rep_folder_id' not in st.session_state:
    st.session_state.rep_folder_id = ROOT_FOLDER_ID
    st.session_state.rep_stack = [("Home", ROOT_FOLDER_ID)]
# Riport nézet
if 'view_report_id' in st.session_state:
    if st.button("⬅️ Vissza a listához"):
        del st.session_state.view_report_id
        st.rerun()
    html_content = utils.get_file_content(st.session_state.view_report_id)
    components.html(html_content, height=1000, scrolling=True)
else:
    # Lista nézet - Vissza gomb
    if len(st.session_state.rep_stack) > 1:
        if st.button("⬅️ Vissza"):
            st.session_state.rep_stack.pop()
            st.session_state.rep_folder_id = st.session_state.rep_stack[-1][1]
            st.rerun()
    # Tartalom betöltése
    current_id = st.session_state.rep_folder_id
    folders, reports = utils.get_children(current_id)
    if not folders and not reports:
        st.warning(f"Üres mappa vagy hiba. ID: {current_id}")
    # Mappák
    if folders:
        st.subheader("Mappák")
        cols = st.columns(3)
        for idx, folder in enumerate(folders):
             with cols[idx % 3]:
                if st.button(f"📁 {folder['name']}", key=folder['id'], use_container_width=True):
                    st.session_state.rep_folder_id = folder['id']
                    st.session_state.rep_stack.append((folder['name'], folder['id']))
                    st.rerun()
    
    # Fájlok
    if reports:
        st.subheader("Fájlok")
        for report in reports:
            col1, col2 = st.columns([0.8, 0.2])
            with col1: st.write(f"📄 **{report['name']}**")
            with col2:
                if st.button("Megnyitás", key=f"v_{report['id']}"):
                    st.session_state.view_report_id = report['id']
                    st.rerun()
