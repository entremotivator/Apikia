"""File Manager Page - Advanced file management interface"""

import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="File Manager",
    page_icon="📂",
    layout="wide"
)

st.title("📂 File Manager")
st.markdown("---")

# Check if Google Drive is configured
if not st.session_state.get('credentials_loaded', False):
    st.warning("⚠️ Please upload your Google Drive service account JSON file in the sidebar first!")
    st.stop()

gdrive_manager = st.session_state.gdrive_manager

# Initialize session state for file manager
if 'current_folder_id' not in st.session_state:
    st.session_state.current_folder_id = None
if 'current_folder_name' not in st.session_state:
    st.session_state.current_folder_name = "Default Folder"
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []

# Navigation bar
st.header("🧭 Navigation")

col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

with col1:
    st.write(f"**Current Location:** {st.session_state.current_folder_name}")

with col2:
    folder_input = st.text_input("Go to folder", placeholder="Enter folder name", label_visibility="collapsed")

with col3:
    if st.button("📁 Go", use_container_width=True):
        if folder_input:
            folder_id = gdrive_manager.get_or_create_folder(folder_input)
            if folder_id:
                st.session_state.current_folder_id = folder_id
                st.session_state.current_folder_name = folder_input
                st.rerun()

with col4:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_folder_id = None
        st.session_state.current_folder_name = "Default Folder"
        st.rerun()

st.markdown("---")

# Action toolbar
st.header("🔧 Actions")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col2:
    create_folder = st.button("➕ New Folder", use_container_width=True)

with col3:
    upload_file = st.button("📤 Upload", use_container_width=True)

with col4:
    if st.session_state.selected_files:
        delete_selected = st.button(f"🗑️ Delete ({len(st.session_state.selected_files)})", use_container_width=True)
    else:
        delete_selected = False
        st.button("🗑️ Delete", use_container_width=True, disabled=True)

with col5:
    if st.session_state.selected_files:
        download_selected = st.button(f"💾 Download ({len(st.session_state.selected_files)})", use_container_width=True)
    else:
        download_selected = False
        st.button("💾 Download", use_container_width=True, disabled=True)

# Handle actions
if create_folder:
    with st.form("create_folder_form"):
        st.subheader("Create New Folder")
        new_folder_name = st.text_input("Folder Name")
        submitted = st.form_submit_button("Create")
        
        if submitted and new_folder_name:
            folder_id = gdrive_manager.get_or_create_folder(
                new_folder_name,
                parent_id=st.session_state.current_folder_id
            )
            if folder_id:
                st.success(f"✅ Folder '{new_folder_name}' created!")
                st.rerun()
            else:
                st.error("❌ Failed to create folder")

if upload_file:
    with st.form("upload_file_form"):
        st.subheader("Upload Files")
        uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
        submitted = st.form_submit_button("Upload")
        
        if submitted and uploaded_files:
            progress_bar = st.progress(0)
            success_count = 0
            
            for idx, file in enumerate(uploaded_files):
                file_bytes = file.read()
                result = gdrive_manager.upload_file_from_bytes(
                    file_bytes,
                    file.name,
                    folder_id=st.session_state.current_folder_id,
                    mime_type=file.type
                )
                
                if result:
                    success_count += 1
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            st.success(f"✅ Uploaded {success_count}/{len(uploaded_files)} files!")
            st.rerun()

if delete_selected:
    st.warning("⚠️ Are you sure you want to delete the selected files?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Yes, Delete", type="primary"):
            success_count = 0
            for file_id in st.session_state.selected_files:
                if gdrive_manager.delete_file(file_id):
                    success_count += 1
            
            st.success(f"✅ Deleted {success_count} files!")
            st.session_state.selected_files = []
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel"):
            st.rerun()

if download_selected:
    st.subheader("Download Selected Files")
    
    for file_id in st.session_state.selected_files:
        try:
            file_info = gdrive_manager.get_file_metadata(file_id)
            file_bytes = gdrive_manager.download_file(file_id)
            
            if file_bytes and file_info:
                st.download_button(
                    label=f"💾 {file_info['name']}",
                    data=file_bytes,
                    file_name=file_info['name'],
                    mime=file_info.get('mimeType', 'application/octet-stream'),
                    key=f"dl_{file_id}"
                )
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")

# File list
st.header("📋 Files and Folders")

try:
    # Get files
    files = gdrive_manager.list_files(folder_id=st.session_state.current_folder_id)
    
    if not files:
        st.info("📭 This folder is empty")
    else:
        # Separate folders and files
        folders = [f for f in files if f.get('mimeType') == 'application/vnd.google-apps.folder']
        regular_files = [f for f in files if f.get('mimeType') != 'application/vnd.google-apps.folder']
        
        # Display folders
        if folders:
            st.subheader("📁 Folders")
            
            for folder in folders:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"📁 **{folder['name']}**")
                
                with col2:
                    st.write(f"Created: {folder.get('createdTime', 'N/A')[:10]}")
                
                with col3:
                    if st.button("Open", key=f"open_{folder['id']}"):
                        st.session_state.current_folder_id = folder['id']
                        st.session_state.current_folder_name = folder['name']
                        st.rerun()
            
            st.markdown("---")
        
        # Display files
        if regular_files:
            st.subheader("📄 Files")
            
            # Table header
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 1.5, 1.5, 1, 1])
            
            with col1:
                st.write("**☑️**")
            with col2:
                st.write("**Name**")
            with col3:
                st.write("**Type**")
            with col4:
                st.write("**Size**")
            with col5:
                st.write("**Created**")
            with col6:
                st.write("**Actions**")
            
            st.markdown("---")
            
            # File rows
            for file in regular_files:
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 1.5, 1.5, 1, 1])
                
                with col1:
                    selected = st.checkbox(
                        "",
                        value=file['id'] in st.session_state.selected_files,
                        key=f"select_{file['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if selected and file['id'] not in st.session_state.selected_files:
                        st.session_state.selected_files.append(file['id'])
                    elif not selected and file['id'] in st.session_state.selected_files:
                        st.session_state.selected_files.remove(file['id'])
                
                with col2:
                    # Icon based on type
                    mime_type = file.get('mimeType', '')
                    if mime_type.startswith('image/'):
                        icon = "🖼️"
                    elif mime_type.startswith('video/'):
                        icon = "🎥"
                    elif mime_type.startswith('audio/'):
                        icon = "🎵"
                    else:
                        icon = "📄"
                    
                    st.write(f"{icon} {file['name']}")
                
                with col3:
                    st.write(mime_type.split('/')[-1] if '/' in mime_type else mime_type)
                
                with col4:
                    size = int(file.get('size', 0))
                    if size < 1024:
                        st.write(f"{size} B")
                    elif size < 1024 * 1024:
                        st.write(f"{size / 1024:.2f} KB")
                    else:
                        st.write(f"{size / (1024 * 1024):.2f} MB")
                
                with col5:
                    st.write(file.get('createdTime', 'N/A')[:10])
                
                with col6:
                    if st.button("👁️", key=f"view_{file['id']}", help="View"):
                        # Store file to view in session state
                        st.session_state.viewing_file = file
                        st.rerun()
            
            st.markdown("---")
            
            # Statistics
            total_size = sum(int(f.get('size', 0)) for f in regular_files)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Files", len(regular_files))
            with col2:
                st.metric("Total Size", f"{total_size / (1024 * 1024):.2f} MB")
            with col3:
                st.metric("Selected", len(st.session_state.selected_files))

except Exception as e:
    st.error(f"❌ Error loading files: {str(e)}")

# File viewer
if 'viewing_file' in st.session_state and st.session_state.viewing_file:
    st.markdown("---")
    st.header("👁️ File Viewer")
    
    file = st.session_state.viewing_file
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(file['name'])
    
    with col2:
        if st.button("❌ Close Viewer"):
            del st.session_state.viewing_file
            st.rerun()
    
    try:
        file_bytes = gdrive_manager.download_file(file['id'])
        
        if file_bytes:
            mime_type = file.get('mimeType', '')
            
            if mime_type.startswith('image/'):
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(file_bytes))
                st.image(image, use_container_width=True)
            
            elif mime_type.startswith('video/'):
                st.video(file_bytes)
            
            elif mime_type.startswith('text/'):
                st.text(file_bytes.decode('utf-8'))
            
            else:
                st.info("Preview not available for this file type")
            
            # Download button
            st.download_button(
                label="💾 Download File",
                data=file_bytes,
                file_name=file['name'],
                mime=mime_type,
                key="viewer_download"
            )
        else:
            st.error("Failed to load file")
            
    except Exception as e:
        st.error(f"Error viewing file: {str(e)}")

st.markdown("---")
st.info("💡 **Tip:** Select multiple files using checkboxes to perform batch operations.")
