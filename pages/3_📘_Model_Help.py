import streamlit as st
import streamlit.components.v1 as components
import utils
# --- IDE ÍRD BE A MODEL HELP MAPPA ID-JÁT! ---
MODEL_HELP_ID = "1PhUnFMHMK9yRUhcWNiRg-z30IpwTrSpz" 
st.set_page_config(page_title="Model Help", page_icon="📘", layout="wide")
utils.set_design()
st.title("📘 Model Help Dokumentáció")
if 'help_folder_id' not in st.session_state:
    st.session_state.help_folder_id = MODEL_HELP_ID
# (Egyszerűsített böngésző logika, csak listázás)
folders, reports = utils.get_children(st.session_state.help_folder_id)
if reports:
    st.subheader("Dokumentumok")
    x = 0
    # Rács nézet a help fájlokhoz (opcionális, vagy lista)
    cols = st.columns(2) 
    for report in reports:
        with cols[x % 2]:
            with st.expander(f"📄 {report['name']}"):
                if st.button("Elolvas", key=f"help_{report['id']}"):
                    st.session_state.view_help_id = report['id']
                    st.rerun()
        x += 1
if 'view_help_id' in st.session_state:
    st.divider()
    st.subheader("Megtekintés")
    if st.button("Bezárás"):
        del st.session_state.view_help_id
        st.rerun()
    content = utils.get_file_content(st.session_state.view_help_id)
    components.html(content, height=800, scrolling=True)
