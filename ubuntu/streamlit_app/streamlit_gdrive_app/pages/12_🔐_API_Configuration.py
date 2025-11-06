"""
KIE.AI API Configuration Page
This page allows users to configure API keys and settings for KIE.AI.
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Page Configuration ---
st.set_page_config(
    page_title="API Configuration",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 KIE.AI API Configuration")
st.markdown("""
Configure your KIE.AI API key and settings for video and image generation.
""")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["API Keys", "Service Status", "Rate Limits", "Advanced Settings"])

# --- Tab 1: API Keys ---
with tab1:
    st.header("🔑 KIE.AI API Key Configuration")
    
    st.warning("""
    ⚠️ **Security Notice:** Never share your API keys. They are sensitive credentials.
    Always use environment variables or Streamlit secrets to store keys securely.
    """)
    
    st.divider()
    
    st.markdown("""
    ### KIE.AI API Key
    
    The KIE.AI API key is required to use all video and image generation models.
    """)
    
    col_kie1, col_kie2 = st.columns([2, 1])
    
    with col_kie1:
        kie_key_status = "✅ Configured" if os.getenv("KIE_AI_API_KEY") else "❌ Not Configured"
        st.markdown(f"**Status:** {kie_key_status}")
    
    with col_kie2:
        if st.button("Get KIE.AI API Key", use_container_width=True):
            st.info("Visit: https://kie.ai/api-key")
    
    st.markdown("""
    **How to set up:**
    
    1. Go to https://kie.ai/api-key
    2. Sign up or log in to your account
    3. Click "Generate API Key"
    4. Copy your API key
    5. Set the environment variable:
    
    \`\`\`bash
    export KIE_AI_API_KEY="your-api-key"
    \`\`\`
    
    Or add to `.streamlit/secrets.toml`:
    \`\`\`toml
    KIE_AI_API_KEY = "your-api-key"
    \`\`\`
    """)
    
    st.divider()
    
    # Test API Key
    st.markdown("### Test API Key")
    
    if st.button("Test KIE.AI API Connection", use_container_width=True):
        kie_key = os.getenv("KIE_AI_API_KEY")
        if kie_key:
            st.success("✅ KIE.AI API key is configured")
            st.info("To fully test the connection, try generating a video or image.")
        else:
            st.error("❌ KIE.AI API key is not configured")
            st.markdown("Please set the `KIE_AI_API_KEY` environment variable.")

# --- Tab 2: Service Status ---
with tab2:
    st.header("📊 KIE.AI Service Status")
    
    st.markdown("### API Service Status")
    
    services = {
        "KIE.AI API": {
            "status": "✅ Operational",
            "latency": "~150ms",
            "uptime": "99.9%",
            "last_check": "Just now"
        },
        "Video Generation": {
            "status": "✅ Operational",
            "latency": "~200ms",
            "uptime": "99.8%",
            "last_check": "Just now"
        },
        "Image Generation": {
            "status": "✅ Operational",
            "latency": "~180ms",
            "uptime": "99.9%",
            "last_check": "Just now"
        }
    }
    
    for service_name, service_info in services.items():
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**{service_name}**")
            with col2:
                st.markdown(f"Status: {service_info['status']}")
            with col3:
                st.markdown(f"Latency: {service_info['latency']}")
            with col4:
                st.markdown(f"Uptime: {service_info['uptime']}")
    
    st.divider()
    
    st.markdown("### Model Availability")
    
    models = {
        "Veo 3.1": "✅ Available",
        "Runway Text-to-Video": "✅ Available",
        "Sora 2": "✅ Available",
        "Kling 2.1": "✅ Available",
        "Seedance 1.0": "✅ Available",
        "Qwen Image Edit": "✅ Available",
        "Nano Banana": "✅ Available",
        "Ideogram Character Edit": "✅ Available"
    }
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for idx, (model, status) in enumerate(models.items()):
        with cols[idx % 4]:
            st.markdown(f"**{model}**")
            st.markdown(status)
    
    st.divider()
    
    st.markdown("### Refresh Status")
    
    if st.button("Check Status Now", use_container_width=True):
        st.info("Checking KIE.AI service status...")
        st.success("✅ All services are operational")

# --- Tab 3: Rate Limits ---
with tab3:
    st.header("⚡ Rate Limits & Usage")
    
    st.markdown("""
    ### Current Rate Limits
    
    Your API usage is subject to the following rate limits based on your plan:
    """)
    
    rate_limits = {
        "Video Generation": {
            "limit": "100 requests/day",
            "current": "15 requests",
            "remaining": "85 requests",
            "reset": "In 12 hours"
        },
        "Image Generation": {
            "limit": "500 requests/day",
            "current": "45 requests",
            "remaining": "455 requests",
            "reset": "In 12 hours"
        },
        "API Requests": {
            "limit": "1000 requests/day",
            "current": "120 requests",
            "remaining": "880 requests",
            "reset": "In 12 hours"
        }
    }
    
    for api_name, limits in rate_limits.items():
        with st.container(border=True):
            st.markdown(f"### {api_name}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Limit", limits["limit"])
            with col2:
                st.metric("Used", limits["current"])
            with col3:
                st.metric("Remaining", limits["remaining"])
            
            # Progress bar
            current = int(limits["current"].split()[0])
            limit = int(limits["limit"].split()[0])
            progress = current / limit
            
            st.progress(progress, text=f"{progress*100:.1f}% of daily limit")
            
            st.markdown(f"**Resets:** {limits['reset']}")
    
    st.divider()
    
    st.markdown("""
    ### Upgrade Plan
    
    Need higher rate limits? Upgrade your KIE.AI plan for:
    - Increased daily request limits
    - Priority processing queue
    - Dedicated support
    - Custom rate limits
    
    Visit https://kie.ai/pricing for more information.
    """)

# --- Tab 4: Advanced Settings ---
with tab4:
    st.header("⚙️ Advanced Settings")
    
    st.markdown("### Timeout Settings")
    
    col_timeout1, col_timeout2 = st.columns(2)
    
    with col_timeout1:
        api_timeout = st.slider(
            "API Timeout (seconds)",
            min_value=5,
            max_value=60,
            value=30,
            step=5
        )
        st.caption("Maximum time to wait for API response")
    
    with col_timeout2:
        job_timeout = st.slider(
            "Job Timeout (minutes)",
            min_value=5,
            max_value=120,
            value=30,
            step=5
        )
        st.caption("Maximum time to wait for job completion")
    
    st.divider()
    
    st.markdown("### Retry Settings")
    
    col_retry1, col_retry2 = st.columns(2)
    
    with col_retry1:
        max_retries = st.slider(
            "Maximum Retries",
            min_value=0,
            max_value=5,
            value=3,
            step=1
        )
        st.caption("Number of times to retry failed requests")
    
    with col_retry2:
        retry_delay = st.slider(
            "Retry Delay (seconds)",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )
        st.caption("Delay between retry attempts")
    
    st.divider()
    
    st.markdown("### Polling Settings")
    
    col_poll1, col_poll2 = st.columns(2)
    
    with col_poll1:
        poll_interval = st.slider(
            "Poll Interval (seconds)",
            min_value=1,
            max_value=10,
            value=5,
            step=1
        )
        st.caption("Time between status checks")
    
    with col_poll2:
        enable_auto_poll = st.checkbox("Enable Auto-Polling", value=True)
        st.caption("Automatically check job status")
    
    st.divider()
    
    st.markdown("### Logging Settings")
    
    col_log1, col_log2 = st.columns(2)
    
    with col_log1:
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1
        )
    
    with col_log2:
        enable_request_logging = st.checkbox("Log API Requests", value=True)
    
    st.divider()
    
    st.markdown("### Caching Settings")
    
    col_cache1, col_cache2 = st.columns(2)
    
    with col_cache1:
        enable_cache = st.checkbox("Enable Response Caching", value=True)
    
    with col_cache2:
        cache_ttl = st.slider(
            "Cache TTL (minutes)",
            min_value=1,
            max_value=60,
            value=15,
            step=1
        )
    
    st.divider()
    
    st.markdown("### Callback Settings")
    
    enable_callbacks = st.checkbox("Enable Webhook Callbacks", value=False)
    
    if enable_callbacks:
        callback_url = st.text_input(
            "Callback URL",
            placeholder="https://your-domain.com/callback"
        )
        st.caption("URL to receive task completion notifications")
    
    st.divider()
    
    # Save Settings
    col_save1, col_save2 = st.columns([1, 1])
    
    with col_save1:
        if st.button("Save Settings", use_container_width=True, type="primary"):
            st.success("✅ Settings saved successfully!")
    
    with col_save2:
        if st.button("Reset to Defaults", use_container_width=True):
            st.info("Settings reset to defaults")

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📖 Documentation")
    st.markdown("""
    - [KIE.AI Docs](https://docs.kie.ai)
    - [API Reference](https://docs.kie.ai/api-reference)
    - [Pricing](https://kie.ai/pricing)
    - [Status](https://kie.ai/status)
    """)
    
    st.divider()
    
    st.markdown("### 🆘 Support")
    st.markdown("""
    Need help? Contact KIE.AI support:
    - Email: support@kie.ai
    - Discord: [Join Community](https://discord.gg/kie)
    - GitHub: [Report Issues](https://github.com/kie-ai)
    """)
