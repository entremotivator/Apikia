"""
Job Monitor Page
This page allows users to monitor and manage their video generation jobs.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Page Configuration ---
st.set_page_config(
    page_title="Job Monitor",
    page_icon="⏱️",
    layout="wide"
)

st.title("⏱️ Video Generation Job Monitor")
st.markdown("""
Monitor the status of your video generation jobs, view results, and manage your generation history.
""")

# --- Initialize Session State ---
if "jobs" not in st.session_state:
    st.session_state.jobs = {}

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Active Jobs", "Completed Jobs", "Job Statistics"])

# --- Tab 1: Active Jobs ---
with tab1:
    st.header("🔄 Active Jobs")
    
    active_jobs = {
        job_id: job for job_id, job in st.session_state.jobs.items()
        if job.get("status") in ["pending", "processing"]
    }
    
    if active_jobs:
        for job_id, job in active_jobs.items():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Job ID:** `{job_id}`")
                    st.markdown(f"**Generator:** {job.get('generator', 'Unknown')}")
                    st.markdown(f"**Status:** {job.get('status', 'Unknown').upper()}")
                    st.markdown(f"**Created:** {job.get('created_at', 'N/A')}")
                
                with col2:
                    progress = job.get("progress", 0)
                    st.progress(progress / 100, text=f"{progress}%")
                
                with col3:
                    if st.button("Cancel", key=f"cancel_{job_id}"):
                        st.session_state.jobs[job_id]["status"] = "cancelled"
                        st.rerun()
                    
                    if st.button("Refresh", key=f"refresh_{job_id}"):
                        # In a real app, this would query the API
                        st.info("Status refreshed (simulated)")
    else:
        st.info("No active jobs at the moment.")
    
    st.divider()
    
    st.markdown("""
    ### Add New Job
    
    Manually track a job by entering its ID:
    """)
    
    col_add1, col_add2 = st.columns([3, 1])
    
    with col_add1:
        job_id_input = st.text_input("Job ID", placeholder="Enter job ID to track")
    
    with col_add2:
        if st.button("Add Job", use_container_width=True):
            if job_id_input:
                st.session_state.jobs[job_id_input] = {
                    "status": "pending",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "progress": 0,
                    "generator": "Unknown"
                }
                st.success(f"✅ Added job: {job_id_input}")
                st.rerun()
            else:
                st.error("Please enter a job ID")

# --- Tab 2: Completed Jobs ---
with tab2:
    st.header("✅ Completed Jobs")
    
    completed_jobs = {
        job_id: job for job_id, job in st.session_state.jobs.items()
        if job.get("status") in ["completed", "success"]
    }
    
    if completed_jobs:
        # Sort by completion time
        sorted_jobs = sorted(
            completed_jobs.items(),
            key=lambda x: x[1].get("completed_at", ""),
            reverse=True
        )
        
        for job_id, job in sorted_jobs:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Job ID:** `{job_id}`")
                    st.markdown(f"**Generator:** {job.get('generator', 'Unknown')}")
                    st.markdown(f"**Completed:** {job.get('completed_at', 'N/A')}")
                    
                    # Show prompt if available
                    if job.get("prompt"):
                        with st.expander("View Prompt"):
                            st.text(job["prompt"])
                
                with col2:
                    if job.get("result_uri"):
                        st.markdown(f"**Result:** [View Video]({job['result_uri']})")
                    else:
                        st.markdown("**Result:** Pending")
                
                with col3:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Download", key=f"download_{job_id}", use_container_width=True):
                            st.info("Download feature coming soon")
                    with col_btn2:
                        if st.button("Delete", key=f"delete_{job_id}", use_container_width=True):
                            del st.session_state.jobs[job_id]
                            st.rerun()
    else:
        st.info("No completed jobs yet.")

# --- Tab 3: Job Statistics ---
with tab3:
    st.header("📊 Job Statistics")
    
    if st.session_state.jobs:
        # Calculate statistics
        total_jobs = len(st.session_state.jobs)
        active_count = len([j for j in st.session_state.jobs.values() if j.get("status") in ["pending", "processing"]])
        completed_count = len([j for j in st.session_state.jobs.values() if j.get("status") in ["completed", "success"]])
        failed_count = len([j for j in st.session_state.jobs.values() if j.get("status") == "failed"])
        cancelled_count = len([j for j in st.session_state.jobs.values() if j.get("status") == "cancelled"])
        
        # Display metrics
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        
        with col_m1:
            st.metric("Total Jobs", total_jobs)
        with col_m2:
            st.metric("Active", active_count)
        with col_m3:
            st.metric("Completed", completed_count)
        with col_m4:
            st.metric("Failed", failed_count)
        with col_m5:
            st.metric("Cancelled", cancelled_count)
        
        st.divider()
        
        # Generator breakdown
        st.markdown("### Generator Usage")
        
        generator_counts = {}
        for job in st.session_state.jobs.values():
            gen = job.get("generator", "Unknown")
            generator_counts[gen] = generator_counts.get(gen, 0) + 1
        
        if generator_counts:
            col_gen1, col_gen2 = st.columns(2)
            
            with col_gen1:
                st.markdown("**Jobs by Generator:**")
                for gen, count in sorted(generator_counts.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"- {gen}: {count}")
            
            with col_gen2:
                # Simple bar chart
                st.bar_chart(generator_counts)
        
        st.divider()
        
        # Status breakdown
        st.markdown("### Status Breakdown")
        
        status_counts = {}
        for job in st.session_state.jobs.values():
            status = job.get("status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            col_status1, col_status2 = st.columns(2)
            
            with col_status1:
                st.markdown("**Jobs by Status:**")
                for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"- {status.upper()}: {count}")
            
            with col_status2:
                st.pie_chart(status_counts)
        
        st.divider()
        
        # Export data
        st.markdown("### Export Data")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("Export as JSON", use_container_width=True):
                json_data = json.dumps(st.session_state.jobs, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="jobs.json",
                    mime="application/json"
                )
        
        with col_export2:
            if st.button("Export as CSV", use_container_width=True):
                import csv
                import io
                
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)
                
                # Header
                writer.writerow(["Job ID", "Generator", "Status", "Created", "Completed"])
                
                # Data
                for job_id, job in st.session_state.jobs.items():
                    writer.writerow([
                        job_id,
                        job.get("generator", "Unknown"),
                        job.get("status", "Unknown"),
                        job.get("created_at", "N/A"),
                        job.get("completed_at", "N/A")
                    ])
                
                st.download_button(
                    label="Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="jobs.csv",
                    mime="text/csv"
                )
    else:
        st.info("No jobs to display. Start generating videos to see statistics.")

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🔄 Auto-Refresh")
    
    auto_refresh = st.checkbox("Enable auto-refresh", value=False)
    
    if auto_refresh:
        refresh_interval = st.slider(
            "Refresh interval (seconds)",
            min_value=5,
            max_value=60,
            value=10,
            step=5
        )
        st.info(f"Page will refresh every {refresh_interval} seconds")
    
    st.divider()
    
    st.markdown("### 📈 Tips")
    st.markdown("""
    - **Monitor Progress:** Check job status in real-time
    - **Export Results:** Download job data for analysis
    - **Track History:** Keep records of all generations
    - **Batch Operations:** Manage multiple jobs at once
    """)
