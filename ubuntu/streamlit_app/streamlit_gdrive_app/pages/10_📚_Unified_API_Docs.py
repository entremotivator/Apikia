"""
KIE.AI API Documentation Page
This page provides comprehensive documentation for the KIE.AI API integration.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Page Configuration ---
st.set_page_config(
    page_title="KIE.AI API Documentation",
    page_icon="📚",
    layout="wide"
)

st.title("📚 KIE.AI API Documentation")
st.markdown("""
This page provides comprehensive documentation for the **KIE.AI API**, 
a unified platform for accessing multiple AI video and image generation models.
""")

# --- Tabs for Different Documentation Sections ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "API Reference",
    "Integration Guide",
    "Code Examples",
    "Troubleshooting"
])

# --- Tab 1: Overview ---
with tab1:
    st.header("🎯 Overview")
    
    st.markdown("""
    ### What is KIE.AI?
    
    **KIE.AI** is an affordable AI API platform that provides access to multiple 
    state-of-the-art video and image generation models through a single, unified interface.
    
    ### Supported Models
    
    #### Video Generation Models
    """)
    
    st.markdown("""
    | Model | Provider | Status | Max Duration | Quality |
    |-------|----------|--------|--------------|---------|
    | Veo 3.1 | Google | ✅ Available | 10 seconds | 720p-1080p |
    | Runway Text-to-Video | Runway | ✅ Available | 10 seconds | High |
    | Sora 2 | OpenAI | ✅ Available | 10 seconds | Ultra |
    | Kling 2.1 | ByteDance | ✅ Available | 10 seconds | 1080p |
    | Seedance 1.0 | ByteDance | ✅ Available | 10 seconds | High |
    """)
    
    st.markdown("""
    #### Image Generation Models
    """)
    
    st.markdown("""
    | Model | Purpose | Status |
    |-------|---------|--------|
    | Qwen Image Edit | Image editing & generation | ✅ Available |
    | Nano Banana | Fast image generation | ✅ Available |
    | Ideogram Character Edit | Character editing | ✅ Available |
    """)
    
    st.divider()
    
    st.markdown("""
    ### Key Features
    
    ✅ **Single API for All Models** - One endpoint for all generators
    
    ✅ **Affordable Pricing** - 60% cheaper than official APIs
    
    ✅ **Easy Integration** - Simple REST API
    
    ✅ **Async Processing** - Task-based generation with polling
    
    ✅ **Callback Support** - Optional webhooks for task completion
    
    ✅ **Reliable** - Enterprise-grade uptime and support
    """)

# --- Tab 2: API Reference ---
with tab2:
    st.header("📖 API Reference")
    
    st.markdown("""
    ### Authentication
    
    All API requests require a Bearer Token:
    """)
    
    st.code("""
Authorization: Bearer YOUR_KIE_AI_API_KEY
    """, language="text")
    
    st.markdown("""
    Get your API key at: https://kie.ai/api-key
    """)
    
    st.divider()
    
    st.markdown("""
    ### 1. Create Generation Task
    
    **Endpoint:** `POST https://api.kie.ai/api/v1/jobs/createTask`
    """)
    
    st.code("""
{
  "model": "veo-3.1",
  "input": {
    "prompt": "A beautiful sunset over mountains",
    "duration": 5,
    "aspect_ratio": "16:9"
  },
  "callBackUrl": "https://your-domain.com/callback"  // Optional
}
    """, language="json")
    
    st.markdown("""
    **Response:**
    """)
    
    st.code("""
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "abc123def456..."
  }
}
    """, language="json")
    
    st.divider()
    
    st.markdown("""
    ### 2. Query Task Status
    
    **Endpoint:** `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=abc123def456...`
    """)
    
    st.markdown("""
    **Response:**
    """)
    
    st.code("""
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "abc123def456...",
    "model": "veo-3.1",
    "state": "success",  // waiting, success, fail
    "resultJson": "{\\"resultUrls\\":[\\"https://...\\"]}",
    "failMsg": null,
    "costTime": 45000,  // milliseconds
    "completeTime": 1704067200000
  }
}
    """, language="json")
    
    st.divider()
    
    st.markdown("""
    ### Task States
    
    - **waiting** - Task is queued or processing
    - **success** - Task completed successfully
    - **fail** - Task failed
    """)

# --- Tab 3: Integration Guide ---
with tab3:
    st.header("🔗 Integration Guide")
    
    st.markdown("""
    ### Step 1: Get API Key
    
    1. Visit https://kie.ai/api-key
    2. Sign up or log in
    3. Generate a new API key
    4. Copy your API key
    """)
    
    st.divider()
    
    st.markdown("""
    ### Step 2: Set Environment Variable
    
    \`\`\`bash
    export KIE_AI_API_KEY="your-api-key"
    \`\`\`
    
    Or in Streamlit secrets (`.streamlit/secrets.toml`):
    \`\`\`toml
    KIE_AI_API_KEY = "your-api-key"
    \`\`\`
    """)
    
    st.divider()
    
    st.markdown("""
    ### Step 3: Initialize API Client
    
    \`\`\`python
    from unified_api import UnifiedKIEAPI
    
    api = UnifiedKIEAPI()
    \`\`\`
    """)
    
    st.divider()
    
    st.markdown("""
    ### Step 4: Generate Content
    
    \`\`\`python
    # Generate a video
    result = api.generate_video(
        model="veo-3.1",
        prompt="A cinematic sunset over mountains",
        duration=5,
        aspect_ratio="16:9"
    )
    
    task_id = result['task_id']
    \`\`\`
    """)
    
    st.divider()
    
    st.markdown("""
    ### Step 5: Check Status
    
    \`\`\`python
    # Poll for completion
    task_info = api.wait_for_completion(task_id)
    
    if task_info['state'] == 'success':
        urls = api.get_result_urls(task_info)
        print(f"Video ready: {urls[0]}")
    \`\`\`
    """)

# --- Tab 4: Code Examples ---
with tab4:
    st.header("💻 Code Examples")
    
    st.markdown("""
    ### Example 1: Simple Video Generation
    """)
    
    st.code("""
from unified_api import UnifiedKIEAPI

api = UnifiedKIEAPI()

# Generate video
result = api.generate_video(
    model="veo-3.1",
    prompt="A serene forest at sunrise with mist and birds",
    duration=5
)

print(f"Task ID: {result['task_id']}")
print(f"Status: {result['status']}")
    """, language="python")
    
    st.divider()
    
    st.markdown("""
    ### Example 2: Using Templates
    """)
    
    st.code("""
from unified_api import UnifiedKIEAPI, VIDEO_TEMPLATES

api = UnifiedKIEAPI()

# Get a template
template = VIDEO_TEMPLATES[0]

# Generate from template
result = api.generate_video(
    model=template['model'],
    prompt=template['prompt'],
    duration=template['duration']
)

print(f"Generated from template: {template['name']}")
    """, language="python")
    
    st.divider()
    
    st.markdown("""
    ### Example 3: Wait for Results
    """)
    
    st.code("""
from unified_api import UnifiedKIEAPI

api = UnifiedKIEAPI()

# Create task
result = api.generate_video(
    model="runway/text-to-video",
    prompt="A professional product showcase",
    duration=6
)

task_id = result['task_id']

# Wait for completion (max 5 minutes)
task_info = api.wait_for_completion(task_id, max_wait=300)

if task_info and task_info['state'] == 'success':
    urls = api.get_result_urls(task_info)
    print(f"✅ Video ready: {urls[0]}")
else:
    print("❌ Generation failed or timed out")
    """, language="python")
    
    st.divider()
    
    st.markdown("""
    ### Example 4: Image Generation
    """)
    
    st.code("""
from unified_api import UnifiedKIEAPI

api = UnifiedKIEAPI()

# Generate image
result = api.generate_image(
    model="qwen/image-edit",
    prompt="A professional product photo with studio lighting",
    image_size="landscape_16_9",
    num_images="1"
)

print(f"Image generation started: {result['task_id']}")
    """, language="python")

# --- Tab 5: Troubleshooting ---
with tab5:
    st.header("🔧 Troubleshooting")
    
    st.markdown("""
    ### Common Issues
    
    #### Issue 1: "API Key not configured"
    
    **Solution:**
    - Set the `KIE_AI_API_KEY` environment variable
    - Or pass the key directly: `UnifiedKIEAPI(api_key="your-key")`
    - Get a key at: https://kie.ai/api-key
    
    #### Issue 2: "Task creation failed"
    
    **Solution:**
    - Check your API key is valid
    - Verify the model name is correct
    - Ensure prompt is not empty
    - Check your account balance
    
    #### Issue 3: "Task timeout"
    
    **Solution:**
    - Increase the `max_wait` parameter
    - Check task status manually with task ID
    - Some models take longer to process
    
    #### Issue 4: "Invalid model name"
    
    **Solution:**
    - Use one of the supported models:
      - `veo-3.1`
      - `runway/text-to-video`
      - `sora-2`
      - `qwen/image-edit`
    
    #### Issue 5: "Rate limit exceeded"
    
    **Solution:**
    - Wait before making more requests
    - Upgrade your plan for higher limits
    - Contact support for enterprise limits
    """)
    
    st.divider()
    
    st.markdown("""
    ### Getting Help
    
    - **API Documentation:** https://docs.kie.ai
    - **Status Page:** https://kie.ai/status
    - **Contact Support:** support@kie.ai
    - **Discord Community:** https://discord.gg/kie
    """)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🔗 Quick Links")
    st.markdown("""
    - [KIE.AI Website](https://kie.ai)
    - [API Documentation](https://docs.kie.ai)
    - [Get API Key](https://kie.ai/api-key)
    - [Pricing](https://kie.ai/pricing)
    - [Status](https://kie.ai/status)
    """)
    
    st.divider()
    
    st.markdown("### 📞 Support")
    st.markdown("""
    - Email: support@kie.ai
    - Discord: [Join Community](https://discord.gg/kie)
    - GitHub: [Report Issues](https://github.com/kie-ai)
    """)
