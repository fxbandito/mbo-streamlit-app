import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
@st.cache_resource
def init_drive_service():
    """Hitelesítés a Streamlit Secrets-ből."""
    if "gcp_service_account" not in st.secrets:
        st.error("HIBA: Hiányoznak a titkos kulcsok (Secrets)!")
        return None
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Hiba a hitelesítés során: {e}")
        return None
@st.cache_data(ttl=300)
def get_children(folder_id):
    """Mappa tartalmának lekérése."""
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
        return [], []
def get_file_content(file_id):
    """HTML tartalom letöltése."""
    service = init_drive_service()
    try:
        content = service.files().get_media(fileId=file_id).execute()
        return content.decode('utf-8')
    except Exception as e:
        return f"<h1>Hiba: {e}</h1>"
def set_design():
    """Közös dizájn beállítása minden oldalra."""
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #e4e4e4; }
        h1, h2, h3, p, div, li { color: #e4e4e4 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .stButton>button, .streamlit-expanderHeader { 
            background: rgba(255, 255, 255, 0.05) !important; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #fff !important;
        }
    </style>
    """, unsafe_allow_html=True)
