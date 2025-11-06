"""View Gallery Page - Browse and view media files from Google Drive"""

import streamlit as st
from PIL import Image
import io
import json

st.set_page_config(
    page_title="View Gallery",
    page_icon="🖼️",
    layout="wide"
)

st.title("🖼️ Media Gallery")
st.markdown("---")

# Check if Google Drive is configured
if not st.session_state.get('credentials_loaded', False):
    st.warning("⚠️ Please upload your Google Drive service account JSON file in the sidebar first!")
    st.stop()

gdrive_manager = st.session_state.gdrive_manager

# Filter options
st.header("🔍 Filter Options")

col1, col2, col3 = st.columns(3)

with col1:
    media_type = st.selectbox(
        "Media Type",
        ["All", "Images", "Videos"],
        index=0
    )

with col2:
    folder_option = st.selectbox(
        "Folder",
        ["Default Folder", "Custom Folder"],
        index=0
    )

with col3:
    if folder_option == "Custom Folder":
        custom_folder_name = st.text_input("Folder Name", placeholder="Enter folder name")
    else:
        custom_folder_name = None

# Refresh button
if st.button("🔄 Refresh Gallery", type="primary"):
    st.rerun()

st.markdown("---")

# Determine folder ID
folder_id = None
if folder_option == "Custom Folder" and custom_folder_name:
    folder_id = gdrive_manager.get_or_create_folder(custom_folder_name)
    if not folder_id:
        st.error(f"❌ Folder '{custom_folder_name}' not found!")
        st.stop()

# Fetch files
with st.spinner("Loading media files..."):
    try:
        # Determine MIME type filter
        mime_filter = None
        if media_type == "Images":
            mime_filter = "image/"
        elif media_type == "Videos":
            mime_filter = "video/"
        
        # List files
        files = gdrive_manager.list_files(folder_id=folder_id, mime_type_filter=mime_filter)
        
        if not files:
            st.info("📭 No media files found in this folder. Upload some files to get started!")
            st.stop()
        
        # Display statistics
        st.header("📊 Statistics")
        
        images = [f for f in files if f.get('mimeType', '').startswith('image/')]
        videos = [f for f in files if f.get('mimeType', '').startswith('video/')]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", len(files))
        with col2:
            st.metric("Images", len(images))
        with col3:
            st.metric("Videos", len(videos))
        
        st.markdown("---")
        
        # Display files
        if media_type in ["All", "Images"] and images:
            st.header("📷 Images")
            
            # Grid layout for images
            cols_per_row = 3
            
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        file_info = images[i + j]
                        
                        with col:
                            with st.container():
                                # Download and display image
                                try:
                                    file_bytes = gdrive_manager.download_file(file_info['id'])
                                    
                                    if file_bytes:
                                        image = Image.open(io.BytesIO(file_bytes))
                                        st.image(image, use_container_width=True)
                                        
                                        st.caption(f"**{file_info['name']}**")
                                        
                                        # File details in expander
                                        with st.expander("Details"):
                                            st.write(f"**Size:** {int(file_info.get('size', 0)) / 1024:.2f} KB")
                                            st.write(f"**Type:** {file_info.get('mimeType', 'N/A')}")
                                            st.write(f"**Created:** {file_info.get('createdTime', 'N/A')}")
                                            
                                            if file_info.get('webViewLink'):
                                                st.link_button("Open in Drive", file_info['webViewLink'])
                                            
                                            # Delete button
                                            if st.button(f"🗑️ Delete", key=f"del_img_{file_info['id']}"):
                                                if gdrive_manager.delete_file(file_info['id']):
                                                    st.success("Deleted!")
                                                    st.rerun()
                                                else:
                                                    st.error("Failed to delete")
                                    else:
                                        st.error("Failed to load image")
                                        
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
        
        if media_type in ["All", "Videos"] and videos:
            st.header("🎥 Videos")
            
            # List layout for videos
            for file_info in videos:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(file_info['name'])
                        
                        # Try to display video
                        try:
                            file_bytes = gdrive_manager.download_file(file_info['id'])
                            
                            if file_bytes:
                                st.video(file_bytes)
                            else:
                                st.error("Failed to load video")
                                
                        except Exception as e:
                            st.error(f"Error loading video: {str(e)}")
                    
                    with col2:
                        st.write(f"**Size:** {int(file_info.get('size', 0)) / (1024 * 1024):.2f} MB")
                        st.write(f"**Type:** {file_info.get('mimeType', 'N/A')}")
                        st.write(f"**Created:** {file_info.get('createdTime', 'N/A')[:10]}")
                        
                        if file_info.get('webViewLink'):
                            st.link_button("Open in Drive", file_info['webViewLink'], use_container_width=True)
                        
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"del_vid_{file_info['id']}", use_container_width=True):
                            if gdrive_manager.delete_file(file_info['id']):
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete")
                    
                    st.markdown("---")
        
    except Exception as e:
        st.error(f"❌ Error loading files: {str(e)}")

# Footer
st.markdown("---")
st.info("💡 **Tip:** Click on 'Details' to see more information about each file or delete it.")
