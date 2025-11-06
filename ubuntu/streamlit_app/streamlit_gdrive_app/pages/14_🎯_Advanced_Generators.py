"""
Advanced Generators - Additional KieAI API features and specialized generators
"""

import streamlit as st
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_helper import BaseAPIClient

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Generators",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Advanced Generators")
st.markdown("""
Explore advanced KieAI API features including image-to-video, video upscaling, and more specialized generators.
""")

# Check API configuration
if not st.session_state.get('api_key_loaded', False):
    st.warning("⚠️ Please configure your API key in the sidebar first!")
    st.stop()

# Initialize API client
api_key = st.session_state.get('api_client').api_key if st.session_state.get('api_client') else None
if not api_key:
    st.error("❌ API key not found!")
    st.stop()

base_client = BaseAPIClient(api_key)

# --- Tabs for Different Generators ---
tab1, tab2, tab3, tab4 = st.tabs([
    "Image-to-Video",
    "Video Upscaling",
    "Style Transfer",
    "Batch Processing"
])

# --- Tab 1: Image-to-Video ---
with tab1:
    st.header("🖼️➡️🎬 Image-to-Video Generator")
    st.markdown("Transform static images into dynamic videos with AI-powered animation.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Image source
        image_source = st.radio(
            "Image Source",
            ["URL", "Upload", "Google Drive"],
            horizontal=True,
            key="i2v_source"
        )
        
        image_url = None
        
        if image_source == "URL":
            image_url = st.text_input(
                "Image URL",
                placeholder="https://example.com/image.jpg",
                key="i2v_url"
            )
        elif image_source == "Upload":
            uploaded_file = st.file_uploader(
                "Upload Image",
                type=['jpg', 'jpeg', 'png', 'webp'],
                key="i2v_upload"
            )
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                st.info("ℹ️ Upload to a public URL to use with the API")
        else:  # Google Drive
            if st.session_state.get('credentials_loaded', False):
                gdrive_manager = st.session_state.gdrive_manager
                files = gdrive_manager.list_files(mime_type_filter="image/")
                
                if files:
                    selected_file = st.selectbox(
                        "Select Image",
                        options=files,
                        format_func=lambda x: x['name'],
                        key="i2v_gdrive"
                    )
                    if selected_file:
                        image_url = selected_file.get('webContentLink')
                        file_bytes = gdrive_manager.download_file(selected_file['id'])
                        if file_bytes:
                            st.image(file_bytes, caption=selected_file['name'], use_container_width=True)
        
        # Motion prompt
        motion_prompt = st.text_area(
            "Motion Description",
            placeholder="Describe how the image should animate (e.g., 'camera slowly zooms in', 'leaves gently swaying in wind')",
            height=100,
            key="i2v_motion"
        )
    
    with col2:
        # Parameters
        st.markdown("**Parameters**")
        
        duration = st.slider(
            "Duration (seconds)",
            min_value=2,
            max_value=10,
            value=5,
            key="i2v_duration"
        )
        
        motion_intensity = st.slider(
            "Motion Intensity",
            min_value=1,
            max_value=10,
            value=5,
            help="How much movement to add",
            key="i2v_intensity"
        )
        
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["16:9", "9:16", "1:1"],
            key="i2v_aspect"
        )
    
    if st.button("🚀 Generate Video from Image", type="primary", use_container_width=True, key="i2v_generate"):
        if not image_url or not motion_prompt:
            st.error("❌ Please provide both an image and motion description!")
        else:
            with st.spinner("Generating video from image..."):
                input_params = {
                    "image_url": image_url,
                    "prompt": motion_prompt,
                    "duration": duration,
                    "motion_intensity": motion_intensity,
                    "aspect_ratio": aspect_ratio
                }
                
                task_id = base_client.create_task("runway/image-to-video", input_params)
                
                if task_id:
                    st.success(f"✅ Task created! Task ID: `{task_id}`")
                    st.info("💡 Check the Job Monitor page to track progress.")
                else:
                    st.error("❌ Failed to create task")

# --- Tab 2: Video Upscaling ---
with tab2:
    st.header("⬆️ Video Upscaling & Enhancement")
    st.markdown("Upscale and enhance video quality using AI.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        video_url = st.text_input(
            "Video URL",
            placeholder="https://example.com/video.mp4",
            key="upscale_url"
        )
        
        st.markdown("**Enhancement Options**")
        
        col_opt1, col_opt2 = st.columns(2)
        
        with col_opt1:
            upscale_factor = st.selectbox(
                "Upscale Factor",
                ["2x", "4x"],
                key="upscale_factor"
            )
            
            enhance_faces = st.checkbox(
                "Enhance Faces",
                value=True,
                key="upscale_faces"
            )
        
        with col_opt2:
            denoise = st.checkbox(
                "Reduce Noise",
                value=True,
                key="upscale_denoise"
            )
            
            sharpen = st.checkbox(
                "Sharpen Details",
                value=True,
                key="upscale_sharpen"
            )
    
    with col2:
        st.markdown("**Output Settings**")
        
        output_format = st.selectbox(
            "Output Format",
            ["mp4", "mov", "webm"],
            key="upscale_format"
        )
        
        frame_rate = st.selectbox(
            "Frame Rate",
            ["24 fps", "30 fps", "60 fps"],
            index=1,
            key="upscale_fps"
        )
    
    if st.button("🚀 Upscale Video", type="primary", use_container_width=True, key="upscale_generate"):
        if not video_url:
            st.error("❌ Please provide a video URL!")
        else:
            with st.spinner("Upscaling video..."):
                input_params = {
                    "video_url": video_url,
                    "upscale_factor": upscale_factor,
                    "enhance_faces": enhance_faces,
                    "denoise": denoise,
                    "sharpen": sharpen,
                    "output_format": output_format,
                    "frame_rate": int(frame_rate.split()[0])
                }
                
                task_id = base_client.create_task("video/upscale", input_params)
                
                if task_id:
                    st.success(f"✅ Task created! Task ID: `{task_id}`")
                    st.info("💡 Upscaling may take several minutes depending on video length.")
                else:
                    st.error("❌ Failed to create task")

# --- Tab 3: Style Transfer ---
with tab3:
    st.header("🎨 AI Style Transfer")
    st.markdown("Apply artistic styles to images or videos.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        content_type = st.radio(
            "Content Type",
            ["Image", "Video"],
            horizontal=True,
            key="style_type"
        )
        
        content_url = st.text_input(
            f"{content_type} URL",
            placeholder=f"https://example.com/{'image.jpg' if content_type == 'Image' else 'video.mp4'}",
            key="style_content_url"
        )
        
        # Style selection
        st.markdown("**Style Selection**")
        
        style_method = st.radio(
            "Style Method",
            ["Preset Style", "Reference Image"],
            horizontal=True,
            key="style_method"
        )
        
        if style_method == "Preset Style":
            preset_style = st.selectbox(
                "Choose Style",
                [
                    "Van Gogh - Starry Night",
                    "Picasso - Cubism",
                    "Monet - Impressionism",
                    "Anime - Studio Ghibli",
                    "Watercolor",
                    "Oil Painting",
                    "Sketch - Pencil Drawing",
                    "Pop Art - Warhol",
                    "Cyberpunk Neon",
                    "Minimalist Modern"
                ],
                key="style_preset"
            )
        else:
            style_image_url = st.text_input(
                "Style Reference Image URL",
                placeholder="https://example.com/style.jpg",
                key="style_reference"
            )
    
    with col2:
        st.markdown("**Style Parameters**")
        
        style_strength = st.slider(
            "Style Strength",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="How strongly to apply the style",
            key="style_strength"
        )
        
        preserve_content = st.slider(
            "Preserve Content",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="How much to preserve original content",
            key="style_preserve"
        )
        
        if content_type == "Video":
            temporal_consistency = st.checkbox(
                "Temporal Consistency",
                value=True,
                help="Maintain consistency across frames",
                key="style_temporal"
            )
    
    if st.button("🚀 Apply Style Transfer", type="primary", use_container_width=True, key="style_generate"):
        if not content_url:
            st.error(f"❌ Please provide a {content_type.lower()} URL!")
        elif style_method == "Reference Image" and not style_image_url:
            st.error("❌ Please provide a style reference image URL!")
        else:
            with st.spinner(f"Applying style to {content_type.lower()}..."):
                input_params = {
                    "content_url": content_url,
                    "content_type": content_type.lower(),
                    "style_strength": style_strength,
                    "preserve_content": preserve_content
                }
                
                if style_method == "Preset Style":
                    input_params["style_preset"] = preset_style
                else:
                    input_params["style_image_url"] = style_image_url
                
                if content_type == "Video":
                    input_params["temporal_consistency"] = temporal_consistency
                
                model = "style-transfer/image" if content_type == "Image" else "style-transfer/video"
                task_id = base_client.create_task(model, input_params)
                
                if task_id:
                    st.success(f"✅ Task created! Task ID: `{task_id}`")
                    st.info("💡 Style transfer processing time varies by content size.")
                else:
                    st.error("❌ Failed to create task")

# --- Tab 4: Batch Processing ---
with tab4:
    st.header("📦 Batch Processing")
    st.markdown("Process multiple items with the same settings.")
    
    st.markdown("**Batch Configuration**")
    
    batch_type = st.selectbox(
        "Processing Type",
        [
            "Image Generation",
            "Image Editing",
            "Video Generation",
            "Style Transfer"
        ],
        key="batch_type"
    )
    
    st.divider()
    
    # Input method
    input_method = st.radio(
        "Input Method",
        ["Text List", "CSV Upload", "Google Drive Folder"],
        horizontal=True,
        key="batch_input_method"
    )
    
    prompts_list = []
    
    if input_method == "Text List":
        prompts_text = st.text_area(
            "Enter prompts (one per line)",
            placeholder="Prompt 1\nPrompt 2\nPrompt 3",
            height=200,
            key="batch_prompts"
        )
        if prompts_text:
            prompts_list = [p.strip() for p in prompts_text.split('\n') if p.strip()]
    
    elif input_method == "CSV Upload":
        csv_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="CSV should have a 'prompt' column",
            key="batch_csv"
        )
        if csv_file:
            import pandas as pd
            df = pd.read_csv(csv_file)
            if 'prompt' in df.columns:
                prompts_list = df['prompt'].tolist()
                st.success(f"✅ Loaded {len(prompts_list)} prompts from CSV")
            else:
                st.error("❌ CSV must have a 'prompt' column")
    
    else:  # Google Drive Folder
        if st.session_state.get('credentials_loaded', False):
            st.info("📁 This will process all text files in the selected folder as prompts")
            # Implementation would list folders and read text files
        else:
            st.warning("⚠️ Please configure Google Drive credentials first")
    
    if prompts_list:
        st.success(f"📝 Ready to process {len(prompts_list)} items")
        
        # Batch settings
        col_batch1, col_batch2 = st.columns(2)
        
        with col_batch1:
            batch_delay = st.number_input(
                "Delay between requests (seconds)",
                min_value=0,
                max_value=60,
                value=2,
                help="Prevent rate limiting",
                key="batch_delay"
            )
        
        with col_batch2:
            auto_save_batch = st.checkbox(
                "Auto-save all results",
                value=True,
                key="batch_auto_save"
            )
        
        if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True, key="batch_start"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            task_ids = []
            
            for idx, prompt in enumerate(prompts_list):
                status_text.text(f"Processing {idx + 1}/{len(prompts_list)}: {prompt[:50]}...")
                
                # Create task based on batch type
                input_params = {"prompt": prompt}
                
                if batch_type == "Image Generation":
                    model = "qwen/image-edit"
                elif batch_type == "Video Generation":
                    model = "veo-3.1"
                else:
                    model = "qwen/image-edit"
                
                task_id = base_client.create_task(model, input_params)
                
                if task_id:
                    task_ids.append({"prompt": prompt, "task_id": task_id})
                
                progress_bar.progress((idx + 1) / len(prompts_list))
                
                if idx < len(prompts_list) - 1:
                    time.sleep(batch_delay)
            
            status_text.text("✅ Batch processing initiated!")
            
            st.success(f"🎉 Created {len(task_ids)} tasks successfully!")
            
            # Display task IDs
            st.markdown("**Task IDs:**")
            for item in task_ids:
                st.code(f"{item['task_id']} - {item['prompt'][:50]}...")
            
            # Save to session state
            if "batch_history" not in st.session_state:
                st.session_state.batch_history = []
            st.session_state.batch_history.append({
                "type": batch_type,
                "count": len(task_ids),
                "tasks": task_ids
            })

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🎯 Advanced Features")
    st.markdown("""
    **Image-to-Video**
    - Animate static images
    - Control motion intensity
    - Custom camera movements
    
    **Video Upscaling**
    - 2x or 4x resolution
    - AI-powered enhancement
    - Face and detail improvement
    
    **Style Transfer**
    - Artistic style application
    - Preset or custom styles
    - Image and video support
    
    **Batch Processing**
    - Process multiple items
    - CSV import support
    - Automated workflows
    """)
    
    st.divider()
    
    if "batch_history" in st.session_state and st.session_state.batch_history:
        st.markdown("### 📊 Batch History")
        for idx, batch in enumerate(reversed(st.session_state.batch_history[-5:])):
            st.markdown(f"**Batch {len(st.session_state.batch_history) - idx}**")
            st.markdown(f"Type: {batch['type']}")
            st.markdown(f"Items: {batch['count']}")
            st.divider()
