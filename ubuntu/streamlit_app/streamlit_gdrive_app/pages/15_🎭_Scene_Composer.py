"""
Scene Composer - Create complex multi-shot video sequences
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_helper import BaseAPIClient

# --- Page Configuration ---
st.set_page_config(
    page_title="Scene Composer",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 Scene Composer")
st.markdown("""
Create complex video sequences by composing multiple shots together.
Plan your scenes, set transitions, and generate a complete video story.
""")

# Initialize session state for scenes
if "scenes" not in st.session_state:
    st.session_state.scenes = []

# --- Scene Builder ---
st.header("Build Your Scene Sequence")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Add New Shot")
    
    shot_name = st.text_input(
        "Shot Name",
        placeholder="e.g., Opening Establishing Shot",
        key="shot_name"
    )
    
    shot_prompt = st.text_area(
        "Shot Description",
        placeholder="Describe this shot in detail...",
        height=100,
        key="shot_prompt"
    )
    
    col_shot1, col_shot2, col_shot3 = st.columns(3)
    
    with col_shot1:
        shot_duration = st.slider(
            "Duration (seconds)",
            min_value=2,
            max_value=10,
            value=5,
            key="shot_duration"
        )
    
    with col_shot2:
        shot_model = st.selectbox(
            "Model",
            ["veo-3.1", "runway/text-to-video", "sora-2"],
            key="shot_model"
        )
    
    with col_shot3:
        shot_transition = st.selectbox(
            "Transition",
            ["Cut", "Fade", "Dissolve", "Wipe"],
            key="shot_transition"
        )
    
    if st.button("➕ Add Shot to Sequence", type="primary", use_container_width=True):
        if shot_name and shot_prompt:
            st.session_state.scenes.append({
                "name": shot_name,
                "prompt": shot_prompt,
                "duration": shot_duration,
                "model": shot_model,
                "transition": shot_transition
            })
            st.success(f"✅ Added shot: {shot_name}")
            st.rerun()
        else:
            st.error("❌ Please provide both name and description")

with col2:
    st.subheader("Scene Statistics")
    
    if st.session_state.scenes:
        total_duration = sum(scene["duration"] for scene in st.session_state.scenes)
        st.metric("Total Shots", len(st.session_state.scenes))
        st.metric("Total Duration", f"{total_duration}s")
        st.metric("Estimated Cost", f"${len(st.session_state.scenes) * 0.50:.2f}")
    else:
        st.info("No shots added yet")
    
    if st.session_state.scenes:
        if st.button("🗑️ Clear All Shots", use_container_width=True):
            st.session_state.scenes = []
            st.rerun()

# --- Scene Timeline ---
if st.session_state.scenes:
    st.divider()
    st.header("Scene Timeline")
    
    for idx, scene in enumerate(st.session_state.scenes):
        with st.container(border=True):
            col_scene1, col_scene2, col_scene3 = st.columns([3, 1, 1])
            
            with col_scene1:
                st.markdown(f"### Shot {idx + 1}: {scene['name']}")
                st.markdown(f"**Prompt:** {scene['prompt']}")
                st.markdown(f"**Transition:** {scene['transition']}")
            
            with col_scene2:
                st.markdown(f"**Duration:** {scene['duration']}s")
                st.markdown(f"**Model:** {scene['model']}")
            
            with col_scene3:
                if st.button("⬆️", key=f"up_{idx}", disabled=idx==0):
                    st.session_state.scenes[idx], st.session_state.scenes[idx-1] = st.session_state.scenes[idx-1], st.session_state.scenes[idx]
                    st.rerun()
                
                if st.button("⬇️", key=f"down_{idx}", disabled=idx==len(st.session_state.scenes)-1):
                    st.session_state.scenes[idx], st.session_state.scenes[idx+1] = st.session_state.scenes[idx+1], st.session_state.scenes[idx]
                    st.rerun()
                
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.scenes.pop(idx)
                    st.rerun()
    
    st.divider()
    
    # Generate All Shots
    col_gen1, col_gen2 = st.columns([3, 1])
    
    with col_gen1:
        st.markdown("### Ready to Generate?")
        st.markdown(f"This will create {len(st.session_state.scenes)} video shots with a total duration of {sum(scene['duration'] for scene in st.session_state.scenes)} seconds.")
    
    with col_gen2:
        if st.button("🚀 Generate All Shots", type="primary", use_container_width=True, key="generate_all"):
            st.info("🎬 Batch generation feature coming soon!")
            st.markdown("For now, generate each shot individually from the Video Generator page.")

# --- Sidebar: Scene Templates ---
with st.sidebar:
    st.markdown("### 🎬 Scene Templates")
    
    if st.button("📽️ Short Film Opening", use_container_width=True):
        st.session_state.scenes = [
            {
                "name": "Establishing Wide Shot",
                "prompt": "Wide aerial shot of city at dawn, cinematic, 4K",
                "duration": 5,
                "model": "veo-3.1",
                "transition": "Fade"
            },
            {
                "name": "Street Level",
                "prompt": "Street level shot, people walking, urban atmosphere",
                "duration": 4,
                "model": "sora-2",
                "transition": "Cut"
            },
            {
                "name": "Close-up Character",
                "prompt": "Close-up of main character, emotional, cinematic lighting",
                "duration": 3,
                "model": "runway/text-to-video",
                "transition": "Dissolve"
            }
        ]
        st.rerun()
    
    if st.button("🌅 Nature Documentary", use_container_width=True):
        st.session_state.scenes = [
            {
                "name": "Mountain Vista",
                "prompt": "Majestic mountain range at sunrise, cinematic",
                "duration": 6,
                "model": "veo-3.1",
                "transition": "Fade"
            },
            {
                "name": "Wildlife Close-up",
                "prompt": "Close-up of wildlife in natural habitat",
                "duration": 5,
                "model": "sora-2",
                "transition": "Cut"
            },
            {
                "name": "Forest Walk",
                "prompt": "Walking through forest, peaceful atmosphere",
                "duration": 5,
                "model": "veo-3.1",
                "transition": "Dissolve"
            }
        ]
        st.rerun()
    
    if st.button("🎵 Music Video", use_container_width=True):
        st.session_state.scenes = [
            {
                "name": "Performance Shot",
                "prompt": "Artist performing, dramatic lighting, music video style",
                "duration": 4,
                "model": "runway/text-to-video",
                "transition": "Cut"
            },
            {
                "name": "Abstract Visual",
                "prompt": "Abstract colorful visuals, artistic, vibrant",
                "duration": 3,
                "model": "sora-2",
                "transition": "Wipe"
            },
            {
                "name": "Close-up Emotion",
                "prompt": "Close-up emotional performance, cinematic",
                "duration": 4,
                "model": "runway/text-to-video",
                "transition": "Cut"
            }
        ]
        st.rerun()
    
    st.divider()
    
    st.markdown("### 💡 Scene Tips")
    st.markdown("""
    **Composition:**
    - Start wide, go close
    - Vary shot lengths
    - Use transitions wisely
    
    **Pacing:**
    - Action: 2-4 seconds
    - Dialogue: 4-6 seconds
    - Establishing: 5-7 seconds
    
    **Transitions:**
    - Cut: Fast pacing
    - Fade: Time passage
    - Dissolve: Smooth flow
    - Wipe: Style choice
    """)
