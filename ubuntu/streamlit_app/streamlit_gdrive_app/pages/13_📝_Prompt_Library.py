"""
Prompt Library - Browse and use curated prompts for better generation results
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_api import get_prompt_collection, search_prompts, get_random_prompt

# --- Page Configuration ---
st.set_page_config(
    page_title="Prompt Library",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Prompt Library")
st.markdown("""
Browse our curated collection of professional prompts to enhance your AI generations.
Copy prompts directly or use them as inspiration for your own creations.
""")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Browse by Category", "Search Prompts", "Random Inspiration"])

# --- Tab 1: Browse by Category ---
with tab1:
    st.header("Browse Prompt Categories")
    
    prompt_collection = get_prompt_collection()
    
    # Category selector
    categories = list(prompt_collection.keys())
    category_names = [prompt_collection[cat]["name"] for cat in categories]
    
    selected_category_name = st.selectbox(
        "Select a category",
        category_names,
        key="category_selector"
    )
    
    # Find the category key
    selected_category = categories[category_names.index(selected_category_name)]
    category_data = prompt_collection[selected_category]
    
    st.markdown(f"**{category_data['description']}**")
    st.divider()
    
    # Display prompts in the category
    for idx, prompt_data in enumerate(category_data["prompts"]):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(prompt_data["title"])
                st.code(prompt_data["prompt"], language="text")
                
                # Tags
                tags_html = " ".join([f'<span style="background-color: #e0e0e0; padding: 2px 8px; border-radius: 12px; margin-right: 4px; font-size: 12px;">{tag}</span>' for tag in prompt_data["tags"]])
                st.markdown(tags_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Actions**")
                
                # Copy button
                if st.button("📋 Copy", key=f"copy_{selected_category}_{idx}", use_container_width=True):
                    st.session_state.clipboard = prompt_data["prompt"]
                    st.success("Copied!")
                
                # Use in generator
                if st.button("🎬 Use in Video", key=f"video_{selected_category}_{idx}", use_container_width=True):
                    st.session_state.video_prompt = prompt_data["prompt"]
                    st.success("Prompt loaded! Go to Video Generator.")
                
                if st.button("🖼️ Use in Image", key=f"image_{selected_category}_{idx}", use_container_width=True):
                    st.session_state.image_prompt = prompt_data["prompt"]
                    st.success("Prompt loaded! Go to API Testing.")

# --- Tab 2: Search Prompts ---
with tab2:
    st.header("Search Prompts")
    
    col_search1, col_search2 = st.columns([3, 1])
    
    with col_search1:
        search_query = st.text_input(
            "Search by keyword or tag",
            placeholder="e.g., cinematic, dramatic, neon, etc.",
            key="search_input"
        )
    
    with col_search2:
        search_category = st.selectbox(
            "Filter by category",
            ["All Categories"] + category_names,
            key="search_category"
        )
    
    if search_query:
        # Perform search
        category_filter = None if search_category == "All Categories" else categories[category_names.index(search_category)]
        
        results = search_prompts(search_query, category_filter)
        
        if results:
            st.success(f"Found {len(results)} matching prompt(s)")
            
            for idx, result in enumerate(results):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{result['title']}** <span style='color: gray; font-size: 12px;'>({result['category_name']})</span>", unsafe_allow_html=True)
                        st.code(result["prompt"], language="text")
                        
                        # Tags
                        tags_html = " ".join([f'<span style="background-color: #e0e0e0; padding: 2px 8px; border-radius: 12px; margin-right: 4px; font-size: 12px;">{tag}</span>' for tag in result["tags"]])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Actions**")
                        
                        if st.button("📋 Copy", key=f"search_copy_{idx}", use_container_width=True):
                            st.session_state.clipboard = result["prompt"]
                            st.success("Copied!")
                        
                        if st.button("🎬 Use in Video", key=f"search_video_{idx}", use_container_width=True):
                            st.session_state.video_prompt = result["prompt"]
                            st.success("Prompt loaded!")
                        
                        if st.button("🖼️ Use in Image", key=f"search_image_{idx}", use_container_width=True):
                            st.session_state.image_prompt = result["prompt"]
                            st.success("Prompt loaded!")
        else:
            st.info("No prompts found matching your search.")
    else:
        st.info("Enter a search query to find prompts.")

# --- Tab 3: Random Inspiration ---
with tab3:
    st.header("Random Prompt Inspiration")
    st.markdown("Get random prompts for creative inspiration!")
    
    col_random1, col_random2 = st.columns([2, 1])
    
    with col_random1:
        random_category = st.selectbox(
            "Category (optional)",
            ["All Categories"] + category_names,
            key="random_category"
        )
    
    with col_random2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_random = st.button("🎲 Get Random Prompt", use_container_width=True, type="primary")
    
    if generate_random or "random_prompt" not in st.session_state:
        category_filter = None if random_category == "All Categories" else categories[category_names.index(random_category)]
        st.session_state.random_prompt = get_random_prompt(category_filter)
    
    if "random_prompt" in st.session_state:
        random_prompt = st.session_state.random_prompt
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(random_prompt["title"])
                st.markdown(f"*Category: {random_prompt['category_name']}*")
                st.code(random_prompt["prompt"], language="text")
                
                # Tags
                tags_html = " ".join([f'<span style="background-color: #e0e0e0; padding: 2px 8px; border-radius: 12px; margin-right: 4px; font-size: 12px;">{tag}</span>' for tag in random_prompt["tags"]])
                st.markdown(tags_html, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Actions**")
                
                if st.button("📋 Copy", key="random_copy", use_container_width=True):
                    st.session_state.clipboard = random_prompt["prompt"]
                    st.success("Copied!")
                
                if st.button("🎬 Use in Video", key="random_video", use_container_width=True):
                    st.session_state.video_prompt = random_prompt["prompt"]
                    st.success("Prompt loaded! Go to Video Generator.")
                
                if st.button("🖼️ Use in Image", key="random_image", use_container_width=True):
                    st.session_state.image_prompt = random_prompt["prompt"]
                    st.success("Prompt loaded! Go to API Testing.")

# --- Sidebar: Prompt Tips ---
with st.sidebar:
    st.markdown("### 💡 Prompt Writing Tips")
    st.markdown("""
    **Be Specific**
    - Include details about style, lighting, and mood
    - Mention camera angles and movements
    - Specify quality (4K, 8K, professional)
    
    **Use Modifiers**
    - Lighting: golden hour, neon, dramatic
    - Style: cinematic, photorealistic, animated
    - Mood: peaceful, epic, mysterious
    
    **Combine Prompts**
    - Mix multiple prompt elements
    - Layer different categories
    - Create unique combinations
    
    **Iterate**
    - Start with a template
    - Modify and refine
    - Experiment with variations
    """)
    
    st.divider()
    
    st.markdown("### 📚 Quick Stats")
    total_prompts = sum(len(cat["prompts"]) for cat in prompt_collection.values())
    st.metric("Total Prompts", total_prompts)
    st.metric("Categories", len(prompt_collection))
    
    st.divider()
    
    if "clipboard" in st.session_state:
        st.markdown("### 📋 Clipboard")
        st.text_area("Last copied prompt", st.session_state.clipboard, height=100, disabled=True)
