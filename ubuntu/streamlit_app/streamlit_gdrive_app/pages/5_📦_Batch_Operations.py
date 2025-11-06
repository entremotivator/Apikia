"""Batch Operations Page - Perform batch operations on media files"""

import streamlit as st
import time
from datetime import datetime

st.set_page_config(
    page_title="Batch Operations",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Batch Operations")
st.markdown("---")

# Check if Google Drive is configured
if not st.session_state.get('credentials_loaded', False):
    st.warning("⚠️ Please upload your Google Drive service account JSON file in the sidebar first!")
    st.stop()

gdrive_manager = st.session_state.gdrive_manager

# Operation selection
st.header("🔧 Select Operation")

operation = st.selectbox(
    "Choose an operation",
    [
        "Batch Upload",
        "Batch Download",
        "Batch Delete",
        "Move Files",
        "Copy Files",
        "Rename Files"
    ]
)

st.markdown("---")

# Batch Upload
if operation == "Batch Upload":
    st.header("📤 Batch Upload Files")
    
    uploaded_files = st.file_uploader(
        "Choose multiple files",
        accept_multiple_files=True,
        help="Upload multiple images and videos at once"
    )
    
    if uploaded_files:
        st.write(f"**Selected {len(uploaded_files)} file(s)**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_folder = st.text_input(
                "Target Folder (optional)",
                placeholder="Leave empty for default folder"
            )
        
        with col2:
            add_timestamp = st.checkbox("Add timestamp to filenames", value=False)
        
        if st.button("🚀 Upload All Files", type="primary"):
            folder_id = None
            if target_folder:
                folder_id = gdrive_manager.get_or_create_folder(target_folder)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Uploading {idx + 1}/{len(uploaded_files)}: {file.name}")
                
                try:
                    filename = file.name
                    if add_timestamp:
                        import os
                        name, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{name}_{timestamp}{ext}"
                    
                    file_bytes = file.read()
                    result = gdrive_manager.upload_file_from_bytes(
                        file_bytes,
                        filename,
                        folder_id=folder_id,
                        mime_type=file.type
                    )
                    
                    if result:
                        success_count += 1
                    
                except Exception as e:
                    st.error(f"Error uploading {file.name}: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("Upload complete!")
            st.success(f"✅ Successfully uploaded {success_count}/{len(uploaded_files)} files!")

# Batch Download
elif operation == "Batch Download":
    st.header("📥 Batch Download Files")
    
    folder_name = st.text_input("Folder Name (optional)", placeholder="Leave empty for default folder")
    
    if st.button("📋 List Files"):
        folder_id = None
        if folder_name:
            folder_id = gdrive_manager.get_or_create_folder(folder_name)
        
        files = gdrive_manager.list_files(folder_id=folder_id)
        
        if files:
            st.write(f"**Found {len(files)} file(s)**")
            
            selected_files = st.multiselect(
                "Select files to download",
                options=files,
                format_func=lambda x: f"{x['name']} ({int(x.get('size', 0)) / 1024:.2f} KB)"
            )
            
            if selected_files and st.button("💾 Download Selected Files", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file in enumerate(selected_files):
                    status_text.text(f"Downloading {idx + 1}/{len(selected_files)}: {file['name']}")
                    
                    try:
                        file_bytes = gdrive_manager.download_file(file['id'])
                        
                        if file_bytes:
                            st.download_button(
                                label=f"💾 {file['name']}",
                                data=file_bytes,
                                file_name=file['name'],
                                mime=file.get('mimeType', 'application/octet-stream'),
                                key=f"download_{file['id']}"
                            )
                    except Exception as e:
                        st.error(f"Error downloading {file['name']}: {str(e)}")
                    
                    progress_bar.progress((idx + 1) / len(selected_files))
                
                status_text.text("Download links generated!")
        else:
            st.info("📭 No files found")

# Batch Delete
elif operation == "Batch Delete":
    st.header("🗑️ Batch Delete Files")
    st.warning("⚠️ **Warning:** This operation cannot be undone!")
    
    folder_name = st.text_input("Folder Name (optional)", placeholder="Leave empty for default folder")
    
    if st.button("📋 List Files"):
        folder_id = None
        if folder_name:
            folder_id = gdrive_manager.get_or_create_folder(folder_name)
        
        files = gdrive_manager.list_files(folder_id=folder_id)
        
        if files:
            st.write(f"**Found {len(files)} file(s)**")
            
            selected_files = st.multiselect(
                "Select files to delete",
                options=files,
                format_func=lambda x: f"{x['name']} ({int(x.get('size', 0)) / 1024:.2f} KB)"
            )
            
            if selected_files:
                confirm = st.checkbox("I understand that this action cannot be undone")
                
                if confirm and st.button("🗑️ Delete Selected Files", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    
                    for idx, file in enumerate(selected_files):
                        status_text.text(f"Deleting {idx + 1}/{len(selected_files)}: {file['name']}")
                        
                        try:
                            if gdrive_manager.delete_file(file['id']):
                                success_count += 1
                        except Exception as e:
                            st.error(f"Error deleting {file['name']}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(selected_files))
                    
                    status_text.text("Deletion complete!")
                    st.success(f"✅ Successfully deleted {success_count}/{len(selected_files)} files!")
        else:
            st.info("📭 No files found")

# Move Files
elif operation == "Move Files":
    st.header("📁 Move Files Between Folders")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source_folder = st.text_input("Source Folder", placeholder="Leave empty for default folder")
    
    with col2:
        target_folder = st.text_input("Target Folder", placeholder="Enter target folder name")
    
    if st.button("📋 List Files from Source"):
        source_folder_id = None
        if source_folder:
            source_folder_id = gdrive_manager.get_or_create_folder(source_folder)
        
        files = gdrive_manager.list_files(folder_id=source_folder_id)
        
        if files:
            st.write(f"**Found {len(files)} file(s)**")
            
            selected_files = st.multiselect(
                "Select files to move",
                options=files,
                format_func=lambda x: f"{x['name']} ({int(x.get('size', 0)) / 1024:.2f} KB)"
            )
            
            if selected_files and target_folder and st.button("➡️ Move Selected Files", type="primary"):
                target_folder_id = gdrive_manager.get_or_create_folder(target_folder)
                
                if target_folder_id:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    
                    for idx, file in enumerate(selected_files):
                        status_text.text(f"Moving {idx + 1}/{len(selected_files)}: {file['name']}")
                        
                        try:
                            # Move file by updating parents
                            previous_parents = ",".join(file.get('parents', []))
                            
                            gdrive_manager.service.files().update(
                                fileId=file['id'],
                                addParents=target_folder_id,
                                removeParents=previous_parents,
                                fields='id, parents'
                            ).execute()
                            
                            success_count += 1
                            
                        except Exception as e:
                            st.error(f"Error moving {file['name']}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(selected_files))
                    
                    status_text.text("Move complete!")
                    st.success(f"✅ Successfully moved {success_count}/{len(selected_files)} files!")
                else:
                    st.error("❌ Failed to create/find target folder")
        else:
            st.info("📭 No files found in source folder")

# Copy Files
elif operation == "Copy Files":
    st.header("📋 Copy Files Between Folders")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source_folder = st.text_input("Source Folder", placeholder="Leave empty for default folder")
    
    with col2:
        target_folder = st.text_input("Target Folder", placeholder="Enter target folder name")
    
    if st.button("📋 List Files from Source"):
        source_folder_id = None
        if source_folder:
            source_folder_id = gdrive_manager.get_or_create_folder(source_folder)
        
        files = gdrive_manager.list_files(folder_id=source_folder_id)
        
        if files:
            st.write(f"**Found {len(files)} file(s)**")
            
            selected_files = st.multiselect(
                "Select files to copy",
                options=files,
                format_func=lambda x: f"{x['name']} ({int(x.get('size', 0)) / 1024:.2f} KB)"
            )
            
            if selected_files and target_folder and st.button("📋 Copy Selected Files", type="primary"):
                target_folder_id = gdrive_manager.get_or_create_folder(target_folder)
                
                if target_folder_id:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    
                    for idx, file in enumerate(selected_files):
                        status_text.text(f"Copying {idx + 1}/{len(selected_files)}: {file['name']}")
                        
                        try:
                            # Copy file
                            gdrive_manager.service.files().copy(
                                fileId=file['id'],
                                body={'parents': [target_folder_id], 'name': file['name']}
                            ).execute()
                            
                            success_count += 1
                            
                        except Exception as e:
                            st.error(f"Error copying {file['name']}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(selected_files))
                    
                    status_text.text("Copy complete!")
                    st.success(f"✅ Successfully copied {success_count}/{len(selected_files)} files!")
                else:
                    st.error("❌ Failed to create/find target folder")
        else:
            st.info("📭 No files found in source folder")

# Rename Files
elif operation == "Rename Files":
    st.header("✏️ Batch Rename Files")
    
    folder_name = st.text_input("Folder Name (optional)", placeholder="Leave empty for default folder")
    
    if st.button("📋 List Files"):
        folder_id = None
        if folder_name:
            folder_id = gdrive_manager.get_or_create_folder(folder_name)
        
        files = gdrive_manager.list_files(folder_id=folder_id)
        
        if files:
            st.write(f"**Found {len(files)} file(s)**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                prefix = st.text_input("Add Prefix", placeholder="Optional prefix")
            
            with col2:
                suffix = st.text_input("Add Suffix (before extension)", placeholder="Optional suffix")
            
            selected_files = st.multiselect(
                "Select files to rename",
                options=files,
                format_func=lambda x: x['name']
            )
            
            if selected_files:
                st.subheader("Preview")
                
                import os
                
                for file in selected_files:
                    name, ext = os.path.splitext(file['name'])
                    new_name = f"{prefix}{name}{suffix}{ext}"
                    st.write(f"**{file['name']}** → **{new_name}**")
                
                if st.button("✏️ Rename Selected Files", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    
                    for idx, file in enumerate(selected_files):
                        status_text.text(f"Renaming {idx + 1}/{len(selected_files)}: {file['name']}")
                        
                        try:
                            name, ext = os.path.splitext(file['name'])
                            new_name = f"{prefix}{name}{suffix}{ext}"
                            
                            gdrive_manager.service.files().update(
                                fileId=file['id'],
                                body={'name': new_name}
                            ).execute()
                            
                            success_count += 1
                            
                        except Exception as e:
                            st.error(f"Error renaming {file['name']}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(selected_files))
                    
                    status_text.text("Rename complete!")
                    st.success(f"✅ Successfully renamed {success_count}/{len(selected_files)} files!")
        else:
            st.info("📭 No files found")

st.markdown("---")
st.info("💡 **Tip:** Batch operations help you manage multiple files efficiently.")
