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
import streamlit.components.v1 as components
# --- DATA FETCHING ---
@st.cache_data(ttl=300)
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
def get_file_content(file_id):
    """HTML tartalom letöltése a Drive-ról"""
    service = init_drive_service()
    try:
        # get_media letölti a fájl tartalmát
        content = service.files().get_media(fileId=file_id).execute()
        return content.decode('utf-8')
    except Exception as e:
        return f"<h1>Hiba a fájl betöltésekor: {e}</h1>"
# --- UI LOGIC ---
def main():
    st.title("📊 MBO Trading Reports")
    
    # Állapotkezelés a navigációhoz
    if 'current_folder_id' not in st.session_state:
        st.session_state.current_folder_id = ROOT_FOLDER_ID
        st.session_state.folder_stack = [("Home", ROOT_FOLDER_ID)]
    
    # Ha van kiválasztott jelentés (amit megtekintünk)
    if 'selected_report' in st.session_state and st.session_state.selected_report:
        report_id = st.session_state.selected_report
        
        # Gomb a visszalépéshez a listához
        if st.button("⬅️ Vissza a listához"):
            del st.session_state.selected_report
            st.rerun()
            
        with st.spinner('Jelentés betöltése...'):
            html_content = get_file_content(report_id)
            # HTML megjelenítése Iframe-ben
            components.html(html_content, height=1000, scrolling=True)
            
        return # Kilépés, hogy ne rajzolja ki a mappákat alá
    # --- LISTA NÉZET (Ha nincs jelentés megnyitva) ---
    # Navigációs sáv (Vissza a szülő mappába)
    if len(st.session_state.folder_stack) > 1:
        if st.button("⬅️ Vissza (fel)", key="back_nav"):
            st.session_state.folder_stack.pop()
            st.session_state.current_folder_id = st.session_state.folder_stack[-1][1]
            st.rerun()
            
    # Aktuális mappa tartalmának lekérése
    current_id = st.session_state.current_folder_id
    
    # DEBUG: Kiírjuk az ID-t, hogy lássuk, jót keres-e
    # st.write(f"Keresés ebben a mappában: {current_id}") 
    
    folders, reports = get_children(current_id)
    
    if not folders and not reports:
        st.warning(f"Ez a mappa üres, vagy nem sikerült elérni a Drive-ot. (Mappa ID: {current_id})")
        st.info("Ellenőrizd: 1. A 'secrets' beállítást. 2. Hogy a Service Account hozzá van-e adva ehhez a mappához a Drive-on.")
    
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
            # Egy sorban a név és a gombok
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"📄 **{report['name']}**")
            with col2:
                # Megtekintés gomb
                if st.button("Megnyitás", key=f"view_{report['id']}"):
                    st.session_state.selected_report = report['id']
                    st.rerun()
