"""Settings Page - Configure application settings"""

import streamlit as st
import json

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Application Settings")
st.markdown("---")

# Google Drive Settings
st.header("📂 Google Drive Settings")

if st.session_state.get('credentials_loaded', False):
    gdrive_manager = st.session_state.gdrive_manager
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Configuration")
        st.write(f"**Default Folder:** {gdrive_manager.default_folder_name}")
        
        # Get folder ID
        try:
            folder_id = gdrive_manager.ensure_default_folder()
            if folder_id:
                st.success(f"✅ Folder ID: {folder_id}")
            else:
                st.error("❌ Failed to get folder ID")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("Update Settings")
        
        new_folder_name = st.text_input(
            "New Default Folder Name",
            value=gdrive_manager.default_folder_name,
            help="Enter a new name for the default folder"
        )
        
        if st.button("💾 Update Folder Name", type="primary"):
            gdrive_manager.default_folder_name = new_folder_name
            gdrive_manager.default_folder_id = None
            st.success(f"✅ Default folder updated to: {new_folder_name}")
            st.rerun()
    
    st.markdown("---")
    
    # Folder Management
    st.subheader("📁 Folder Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Create New Folder**")
        new_folder = st.text_input("Folder Name", key="new_folder")
        
        if st.button("➕ Create Folder"):
            if new_folder:
                folder_id = gdrive_manager.get_or_create_folder(new_folder)
                if folder_id:
                    st.success(f"✅ Folder created/found: {new_folder}")
                else:
                    st.error("❌ Failed to create folder")
            else:
                st.warning("⚠️ Please enter a folder name")
    
    with col2:
        st.write("**List All Folders**")
        
        if st.button("📋 List Folders"):
            try:
                # List all folders
                query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = gdrive_manager.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name, createdTime)',
                    orderBy='name'
                ).execute()
                
                folders = results.get('files', [])
                
                if folders:
                    st.write(f"Found {len(folders)} folder(s):")
                    for folder in folders:
                        st.write(f"• **{folder['name']}** (ID: {folder['id']})")
                else:
                    st.info("No folders found")
                    
            except Exception as e:
                st.error(f"Error listing folders: {str(e)}")
    
    st.markdown("---")
    
    # Storage Statistics
    st.subheader("📊 Storage Statistics")
    
    try:
        # Get default folder files
        files = gdrive_manager.list_files()
        
        if files:
            total_size = sum(int(f.get('size', 0)) for f in files)
            images = [f for f in files if f.get('mimeType', '').startswith('image/')]
            videos = [f for f in files if f.get('mimeType', '').startswith('video/')]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", len(files))
            with col2:
                st.metric("Images", len(images))
            with col3:
                st.metric("Videos", len(videos))
            with col4:
                st.metric("Total Size", f"{total_size / (1024 * 1024):.2f} MB")
        else:
            st.info("No files in default folder")
            
    except Exception as e:
        st.error(f"Error getting statistics: {str(e)}")

else:
    st.warning("⚠️ Please upload your Google Drive service account JSON file in the sidebar first!")

st.markdown("---")

# API Settings
st.header("🔑 API Settings")

if st.session_state.get('api_key_loaded', False):
    st.success("✅ API key is configured")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Information")
        st.write("**Base URL:** https://api.kie.ai/api/v1/jobs")
        st.write("**Model:** qwen/image-edit")
    
    with col2:
        st.subheader("API Status")
        
        if st.button("🔍 Test API Connection"):
            try:
                api_client = st.session_state.api_client
                
                # Try to create a simple task to test the API
                with st.spinner("Testing API..."):
                    test_url = "https://file.aiquickdraw.com/custom-page/akr/section-images/1755603225969i6j87xnw.jpg"
                    task_id = api_client.create_task("test", test_url)
                    
                    if task_id:
                        st.success("✅ API connection successful!")
                        st.info(f"Test task ID: {task_id}")
                    else:
                        st.error("❌ API connection failed!")
                        
            except Exception as e:
                st.error(f"Error testing API: {str(e)}")
else:
    st.warning("⚠️ Please configure your API key in the sidebar first!")

st.markdown("---")

# Application Information
st.header("ℹ️ Application Information")

col1, col2 = st.columns(2)

with col1:
    st.subheader("About")
    st.write("**Name:** Google Drive Media Manager")
    st.write("**Version:** 1.0.0")
    st.write("**Framework:** Streamlit")

with col2:
    st.subheader("Features")
    st.write("✅ Google Drive Integration")
    st.write("✅ Multi-page Structure")
    st.write("✅ Image & Video Upload")
    st.write("✅ Media Gallery")
    st.write("✅ API Testing")

st.markdown("---")

# Session State Debug (for development)
with st.expander("🔧 Debug Information (Development)"):
    st.subheader("Session State")
    st.json({
        "credentials_loaded": st.session_state.get('credentials_loaded', False),
        "api_key_loaded": st.session_state.get('api_key_loaded', False),
        "gdrive_manager_exists": st.session_state.get('gdrive_manager') is not None,
        "api_client_exists": st.session_state.get('api_client') is not None
    })

# Reset Settings
st.markdown("---")
st.header("🔄 Reset Settings")

col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Clear Google Drive Credentials", type="secondary"):
        st.session_state.gdrive_manager = None
        st.session_state.credentials_loaded = False
        st.success("✅ Credentials cleared!")
        st.rerun()

with col2:
    if st.button("🗑️ Clear API Key", type="secondary"):
        st.session_state.api_client = None
        st.session_state.api_key_loaded = False
        st.success("✅ API key cleared!")
        st.rerun()

st.markdown("---")
st.info("💡 **Tip:** Use the sidebar to reconfigure your credentials and API key after clearing.")
