import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
# --- KONFIGURÁCIÓ ---
# A mappád ID-ja (amit a címsorból másolsz ki)
ROOT_FOLDER_ID = "1XZ4ZkFzVP2eHouy6CweJI6Hx1fGAF51m"
# --- PAGE SETUP ---
st.set_page_config(
    page_title="MBO Reports",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Egyedi CSS a stílushoz (Sötét téma + Glassmorphism)
st.markdown("""
<style>
    /* Háttér */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Címsorok */
    h1, h2, h3 {
        color: #fff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Kártyák (Expander és egyéb dobozok) */
    .streamlit-expanderHeader, .stButton>button {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e4e4e4 !important;
        border-radius: 10px !important;
    }
    
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(52, 152, 219, 0.5) !important;
    }
    
    /* Szövegszín */
    .stMarkdown, p, div {
        color: #e4e4e4 !important;
    }
</style>
""", unsafe_allow_html=True)
# --- GOOGLE DRIVE AUTH ---
@st.cache_resource
def init_drive_service():
    """Hitelesítés a Streamlit Secrets-ből származó adatokkal."""
    if "gcp_service_account" not in st.secrets:
        st.error("Hiányzik a 'gcp_service_account' beállítás a Streamlit Secrets-ből!")
        return None
    
    # A secrets-ből dictionary-ként olvassuk ki
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=creds)
# --- DATA FETCHING ---
@st.cache_data(ttl=300) # 5 percenként frissít
def get_children(folder_id):
    service = init_drive_service()
    if not service: return [], []
    
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, webViewLink, iconLink)",
        orderBy="name"
    ).execute()
    
    files = results.get('files', [])
    
    folders_list = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.folder']
    reports_list = [f for f in files if f['mimeType'] == 'text/html' or f['name'].endswith('.html')]
    
    return folders_list, reports_list
# --- UI LOGIC ---
def main():
    st.title("📊 MBO Trading Reports")
    
    # Állapotkezelés a navigációhoz (breadcrumbs)
    if 'current_folder_id' not in st.session_state:
        st.session_state.current_folder_id = ROOT_FOLDER_ID
        st.session_state.folder_stack = [("Home", ROOT_FOLDER_ID)]
    # Navigációs sáv (Vissza gomb)
    if len(st.session_state.folder_stack) > 1:
        if st.button("⬅️ Vissza"):
            st.session_state.folder_stack.pop()
            st.session_state.current_folder_id = st.session_state.folder_stack[-1][1]
            st.rerun()
            
    # Aktuális mappa tartalmának lekérése
    current_id = st.session_state.current_folder_id
    folders, reports = get_children(current_id)
    
    # Mappák megjelenítése
    if folders:
        st.subheader("Mappák")
        cols = st.columns(3)
        for idx, folder in enumerate(folders):
            with cols[idx % 3]:
                if st.button(f"📁 {folder['name']}", key=folder['id'], use_container_width=True):
                    st.session_state.current_folder_id = folder['id']
                    st.session_state.folder_stack.append((folder['name'], folder['id']))
                    st.rerun()
    # Riportok megjelenítése
    if reports:
        st.subheader("Jelentések")
        for report in reports:
            # Expander kártya minden jelentéshez
            with st.expander(f"📄 {report['name']}"):
                st.write(f"ID: {report['id']}")
                # Két opció: Megnyitás Drive-on vagy Beágyazás (ha publikus/engedélyezett)
                st.link_button("Megnyitás Google Drive-on ↗️", report['webViewLink'])
                
                # Iframe beágyazás (Limitált: Csak ha a Drive fájl publikus, vagy trükközni kell a proxy-val)
                # Jelenleg a link a legbiztosabb megoldás auth nélkül.
                
if __name__ == "__main__":
    main()
