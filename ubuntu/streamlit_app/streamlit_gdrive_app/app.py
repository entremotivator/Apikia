"""Main Streamlit Application with Google Drive Integration"""

import streamlit as st
import json
from gdrive_helper import GoogleDriveManager
from api_helper import ImageEditAPI, NanoBananaAPI, CharacterEditAPI

# Page configuration
st.set_page_config(
    page_title="Google Drive Media Manager",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'gdrive_manager' not in st.session_state:
    st.session_state.gdrive_manager = None
if 'api_client' not in st.session_state:
    st.session_state.api_client = None
if 'credentials_loaded' not in st.session_state:
    st.session_state.credentials_loaded = False
if 'api_key_loaded' not in st.session_state:
    st.session_state.api_key_loaded = False

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")

# Google Drive Service Account Upload
st.sidebar.header("🔐 Google Drive Authentication")
uploaded_json = st.sidebar.file_uploader(
    "Upload Service Account JSON",
    type=['json'],
    help="Upload your Google Drive service account JSON file"
)

if uploaded_json is not None:
    try:
        credentials_json = json.load(uploaded_json)
        st.session_state.gdrive_manager = GoogleDriveManager(credentials_json)
        st.session_state.credentials_loaded = True
        st.sidebar.success("✅ Credentials loaded successfully!")
        
        # Display service account email
        service_account_email = credentials_json.get('client_email', 'N/A')
        st.sidebar.info(f"📧 Service Account: {service_account_email}")
        
    except Exception as e:
        st.sidebar.error(f"❌ Error loading credentials: {str(e)}")
        st.session_state.credentials_loaded = False
else:
    if st.session_state.credentials_loaded:
        st.sidebar.warning("⚠️ No credentials file uploaded in this session")
    else:
        st.sidebar.info("ℹ️ Please upload your service account JSON file")

# API Configuration
st.sidebar.header("🔑 API Configuration")
api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    help="Enter your API key for image editing"
)

if api_key:
    st.session_state.api_client = ImageEditAPI(api_key)
    st.session_state.nano_banana_client = NanoBananaAPI(api_key)
    st.session_state.character_edit_client = CharacterEditAPI(api_key)
    st.session_state.api_key_loaded = True
    st.sidebar.success("✅ API key configured!")
else:
    if st.session_state.api_key_loaded:
        st.sidebar.warning("⚠️ No API key entered in this session")
    else:
        st.sidebar.info("ℹ️ Enter your API key to use image editing features")

# Default folder configuration
st.sidebar.header("📂 Google Drive Settings")
if st.session_state.gdrive_manager:
    default_folder = st.sidebar.text_input(
        "Default Folder Name",
        value=st.session_state.gdrive_manager.default_folder_name,
        help="Name of the default folder in Google Drive"
    )
    
    if st.sidebar.button("Update Folder Name"):
        st.session_state.gdrive_manager.default_folder_name = default_folder
        st.session_state.gdrive_manager.default_folder_id = None
        st.sidebar.success(f"✅ Default folder updated to: {default_folder}")

# Sidebar divider
st.sidebar.divider()

# Status indicators
st.sidebar.header("📊 Status")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.session_state.credentials_loaded:
        st.success("Drive ✓")
    else:
        st.error("Drive ✗")
with col2:
    if st.session_state.api_key_loaded:
        st.success("API ✓")
    else:
        st.error("API ✗")

# Main content
st.title("📁 Google Drive Media Manager")
st.markdown("---")

# Welcome section
st.header("Welcome! 👋")
st.write("""
This application allows you to manage and view images and videos with Google Drive integration.
Upload your service account JSON file and configure your API key in the sidebar to get started.
""")

# Features overview
st.header("✨ Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📤 Upload Media")
    st.write("Upload images and videos directly to Google Drive with automatic organization.")

with col2:
    st.subheader("🖼️ View Gallery")
    st.write("Browse and view all your media files stored in Google Drive.")

with col3:
    st.subheader("🎨 API Testing")
    st.write("Test image editing API with various parameters and settings.")

st.markdown("---")

# Quick start guide
st.header("🚀 Quick Start Guide")

with st.expander("1. Setup Google Drive Service Account", expanded=False):
    st.markdown("""
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project or select an existing one
    3. Enable the Google Drive API
    4. Create a Service Account and download the JSON key
    5. Share your Google Drive folder with the service account email
    6. Upload the JSON file using the sidebar
    """)

with st.expander("2. Configure API Key", expanded=False):
    st.markdown("""
    1. Visit [API Key Management Page](https://kie.ai/api-key) to get your API Key
    2. Enter the API key in the sidebar
    3. The API will be used for image editing features
    """)

with st.expander("3. Start Using the App", expanded=False):
    st.markdown("""
    1. Navigate to **Upload Media** page to upload files
    2. Visit **View Gallery** to browse your media
    3. Use **API Testing** to experiment with image editing
    4. Check **Settings** for additional configuration options
    """)

st.markdown("---")

# System information
if st.session_state.credentials_loaded and st.session_state.gdrive_manager:
    st.header("📋 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Default Folder", st.session_state.gdrive_manager.default_folder_name)
    
    with col2:
        try:
            folder_id = st.session_state.gdrive_manager.ensure_default_folder()
            if folder_id:
                st.metric("Folder Status", "✅ Ready")
            else:
                st.metric("Folder Status", "❌ Error")
        except Exception as e:
            st.metric("Folder Status", "❌ Error")
            st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Google Drive Media Manager | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
