"""
Style Mixer - Combine multiple style elements for unique results
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_helper import BaseAPIClient

# --- Page Configuration ---
st.set_page_config(
    page_title="Style Mixer",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Style Mixer")
st.markdown("""
Create unique visual styles by mixing and matching different artistic elements.
Combine lighting, color palettes, camera techniques, and artistic styles.
""")

# --- Style Categories ---
STYLE_ELEMENTS = {
    "Lighting": [
        "Golden hour warm glow",
        "Neon cyberpunk lighting",
        "Soft studio lighting",
        "Dramatic noir shadows",
        "Natural window light",
        "Volumetric god rays",
        "Blue hour twilight",
        "Harsh midday sun",
        "Candlelit ambiance",
        "LED strip accents"
    ],
    "Color Palette": [
        "Vibrant saturated colors",
        "Muted pastel tones",
        "Monochromatic black and white",
        "Warm orange and teal",
        "Cool blue and purple",
        "Earth tones natural",
        "Neon pink and cyan",
        "Vintage sepia",
        "High contrast",
        "Desaturated cinematic"
    ],
    "Camera Style": [
        "Wide-angle epic",
        "Intimate close-up",
        "Aerial drone view",
        "Handheld documentary",
        "Smooth steadicam",
        "Static locked-off",
        "Slow motion 120fps",
        "Time-lapse accelerated",
        "POV first-person",
        "Dutch angle tilted"
    ],
    "Artistic Style": [
        "Photorealistic",
        "Oil painting",
        "Watercolor",
        "Anime illustration",
        "3D rendered",
        "Sketch drawing",
        "Pop art",
        "Impressionist",
        "Minimalist",
        "Surrealist"
    ],
    "Mood": [
        "Epic and dramatic",
        "Peaceful and serene",
        "Mysterious and dark",
        "Energetic and vibrant",
        "Melancholic and somber",
        "Romantic and dreamy",
        "Tense and suspenseful",
        "Joyful and uplifting",
        "Nostalgic and vintage",
        "Futuristic and sleek"
    ],
    "Quality": [
        "8K ultra HD",
        "4K cinematic",
        "Film grain texture",
        "Sharp crystal clear",
        "Soft focus dreamy",
        "Professional grade",
        "IMAX quality",
        "Anamorphic widescreen",
        "RAW uncompressed",
        "HDR high dynamic range"
    ]
}

# --- Style Mixer Interface ---
st.header("Mix Your Style Elements")

selected_styles = {}

cols = st.columns(3)

for idx, (category, options) in enumerate(STYLE_ELEMENTS.items()):
    with cols[idx % 3]:
        selected = st.selectbox(
            f"🎯 {category}",
            ["None"] + options,
            key=f"style_{category}"
        )
        if selected != "None":
            selected_styles[category] = selected

st.divider()

# --- Base Prompt ---
st.header("Base Content Description")

base_prompt = st.text_area(
    "Describe what you want to generate",
    placeholder="e.g., A person walking through a forest, A city street at night, A product on a table...",
    height=100,
    key="base_prompt"
)

# --- Generated Prompt Preview ---
if base_prompt or selected_styles:
    st.divider()
    st.header("🎬 Generated Prompt")
    
    # Construct the full prompt
    prompt_parts = [base_prompt] if base_prompt else []
    
    for category, style in selected_styles.items():
        prompt_parts.append(style)
    
    full_prompt = ", ".join(prompt_parts)
    
    st.code(full_prompt, language="text")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📋 Copy Prompt", use_container_width=True):
            st.session_state.clipboard = full_prompt
            st.success("✅ Copied to clipboard!")
    
    with col_action2:
        if st.button("🎬 Use in Video Generator", use_container_width=True):
            st.session_state.video_prompt = full_prompt
            st.success("✅ Loaded! Go to Video Generator.")
    
    with col_action3:
        if st.button("🖼️ Use in Image Generator", use_container_width=True):
            st.session_state.image_prompt = full_prompt
            st.success("✅ Loaded! Go to API Testing.")

# --- Style Presets ---
st.divider()
st.header("🎨 Style Presets")

st.markdown("Quick-load popular style combinations:")

preset_cols = st.columns(4)

PRESETS = {
    "Cinematic Film": {
        "Lighting": "Golden hour warm glow",
        "Color Palette": "Warm orange and teal",
        "Camera Style": "Wide-angle epic",
        "Artistic Style": "Photorealistic",
        "Mood": "Epic and dramatic",
        "Quality": "4K cinematic"
    },
    "Cyberpunk Neon": {
        "Lighting": "Neon cyberpunk lighting",
        "Color Palette": "Neon pink and cyan",
        "Camera Style": "Handheld documentary",
        "Artistic Style": "Photorealistic",
        "Mood": "Futuristic and sleek",
        "Quality": "8K ultra HD"
    },
    "Dreamy Watercolor": {
        "Lighting": "Soft studio lighting",
        "Color Palette": "Muted pastel tones",
        "Camera Style": "Intimate close-up",
        "Artistic Style": "Watercolor",
        "Mood": "Romantic and dreamy",
        "Quality": "Soft focus dreamy"
    },
    "Documentary Real": {
        "Lighting": "Natural window light",
        "Color Palette": "Desaturated cinematic",
        "Camera Style": "Handheld documentary",
        "Artistic Style": "Photorealistic",
        "Mood": "Peaceful and serene",
        "Quality": "4K cinematic"
    },
    "Anime Style": {
        "Lighting": "Soft studio lighting",
        "Color Palette": "Vibrant saturated colors",
        "Camera Style": "Static locked-off",
        "Artistic Style": "Anime illustration",
        "Mood": "Energetic and vibrant",
        "Quality": "Sharp crystal clear"
    },
    "Noir Mystery": {
        "Lighting": "Dramatic noir shadows",
        "Color Palette": "Monochromatic black and white",
        "Camera Style": "Dutch angle tilted",
        "Artistic Style": "Photorealistic",
        "Mood": "Mysterious and dark",
        "Quality": "Film grain texture"
    },
    "Nature Documentary": {
        "Lighting": "Golden hour warm glow",
        "Color Palette": "Earth tones natural",
        "Camera Style": "Aerial drone view",
        "Artistic Style": "Photorealistic",
        "Mood": "Peaceful and serene",
        "Quality": "8K ultra HD"
    },
    "Vintage Retro": {
        "Lighting": "Harsh midday sun",
        "Color Palette": "Vintage sepia",
        "Camera Style": "Static locked-off",
        "Artistic Style": "Photorealistic",
        "Mood": "Nostalgic and vintage",
        "Quality": "Film grain texture"
    }
}

for idx, (preset_name, preset_styles) in enumerate(PRESETS.items()):
    with preset_cols[idx % 4]:
        if st.button(preset_name, use_container_width=True, key=f"preset_{idx}"):
            for category, style in preset_styles.items():
                st.session_state[f"style_{category}"] = style
            st.success(f"✅ Loaded {preset_name} preset!")
            st.rerun()

# --- Random Style Generator ---
st.divider()
st.header("🎲 Random Style Generator")

col_random1, col_random2 = st.columns([3, 1])

with col_random1:
    st.markdown("Generate a completely random style combination for creative inspiration!")

with col_random2:
    if st.button("🎲 Randomize All", use_container_width=True, type="primary"):
        import random
        for category, options in STYLE_ELEMENTS.items():
            st.session_state[f"style_{category}"] = random.choice(options)
        st.success("✅ Randomized all styles!")
        st.rerun()

# --- Sidebar: Style Guide ---
with st.sidebar:
    st.markdown("### 🎨 Style Mixing Guide")
    st.markdown("""
    **How to Mix Styles:**
    
    1. **Start with Base Content**
       - Describe what you want
       - Be specific about subject
    
    2. **Choose Lighting**
       - Sets the mood
       - Affects atmosphere
    
    3. **Pick Color Palette**
       - Defines visual tone
       - Creates cohesion
    
    4. **Select Camera Style**
       - Determines perspective
       - Affects engagement
    
    5. **Add Artistic Style**
       - Defines rendering
       - Sets visual language
    
    6. **Set Mood**
       - Emotional impact
       - Viewer feeling
    
    7. **Choose Quality**
       - Technical specs
       - Final polish
    """)
    
    st.divider()
    
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    - **Contrast is key**: Mix warm/cool
    - **Less is more**: 3-4 elements max
    - **Test variations**: Try different combos
    - **Save favorites**: Note what works
    - **Be bold**: Unexpected mixes shine
    """)
