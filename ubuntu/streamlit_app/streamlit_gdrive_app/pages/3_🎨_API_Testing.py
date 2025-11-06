"""API Testing Page - Test image editing API"""

import streamlit as st
import time
from PIL import Image
import io
import requests

st.set_page_config(
    page_title="API Testing",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Image Edit API Testing")
st.markdown("---")

# Check if API is configured
if not st.session_state.get('api_key_loaded', False):
    st.warning("⚠️ Please configure your API key in the sidebar first!")
    st.stop()

api_client = st.session_state.api_client

# Input section
st.header("📝 Input Parameters")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Image Source")
    
    image_source = st.radio(
        "Select image source",
        ["URL", "Upload from Computer", "From Google Drive"],
        index=0
    )
    
    if image_source == "URL":
        image_url = st.text_input(
            "Image URL",
            value="https://file.aiquickdraw.com/custom-page/akr/section-images/1755603225969i6j87xnw.jpg",
            help="Enter the URL of the image to edit"
        )
    elif image_source == "Upload from Computer":
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['jpg', 'jpeg', 'png', 'webp']
        )
        
        if uploaded_file:
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            
            # Upload to temporary storage to get URL
            st.info("ℹ️ Note: You'll need to upload this to a publicly accessible URL for the API to process it.")
            image_url = None
        else:
            image_url = None
    else:  # From Google Drive
        if not st.session_state.get('credentials_loaded', False):
            st.warning("⚠️ Please upload your Google Drive credentials first!")
            image_url = None
        else:
            gdrive_manager = st.session_state.gdrive_manager
            
            # List images from Google Drive
            with st.spinner("Loading images from Google Drive..."):
                files = gdrive_manager.list_files(mime_type_filter="image/")
                
                if files:
                    selected_file = st.selectbox(
                        "Select an image",
                        options=files,
                        format_func=lambda x: x['name']
                    )
                    
                    if selected_file:
                        # Display selected image
                        file_bytes = gdrive_manager.download_file(selected_file['id'])
                        if file_bytes:
                            st.image(file_bytes, caption=selected_file['name'], use_container_width=True)
                        
                        # Get web content link
                        image_url = selected_file.get('webContentLink')
                        if not image_url:
                            st.warning("⚠️ This file doesn't have a public URL. Please use URL or Upload option.")
                else:
                    st.info("📭 No images found in Google Drive")
                    image_url = None

with col2:
    st.subheader("Edit Parameters")
    
    prompt = st.text_area(
        "Prompt",
        value="",
        height=100,
        help="The prompt to generate the image with (max 2000 characters)"
    )
    
    negative_prompt = st.text_input(
        "Negative Prompt",
        value="blurry, ugly",
        help="What to avoid in the generation (max 500 characters)"
    )

# Advanced settings
st.markdown("---")
st.header("⚙️ Advanced Settings")

col1, col2, col3 = st.columns(3)

with col1:
    image_size = st.selectbox(
        "Image Size",
        ["square", "square_hd", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"],
        index=4
    )
    
    acceleration = st.selectbox(
        "Acceleration",
        ["none", "regular", "high"],
        index=0
    )

with col2:
    num_inference_steps = st.slider(
        "Inference Steps",
        min_value=2,
        max_value=49,
        value=25,
        step=1
    )
    
    guidance_scale = st.slider(
        "Guidance Scale",
        min_value=0.0,
        max_value=20.0,
        value=4.0,
        step=0.1
    )

with col3:
    output_format = st.selectbox(
        "Output Format",
        ["png", "jpeg"],
        index=0
    )
    
    enable_safety_checker = st.checkbox(
        "Enable Safety Checker",
        value=True
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

# Generate button
st.markdown("---")

if st.button("🚀 Generate Image", type="primary", use_container_width=True):
    if not image_url:
        st.error("❌ Please provide an image URL or upload an image!")
    else:
        with st.spinner("Creating task..."):
            # Prepare parameters
            params = {
                "acceleration": acceleration,
                "image_size": image_size,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "output_format": output_format,
                "negative_prompt": negative_prompt,
                "enable_safety_checker": enable_safety_checker
            }
            
            if seed is not None:
                params["seed"] = seed
            
            # Create task
            task_id = api_client.create_task(prompt, image_url, **params)
            
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
                    status_text.text(f"Waiting for results... ({int(time.time() - start_time)}s)")
                    
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
                                st.header("🖼️ Results")
                                
                                cols = st.columns(min(len(result_urls), 3))
                                
                                for idx, url in enumerate(result_urls):
                                    with cols[idx % 3]:
                                        try:
                                            # Download and display image
                                            response = requests.get(url)
                                            response.raise_for_status()
                                            
                                            img_bytes = response.content
                                            image = Image.open(io.BytesIO(img_bytes))
                                            
                                            st.image(image, caption=f"Result {idx + 1}", use_container_width=True)
                                            
                                            # Download button
                                            st.download_button(
                                                label="💾 Download",
                                                data=img_bytes,
                                                file_name=f"result_{idx + 1}.{output_format}",
                                                mime=f"image/{output_format}",
                                                key=f"download_{idx}"
                                            )
                                            
                                            # Auto-save to Google Drive
                                            if auto_save and st.session_state.get('credentials_loaded', False):
                                                gdrive_manager = st.session_state.gdrive_manager
                                                
                                                result = gdrive_manager.upload_file_from_bytes(
                                                    img_bytes,
                                                    f"api_result_{task_id}_{idx + 1}.{output_format}",
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

# Information section
st.markdown("---")
st.header("ℹ️ API Information")

with st.expander("About Image Size Options"):
    st.markdown("""
    - **square**: Square format
    - **square_hd**: Square HD format
    - **portrait_4_3**: Portrait 3:4 ratio
    - **portrait_16_9**: Portrait 9:16 ratio
    - **landscape_4_3**: Landscape 4:3 ratio
    - **landscape_16_9**: Landscape 16:9 ratio
    """)

with st.expander("About Acceleration"):
    st.markdown("""
    - **none**: No acceleration, best quality
    - **regular**: Regular acceleration, balanced speed and quality
    - **high**: High acceleration, fastest but may reduce quality
    """)

with st.expander("About Inference Steps"):
    st.markdown("""
    The number of denoising steps. More steps generally produce better quality but take longer.
    Range: 2-49, Default: 25
    """)

with st.expander("About Guidance Scale"):
    st.markdown("""
    Controls how closely the model follows your prompt. Higher values stick closer to the prompt.
    Range: 0-20, Default: 4
    """)
