"""Character Edit Generator Page - Edit characters using ideogram/character-edit model"""

import streamlit as st
import time
from PIL import Image
import io
import requests

st.set_page_config(
    page_title="Character Edit Generator",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Character Edit Generator")
st.markdown("---")

# Check if API is configured
if not st.session_state.get('api_key_loaded', False):
    st.warning("⚠️ Please configure your API key in the sidebar first!")
    st.stop()

# Import API client
from api_helper import CharacterEditAPI

api_client = CharacterEditAPI(st.session_state.api_client.api_key)

# Description
st.info("👤 **Character Edit** allows you to edit characters in images using a mask and reference images for consistent character generation.")

# Input section
st.header("📝 Input Images")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🖼️ Base Image")
    image_source = st.radio(
        "Select source",
        ["URL", "Upload"],
        key="image_source"
    )
    
    if image_source == "URL":
        image_url = st.text_input(
            "Image URL",
            value="https://file.aiquickdraw.com/custom-page/akr/section-images/17557680349256sa0lk53.webp",
            help="The image to generate from"
        )
        
        if image_url:
            try:
                st.image(image_url, caption="Base Image", use_container_width=True)
            except:
                st.error("Failed to load image")
    else:
        uploaded_image = st.file_uploader("Upload Base Image", type=['jpg', 'jpeg', 'png', 'webp'])
        if uploaded_image:
            st.image(uploaded_image, caption="Base Image", use_container_width=True)
            st.warning("⚠️ You need to upload this to a publicly accessible URL for the API")
            image_url = None
        else:
            image_url = None

with col2:
    st.subheader("🎭 Mask Image")
    mask_source = st.radio(
        "Select source",
        ["URL", "Upload"],
        key="mask_source"
    )
    
    if mask_source == "URL":
        mask_url = st.text_input(
            "Mask URL",
            value="https://file.aiquickdraw.com/custom-page/akr/section-images/1755768046014ftgvma28.webp",
            help="The mask to inpaint the image"
        )
        
        if mask_url:
            try:
                st.image(mask_url, caption="Mask Image", use_container_width=True)
            except:
                st.error("Failed to load mask")
    else:
        uploaded_mask = st.file_uploader("Upload Mask Image", type=['jpg', 'jpeg', 'png', 'webp'])
        if uploaded_mask:
            st.image(uploaded_mask, caption="Mask Image", use_container_width=True)
            st.warning("⚠️ You need to upload this to a publicly accessible URL for the API")
            mask_url = None
        else:
            mask_url = None

with col3:
    st.subheader("👥 Reference Image")
    reference_source = st.radio(
        "Select source",
        ["URL", "Upload"],
        key="reference_source"
    )
    
    if reference_source == "URL":
        reference_url = st.text_input(
            "Reference Image URL",
            value="https://file.aiquickdraw.com/custom-page/akr/section-images/1755768064644jodsmfhq.webp",
            help="Character reference image"
        )
        
        if reference_url:
            try:
                st.image(reference_url, caption="Reference Image", use_container_width=True)
            except:
                st.error("Failed to load reference")
            reference_image_urls = [reference_url]
    else:
        uploaded_reference = st.file_uploader("Upload Reference Image", type=['jpg', 'jpeg', 'png', 'webp'])
        if uploaded_reference:
            st.image(uploaded_reference, caption="Reference Image", use_container_width=True)
            st.warning("⚠️ You need to upload this to a publicly accessible URL for the API")
            reference_image_urls = []
        else:
            reference_image_urls = []

st.markdown("---")

# Prompt section
st.header("✍️ Generation Settings")

col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_area(
        "Prompt",
        value="A fabulous look head tilted down, looking forward with a smile",
        height=100,
        help="The prompt to fill the masked part of the image (max 5000 characters)"
    )
    
    char_count = len(prompt)
    st.caption(f"Characters: {char_count}/5000")
    
    if char_count > 5000:
        st.error("⚠️ Prompt exceeds maximum length of 5000 characters!")

with col2:
    st.subheader("⚙️ Advanced Settings")
    
    rendering_speed = st.selectbox(
        "Rendering Speed",
        ["TURBO", "BALANCED", "QUALITY"],
        index=1,
        help="Speed vs quality tradeoff"
    )
    
    style = st.selectbox(
        "Style",
        ["AUTO", "REALISTIC", "FICTION"],
        index=0,
        help="The style type to generate with"
    )
    
    expand_prompt = st.checkbox(
        "Expand Prompt (MagicPrompt)",
        value=True,
        help="Use MagicPrompt to enhance the prompt"
    )
    
    num_images = st.selectbox(
        "Number of Images",
        ["1", "2", "3", "4"],
        index=0,
        help="Number of images to generate"
    )
    
    use_seed = st.checkbox("Use Custom Seed", value=False)
    if use_seed:
        seed = st.number_input("Seed", min_value=0, value=42, step=1)
    else:
        seed = None

# Auto-save option
st.markdown("---")
auto_save = st.checkbox(
    "🔄 Auto-save results to Google Drive",
    value=st.session_state.get('credentials_loaded', False),
    disabled=not st.session_state.get('credentials_loaded', False)
)

if auto_save and st.session_state.get('credentials_loaded', False):
    custom_folder = st.text_input(
        "Save to folder (optional)",
        placeholder="Leave empty for default folder",
        help="Specify a custom folder name or leave empty"
    )
else:
    custom_folder = None

# Generate button
st.markdown("---")

if st.button("🚀 Generate Character Edit", type="primary", use_container_width=True):
    # Validation
    errors = []
    
    if not prompt:
        errors.append("Please enter a prompt")
    if len(prompt) > 5000:
        errors.append("Prompt is too long (max 5000 characters)")
    if not image_url:
        errors.append("Please provide a base image URL")
    if not mask_url:
        errors.append("Please provide a mask image URL")
    if not reference_image_urls:
        errors.append("Please provide at least one reference image URL")
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
    else:
        with st.spinner("Creating character edit task..."):
            # Prepare parameters
            params = {
                "rendering_speed": rendering_speed,
                "style": style,
                "expand_prompt": expand_prompt,
                "num_images": num_images
            }
            
            if seed is not None:
                params["seed"] = seed
            
            # Create task
            task_id = api_client.create_character_edit_task(
                prompt=prompt,
                image_url=image_url,
                mask_url=mask_url,
                reference_image_urls=reference_image_urls,
                **params
            )
            
            if not task_id:
                st.error("❌ Failed to create task!")
            else:
                st.success(f"✅ Task created! Task ID: {task_id}")
                
                # Wait for completion
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                max_wait = 300  # 5 minutes
                poll_interval = 3
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    status_text.text(f"Generating character edit... ({int(time.time() - start_time)}s)")
                    
                    task_info = api_client.query_task(task_id)
                    
                    if task_info:
                        state = task_info.get('state')
                        
                        if state == 'success':
                            progress_bar.progress(1.0)
                            status_text.text("✅ Generation complete!")
                            
                            # Get result URLs
                            result_urls = api_client.get_result_urls(task_info)
                            
                            if result_urls:
                                st.success(f"🎉 Generated {len(result_urls)} image(s)!")
                                
                                # Display results
                                st.header("🖼️ Generated Images")
                                
                                cols = st.columns(min(len(result_urls), 3))
                                
                                for idx, url in enumerate(result_urls):
                                    with cols[idx % 3]:
                                        try:
                                            # Download and display image
                                            response = requests.get(url)
                                            response.raise_for_status()
                                            
                                            img_bytes = response.content
                                            image = Image.open(io.BytesIO(img_bytes))
                                            
                                            st.image(image, use_container_width=True)
                                            
                                            # Download button
                                            st.download_button(
                                                label="💾 Download",
                                                data=img_bytes,
                                                file_name=f"character_edit_{idx + 1}.webp",
                                                mime="image/webp",
                                                key=f"download_{idx}",
                                                use_container_width=True
                                            )
                                            
                                            # Auto-save to Google Drive
                                            if auto_save and st.session_state.get('credentials_loaded', False):
                                                gdrive_manager = st.session_state.gdrive_manager
                                                
                                                folder_id = None
                                                if custom_folder:
                                                    folder_id = gdrive_manager.get_or_create_folder(custom_folder)
                                                
                                                result = gdrive_manager.upload_file_from_bytes(
                                                    img_bytes,
                                                    f"character_edit_{task_id}_{idx + 1}.webp",
                                                    folder_id=folder_id,
                                                    mime_type="image/webp"
                                                )
                                                
                                                if result:
                                                    st.success(f"✅ Saved to Google Drive!")
                                                else:
                                                    st.warning(f"⚠️ Failed to save to Google Drive")
                                            
                                        except Exception as e:
                                            st.error(f"Error loading image: {str(e)}")
                            else:
                                st.error("❌ No results found!")
                            
                            break
                        
                        elif state == 'fail':
                            progress_bar.progress(0.0)
                            status_text.text("❌ Generation failed!")
                            st.error(f"Task failed: {task_info.get('failMsg', 'Unknown error')}")
                            break
                        
                        else:
                            # Still waiting
                            progress = min((time.time() - start_time) / max_wait, 0.99)
                            progress_bar.progress(progress)
                    
                    time.sleep(poll_interval)
                else:
                    # Timeout
                    progress_bar.progress(0.0)
                    status_text.text("⏱️ Timeout!")
                    st.warning("⚠️ Task timeout. Please check the task status manually.")

# Information section
st.markdown("---")
st.header("ℹ️ About Character Edit")

with st.expander("How It Works"):
    st.markdown("""
    **Character Edit** uses three key inputs to generate consistent character edits:
    
    1. **Base Image**: The original image you want to edit
    2. **Mask Image**: A mask indicating which parts to regenerate (white = edit, black = keep)
    3. **Reference Image**: A character reference to maintain consistency
    
    The model will fill in the masked areas while maintaining the character's appearance from the reference image.
    """)

with st.expander("Rendering Speed Options"):
    st.markdown("""
    | Speed | Description | Best For |
    |-------|-------------|----------|
    | TURBO | Fastest generation | Quick iterations, testing |
    | BALANCED | Good balance of speed and quality | Most use cases |
    | QUALITY | Highest quality output | Final renders, important work |
    """)

with st.expander("Style Options"):
    st.markdown("""
    | Style | Description |
    |-------|-------------|
    | AUTO | Automatically determines the best style |
    | REALISTIC | Photorealistic style |
    | FICTION | Fictional/artistic style |
    """)

with st.expander("Tips for Best Results"):
    st.markdown("""
    1. **Mask Precision**: Ensure your mask accurately covers the areas you want to edit
    2. **Reference Quality**: Use high-quality reference images for better consistency
    3. **Matching Dimensions**: Base image and mask should have the same dimensions
    4. **Clear Prompts**: Be specific about what you want in the masked area
    5. **Multiple Attempts**: Try different prompts and settings for best results
    """)

st.markdown("---")
st.info("💡 **Tip:** Character Edit is perfect for maintaining character consistency across different poses and expressions!")
