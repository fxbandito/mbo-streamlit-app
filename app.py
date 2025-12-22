import streamlit as st
import streamlit.components.v1 as components
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
# --- 1. KONFIGURÁCIÓ (CSAK EZT SZERKESZD!) ---
ROOT_FOLDER_ID = "1XZ4ZkFzVP2eHouy6CweJI6Hx1fGAF51m"  # <--- ITT CSERÉLD KI A SAJÁT DRIVE MAPPA ID-RA!
# --- 2. PAGE SETUP ---
st.set_page_config(page_title="MBO Reports", page_icon="📊", layout="wide")
# Egyedi CSS (Sötét Design)
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #e4e4e4; }
    h1, h2, h3, p, div { color: #e4e4e4 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .stButton>button, .streamlit-expanderHeader { 
        background: rgba(255, 255, 255, 0.05) !important; 
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)
# --- 3. GOOGLE DRIVE KAPCSOLAT (CLOUD) ---
@st.cache_resource
def init_drive_service():
    # Ellenőrizzük, hogy léteznek-e a titkos kulcsok a szerveren
    if "gcp_service_account" not in st.secrets:
        st.error("HIBA: Hiányoznak a titkos kulcsok (Secrets)!")
        st.info("Ez a kód csak a Streamlit Cloud-on fut helyesen, ha beállítottad a 'gcp_service_account' részt a Secrets menüben.")
        st.stop() # Megállítjuk a futást
        return None
    
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Hiba a hitelesítés során: {e}")
        return None
# --- 4. ADATOK LEKÉRÉSE ---
@st.cache_data(ttl=300)
def get_children(folder_id):
    service = init_drive_service()
    if not service: return [], []
    
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query, fields="files(id, name, mimeType, webViewLink)", orderBy="name"
        ).execute()
        files = results.get('files', [])
        
        folders = [f for f in files if f['mimeType'] == 'application/vnd.google-apps.folder']
        reports = [f for f in files if f['mimeType'] == 'text/html' or f['name'].endswith('.html')]
        return folders, reports
    except Exception as e:
        st.error(f"Hiba a mappa olvasásakor: {e}")
        st.warning(f"Ellenőrizd, hogy a megadott MAPPA ID ({folder_id}) helyes-e, és a Service Account hozzá van-e adva!")
        return [], []
def get_file_content(file_id):
    service = init_drive_service()
    try:
        content = service.files().get_media(fileId=file_id).execute()
        return content.decode('utf-8')
    except Exception as e:
        return f"<h1>Hiba a fájl megnyitásakor: {e}</h1>"
# --- 5. FŐPROGRAM (UI) ---
def main():
    st.title("📊 MBO Trading Reports")
    if 'current_folder_id' not in st.session_state:
        st.session_state.current_folder_id = ROOT_FOLDER_ID
        st.session_state.folder_stack = [("Home", ROOT_FOLDER_ID)]
    # Ha riportot nézünk
    if 'selected_report' in st.session_state:
        if st.button("⬅️ Vissza a listához"):
            del st.session_state.selected_report
            st.rerun()
        html_content = get_file_content(st.session_state.selected_report)
        components.html(html_content, height=1000, scrolling=True)
        return
    # LISTA NÉZET
    if len(st.session_state.folder_stack) > 1:
        if st.button("⬅️ Vissza"):
            st.session_state.folder_stack.pop()
            st.session_state.current_folder_id = st.session_state.folder_stack[-1][1]
            st.rerun()
    current_id = st.session_state.current_folder_id
    folders, reports = get_children(current_id)
    # Üres mappa ellenőrzés
    if not folders and not reports:
        if current_id == "IDE_MASOLD_A_MAPPA_ID_T":
             st.warning("⚠️ FIGYELEM: Még nem állítottad be a 'ROOT_FOLDER_ID'-t a kódban!")
        else:
             st.info("Ez a mappa üres.")
    # Kirajzolás
    if folders:
        st.subheader("Mappák")
        cols = st.columns(3)
        for idx, folder in enumerate(folders):
            with cols[idx % 3]:
                if st.button(f"📁 {folder['name']}", key=folder['id'], use_container_width=True):
                    st.session_state.current_folder_id = folder['id']
                    st.session_state.folder_stack.append((folder['name'], folder['id']))
                    st.rerun()
                    
    if reports:
        st.subheader("Jelentések")
        for report in reports:
            col1, col2 = st.columns([0.8, 0.2])
            with col1: st.write(f"📄 **{report['name']}**")
            with col2:
                if st.button("Megnyitás", key=f"view_{report['id']}"):
                    st.session_state.selected_report = report['id']
                    st.rerun()
# GOOGLE SHEET BEÁGYAZÁS (Csak olvasható)
st.subheader("📈 Statisztikák")
# Iframe beágyazása
components.html(f"""
<iframe 
    src="https://docs.google.com/spreadsheets/d/e/2PACX-1vR0OF5cHgusupJvTu0hfTRKvJ5CoguBvKurxHOF6GPCRcr6V5HMoOVwH2Erk1mFgiLWib32fRw6gq0M/pubhtml?widget=true&amp;headers=false"
    width="100%" 
    height="600" 
    frameborder="0" 
    style="border-radius: 10px; background: rgba(255,255,255,0.05);">
</iframe>
""", height=620)
if __name__ == "__main__":
    main()
