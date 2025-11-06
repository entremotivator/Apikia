"""Nano Banana Generator Page - Generate images using google/nano-banana model"""

import streamlit as st
import time
from PIL import Image
import io
import requests

st.set_page_config(
    page_title="Nano Banana Generator",
    page_icon="🍌",
    layout="wide"
)

st.title("🍌 Nano Banana Image Generator")
st.markdown("---")

# Check if API is configured
if not st.session_state.get('api_key_loaded', False):
    st.warning("⚠️ Please configure your API key in the sidebar first!")
    st.stop()

# Import API client
from api_helper import NanoBananaAPI

api_client = NanoBananaAPI(st.session_state.api_client.api_key)

# Description
st.info("🍌 **Nano Banana** is a powerful image generation model that creates stunning visuals from text prompts.")

# Input section
st.header("📝 Generation Parameters")

col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_area(
        "Prompt",
        value="A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art",
        height=150,
        help="Enter your image generation prompt (max 5000 characters)"
    )
    
    char_count = len(prompt)
    st.caption(f"Characters: {char_count}/5000")
    
    if char_count > 5000:
        st.error("⚠️ Prompt exceeds maximum length of 5000 characters!")

with col2:
    st.subheader("⚙️ Settings")
    
    image_size = st.selectbox(
        "Image Size",
        ["1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5", "21:9", "auto"],
        index=0,
        help="Select the aspect ratio for the generated image"
    )
    
    output_format = st.selectbox(
        "Output Format",
        ["png", "jpeg"],
        index=0,
        help="Select the output image format"
    )

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

if st.button("🚀 Generate Image", type="primary", use_container_width=True):
    if not prompt:
        st.error("❌ Please enter a prompt!")
    elif len(prompt) > 5000:
        st.error("❌ Prompt is too long! Maximum 5000 characters.")
    else:
        with st.spinner("Creating generation task..."):
            # Create task
            task_id = api_client.create_nano_banana_task(
                prompt=prompt,
                image_size=image_size,
                output_format=output_format
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
                    status_text.text(f"Generating image... ({int(time.time() - start_time)}s)")
                    
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
                                                file_name=f"nano_banana_{idx + 1}.{output_format}",
                                                mime=f"image/{output_format}",
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
                                                    f"nano_banana_{task_id}_{idx + 1}.{output_format}",
                                                    folder_id=folder_id,
                                                    mime_type=f"image/{output_format}"
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

# Examples section
st.markdown("---")
st.header("💡 Example Prompts")

example_prompts = [
    "A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art",
    "A photorealistic banana wearing sunglasses on a tropical beach at sunset",
    "An abstract geometric composition with bananas in neon colors, cyberpunk style",
    "A banana dressed as a superhero flying through a city skyline, comic book art",
    "A minimalist illustration of a banana on a pastel background, modern design",
    "A steampunk mechanical banana with gears and brass components, detailed rendering"
]

cols = st.columns(2)

for idx, example in enumerate(example_prompts):
    with cols[idx % 2]:
        if st.button(f"📋 Use Example {idx + 1}", key=f"example_{idx}", use_container_width=True):
            st.session_state.example_prompt = example
            st.rerun()

# Apply example if selected
if 'example_prompt' in st.session_state:
    prompt = st.session_state.example_prompt
    del st.session_state.example_prompt

# Information section
st.markdown("---")
st.header("ℹ️ About Nano Banana")

with st.expander("Model Information"):
    st.markdown("""
    **Nano Banana** (`google/nano-banana`) is an advanced image generation model that creates high-quality images from text descriptions.
    
    **Key Features:**
    - Fast generation times
    - High-quality outputs
    - Multiple aspect ratios supported
    - Flexible prompt handling (up to 5000 characters)
    """)

with st.expander("Image Size Options"):
    st.markdown("""
    | Ratio | Description | Best For |
    |-------|-------------|----------|
    | 1:1 | Square | Social media posts, avatars |
    | 9:16 | Portrait (Vertical) | Mobile screens, stories |
    | 16:9 | Landscape (Wide) | Desktop wallpapers, presentations |
    | 3:4 | Portrait | Photo prints |
    | 4:3 | Landscape | Classic displays |
    | 3:2 | Landscape | Photography standard |
    | 2:3 | Portrait | Photography standard |
    | 5:4 | Landscape | Medium format |
    | 4:5 | Portrait | Medium format |
    | 21:9 | Ultra-wide | Cinematic, panoramic |
    | auto | Automatic | Model decides best ratio |
    """)

with st.expander("Tips for Better Results"):
    st.markdown("""
    1. **Be Descriptive**: Include details about style, colors, mood, and composition
    2. **Use Art Styles**: Mention specific art styles like "digital art", "oil painting", "photorealistic"
    3. **Add Context**: Describe the setting, lighting, and atmosphere
    4. **Experiment**: Try different variations of your prompt to see what works best
    5. **Length Matters**: Longer, more detailed prompts often produce better results
    """)

st.markdown("---")
st.info("💡 **Tip:** Generated images are automatically saved to Google Drive when auto-save is enabled!")
