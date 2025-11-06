"""
KIE.AI Video Generator Interface
This page allows users to generate videos using KIE.AI video models.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_helper import generate_video, get_video_templates, query_task

# --- Page Configuration ---
st.set_page_config(
    page_title="Video Generator",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 KIE.AI Video Generator")
st.markdown("""
Generate stunning videos using **KIE.AI** video models including Veo 3.1, Runway, and Sora 2.
Choose from pre-made templates or create custom videos with your own prompts.
""")

# --- Tabs for Different Generation Methods ---
tab1, tab2, tab3 = st.tabs(["Custom Generation", "Template Gallery", "Job Status"])

# --- Tab 1: Custom Generation ---
with tab1:
    st.header("Create Custom Video")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Model Selection
        model_options = {
            "Veo 3.1 (Google)": "veo-3.1",
            "Runway Text-to-Video": "runway/text-to-video",
            "Sora 2 (OpenAI)": "sora-2"
        }
        
        selected_model_name = st.selectbox(
            "Select Video Model",
            list(model_options.keys())
        )
        selected_model = model_options[selected_model_name]
        
        # Prompt Input
        prompt = st.text_area(
            "Video Prompt",
            placeholder="Describe the video you want to generate. Be detailed and specific for best results.",
            height=120
        )
    
    with col2:
        # Duration Selection
        duration = st.slider(
            "Video Duration (seconds)",
            min_value=1,
            max_value=10,
            value=5,
            step=1
        )
        
        # Aspect Ratio Selection
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["16:9", "9:16", "1:1", "4:3"],
            index=0
        )
    
    # Advanced Settings (Collapsible)
    with st.expander("⚙️ Advanced Settings"):
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            quality = st.selectbox(
                "Quality",
                ["Standard", "High", "Ultra"],
                index=1
            )
        
        with col_adv2:
            style = st.selectbox(
                "Style",
                ["Realistic", "Cinematic", "Animated", "Abstract"],
                index=0
            )
    
    # Generate Button
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        generate_btn = st.button(
            "🚀 Generate Video",
            key="custom_generate",
            use_container_width=True,
            type="primary"
        )
    
    with col_btn2:
        clear_btn = st.button(
            "Clear",
            key="custom_clear",
            use_container_width=True
        )
    
    # Handle Generation
    if generate_btn:
        if not prompt.strip():
            st.error("❌ Please enter a prompt for video generation.")
        else:
            with st.spinner(f"🎬 Generating video with {selected_model_name}..."):
                try:
                    result = generate_video(
                        model=selected_model,
                        prompt=prompt,
                        duration=duration,
                        aspect_ratio=aspect_ratio,
                        quality=quality,
                        style=style
                    )
                    
                    if "error" in result:
                        st.error(f"❌ Generation Failed: {result['error']}")
                    else:
                        st.success(result.get("message", "✅ Video generation initiated!"))
                        
                        # Display task information
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.markdown(f"**Task ID:** `{result.get('task_id')}`")
                        with col_info2:
                            st.markdown(f"**Model:** {result.get('model')}")
                        
                        # Store in session state for history
                        if "generation_history" not in st.session_state:
                            st.session_state.generation_history = []
                        
                        st.session_state.generation_history.append({
                            "model": selected_model,
                            "prompt": prompt,
                            "duration": duration,
                            "task_id": result.get("task_id"),
                            "result": result
                        })
                        
                        # Show how to check status
                        st.info("💡 Use the 'Job Status' tab to check the progress of your video generation.")
                
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
    if clear_btn:
        st.rerun()

# --- Tab 2: Template Gallery ---
with tab2:
    st.header("📚 Pre-made Video Templates")
    st.markdown("""
    Browse and use our curated collection of video templates. Click on any template to customize and generate.
    """)
    
    # Display Templates
    templates = get_video_templates()
    
    if templates:
        # Group templates by category
        categories = {}
        for template in templates:
            cat = template.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(template)
        
        # Create tabs for each category
        if len(categories) > 1:
            category_tabs = st.tabs(list(categories.keys()))
            
            for tab_idx, (category, cat_templates) in enumerate(categories.items()):
                with category_tabs[tab_idx]:
                    cols = st.columns(3)
                    
                    for idx, template in enumerate(cat_templates):
                        with cols[idx % 3]:
                            with st.container(border=True):
                                st.subheader(template["name"])
                                st.markdown(f"**Model:** {template['model']}")
                                st.markdown(f"**Duration:** {template['duration']}s")
                                st.markdown(f"_{template['description']}_")
                                
                                # Show prompt
                                with st.expander("View Prompt"):
                                    st.code(template["prompt"], language="text")
                                
                                # Use Template Button
                                if st.button(
                                    "Use This Template",
                                    key=f"template_{template['id']}",
                                    use_container_width=True
                                ):
                                    st.session_state.selected_template = template
                                    st.success(f"✅ Template '{template['name']}' loaded!")
        else:
            # Single category
            cols = st.columns(3)
            
            for idx, template in enumerate(templates):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.subheader(template["name"])
                        st.markdown(f"**Model:** {template['model']}")
                        st.markdown(f"**Duration:** {template['duration']}s")
                        st.markdown(f"_{template['description']}_")
                        
                        # Show prompt
                        with st.expander("View Prompt"):
                            st.code(template["prompt"], language="text")
                        
                        # Use Template Button
                        if st.button(
                            "Use This Template",
                            key=f"template_{template['id']}",
                            use_container_width=True
                        ):
                            st.session_state.selected_template = template
                            st.success(f"✅ Template '{template['name']}' loaded!")
    else:
        st.info("No templates available at the moment.")
    
    # Display Selected Template
    if "selected_template" in st.session_state:
        st.divider()
        st.subheader("🎯 Selected Template")
        template = st.session_state.selected_template
        
        col_t1, col_t2 = st.columns([2, 1])
        
        with col_t1:
            prompt = st.text_area(
                "Customize Prompt",
                value=template["prompt"],
                height=100,
                key="template_prompt"
            )
        
        with col_t2:
            duration = st.slider(
                "Duration (seconds)",
                min_value=1,
                max_value=10,
                value=template["duration"],
                key="template_duration"
            )
        
        if st.button(
            "🚀 Generate from Template",
            key="template_generate",
            use_container_width=True,
            type="primary"
        ):
            with st.spinner("🎬 Generating video from template..."):
                try:
                    result = generate_video(
                        model=template["model"],
                        prompt=prompt,
                        duration=duration
                    )
                    
                    if "error" in result:
                        st.error(f"❌ Generation Failed: {result['error']}")
                    else:
                        st.success(result.get("message", "✅ Video generation initiated!"))
                        st.markdown(f"**Task ID:** `{result.get('task_id')}`")
                        st.info("💡 Use the 'Job Status' tab to check the progress.")
                
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# --- Tab 3: Job Status ---
with tab3:
    st.header("📊 Check Job Status")
    
    st.markdown("""
    Enter a task ID to check the status of your video generation job.
    """)
    
    col_status1, col_status2 = st.columns([3, 1])
    
    with col_status1:
        task_id_input = st.text_input(
            "Task ID",
            placeholder="Enter your task ID here"
        )
    
    with col_status2:
        check_btn = st.button("Check Status", use_container_width=True, type="primary")
    
    if check_btn and task_id_input:
        with st.spinner("Checking status..."):
            task_info = query_task(task_id_input)
            
            if task_info:
                state = task_info.get("state", "unknown")
                
                col_state1, col_state2, col_state3 = st.columns(3)
                
                with col_state1:
                    if state == "success":
                        st.success(f"✅ Status: {state.upper()}")
                    elif state == "fail":
                        st.error(f"❌ Status: {state.upper()}")
                    else:
                        st.info(f"⏳ Status: {state.upper()}")
                
                with col_state2:
                    st.markdown(f"**Task ID:** `{task_info.get('taskId')}`")
                
                with col_state3:
                    st.markdown(f"**Model:** {task_info.get('model')}")
                
                st.divider()
                
                # Show detailed information
                st.markdown("### Task Details")
                
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.markdown(f"**Created:** {task_info.get('createTime')}")
                    if task_info.get('completeTime'):
                        st.markdown(f"**Completed:** {task_info.get('completeTime')}")
                
                with col_detail2:
                    if task_info.get('costTime'):
                        st.markdown(f"**Processing Time:** {task_info.get('costTime')}ms")
                
                # Show results if available
                if state == "success":
                    st.divider()
                    st.markdown("### Results")
                    
                    result_json_str = task_info.get("resultJson", "{}")
                    try:
                        import json
                        result_json = json.loads(result_json_str)
                        result_urls = result_json.get("resultUrls", [])
                        
                        if result_urls:
                            for url in result_urls:
                                st.markdown(f"[📥 Download Video]({url})")
                                st.video(url)
                    except:
                        st.code(result_json_str)
                
                # Show error if failed
                if state == "fail":
                    st.divider()
                    st.markdown("### Error Information")
                    st.error(f"**Error:** {task_info.get('failMsg')}")
                    st.code(f"Error Code: {task_info.get('failCode')}")
            else:
                st.error("❌ Could not retrieve task information. Please check the task ID.")
    
    st.divider()
    
    # Display recent jobs from session state
    if "generation_history" in st.session_state and st.session_state.generation_history:
        st.markdown("### Recent Generation Jobs")
        
        for idx, job in enumerate(reversed(st.session_state.generation_history)):
            with st.expander(f"Job {idx + 1}: {job['model']}"):
                st.markdown(f"**Prompt:** {job['prompt']}")
                st.markdown(f"**Task ID:** `{job['task_id']}`")
                st.markdown(f"**Duration:** {job['duration']}s")
                
                if st.button("Check This Job", key=f"check_job_{idx}"):
                    task_info = query_task(job['task_id'])
                    if task_info:
                        st.json(task_info)

# --- Sidebar Information ---
with st.sidebar:
    st.markdown("### 🎥 Available Models")
    st.markdown("""
    **Veo 3.1** (Google)
    - High-quality, realistic video generation
    - Up to 10 seconds
    - Excellent for cinematic content
    
    **Runway Text-to-Video**
    - Professional video generation
    - Up to 10 seconds
    - Great for creative projects
    
    **Sora 2** (OpenAI)
    - Advanced motion and physics
    - Up to 10 seconds
    - Complex scene understanding
    """)
    
    st.divider()
    
    st.markdown("### ⚡ Tips for Better Results")
    st.markdown("""
    1. **Be Specific:** Include details about lighting, camera movement, and style
    2. **Use Adjectives:** Words like "cinematic," "hyper-realistic," "fast-paced" help
    3. **Describe Motion:** Specify camera angles and object movements
    4. **Set the Scene:** Mention environment, time of day, and atmosphere
    5. **Quality Keywords:** Use terms like "4K," "professional," "high-fidelity"
    """)
    
    st.divider()
    
    st.markdown("### 📚 Documentation")
    st.markdown("[KIE.AI API Docs](https://docs.kie.ai/)")
