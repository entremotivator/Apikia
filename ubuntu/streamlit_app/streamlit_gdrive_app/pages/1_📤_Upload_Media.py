"""Upload Media Page - Upload images and videos to Google Drive"""

import streamlit as st
import os
import tempfile
from datetime import datetime

st.set_page_config(
    page_title="Upload Media",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Upload Media to Google Drive")
st.markdown("---")

# Check if Google Drive is configured
if not st.session_state.get('credentials_loaded', False):
    st.warning("⚠️ Please upload your Google Drive service account JSON file in the sidebar first!")
    st.stop()

gdrive_manager = st.session_state.gdrive_manager

# Upload section
st.header("Upload Files")

# File uploader for images
st.subheader("📷 Upload Images")
uploaded_images = st.file_uploader(
    "Choose image files",
    type=['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp'],
    accept_multiple_files=True,
    key="image_uploader"
)

# File uploader for videos
st.subheader("🎥 Upload Videos")
uploaded_videos = st.file_uploader(
    "Choose video files",
    type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'],
    accept_multiple_files=True,
    key="video_uploader"
)

# Upload options
st.markdown("---")
st.subheader("⚙️ Upload Options")

col1, col2 = st.columns(2)

with col1:
    custom_folder = st.text_input(
        "Custom Folder Name (optional)",
        placeholder="Leave empty to use default folder",
        help="Specify a custom folder name or leave empty to use the default folder"
    )

with col2:
    add_timestamp = st.checkbox(
        "Add timestamp to filename",
        value=False,
        help="Add current timestamp to the filename to avoid duplicates"
    )

# Upload button
st.markdown("---")

if st.button("🚀 Upload to Google Drive", type="primary", use_container_width=True):
    if not uploaded_images and not uploaded_videos:
        st.warning("⚠️ Please select at least one file to upload!")
    else:
        # Determine folder ID
        folder_id = None
        if custom_folder:
            with st.spinner(f"Creating/finding folder: {custom_folder}..."):
                folder_id = gdrive_manager.get_or_create_folder(custom_folder)
                if not folder_id:
                    st.error(f"❌ Failed to create/find folder: {custom_folder}")
                    st.stop()
        
        # Progress tracking
        total_files = len(uploaded_images or []) + len(uploaded_videos or [])
        progress_bar = st.progress(0)
        status_text = st.empty()
        uploaded_count = 0
        
        # Upload images
        if uploaded_images:
            st.subheader("📷 Uploading Images...")
            
            for img_file in uploaded_images:
                status_text.text(f"Uploading: {img_file.name}")
                
                try:
                    # Prepare filename
                    filename = img_file.name
                    if add_timestamp:
                        name, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{name}_{timestamp}{ext}"
                    
                    # Get MIME type
                    mime_type = img_file.type
                    
                    # Upload file
                    file_bytes = img_file.read()
                    result = gdrive_manager.upload_file_from_bytes(
                        file_bytes,
                        filename,
                        folder_id=folder_id,
                        mime_type=mime_type
                    )
                    
                    if result:
                        st.success(f"✅ Uploaded: {filename}")
                        uploaded_count += 1
                    else:
                        st.error(f"❌ Failed to upload: {filename}")
                    
                except Exception as e:
                    st.error(f"❌ Error uploading {img_file.name}: {str(e)}")
                
                # Update progress
                progress_bar.progress(uploaded_count / total_files)
        
        # Upload videos
        if uploaded_videos:
            st.subheader("🎥 Uploading Videos...")
            
            for vid_file in uploaded_videos:
                status_text.text(f"Uploading: {vid_file.name}")
                
                try:
                    # Prepare filename
                    filename = vid_file.name
                    if add_timestamp:
                        name, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{name}_{timestamp}{ext}"
                    
                    # Get MIME type
                    mime_type = vid_file.type
                    
                    # Upload file
                    file_bytes = vid_file.read()
                    result = gdrive_manager.upload_file_from_bytes(
                        file_bytes,
                        filename,
                        folder_id=folder_id,
                        mime_type=mime_type
                    )
                    
                    if result:
                        st.success(f"✅ Uploaded: {filename}")
                        uploaded_count += 1
                    else:
                        st.error(f"❌ Failed to upload: {filename}")
                    
                except Exception as e:
                    st.error(f"❌ Error uploading {vid_file.name}: {str(e)}")
                
                # Update progress
                progress_bar.progress(uploaded_count / total_files)
        
        # Complete
        progress_bar.progress(1.0)
        status_text.text("Upload complete!")
        
        st.success(f"🎉 Successfully uploaded {uploaded_count} out of {total_files} files!")
        
        if uploaded_count < total_files:
            st.warning(f"⚠️ {total_files - uploaded_count} file(s) failed to upload. Please check the errors above.")

# Information section
st.markdown("---")
st.header("ℹ️ Information")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Supported Image Formats")
    st.write("• JPG / JPEG")
    st.write("• PNG")
    st.write("• WEBP")
    st.write("• GIF")
    st.write("• BMP")

with col2:
    st.subheader("Supported Video Formats")
    st.write("• MP4")
    st.write("• AVI")
    st.write("• MOV")
    st.write("• MKV")
    st.write("• WMV")
    st.write("• FLV")
    st.write("• WEBM")

st.markdown("---")
st.info("💡 **Tip:** Files are automatically saved to your Google Drive. You can view them in the 'View Gallery' page.")
