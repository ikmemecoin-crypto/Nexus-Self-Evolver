import streamlit as st
import json
import os
from github import Github
from github import GithubException
import requests

# --- CONFIGURATION ---
# Ensure these secrets are set in your Streamlit Cloud or local .env
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))
GITHUB_REPO_NAME = st.secrets.get("GITHUB_REPO", os.getenv("GITHUB_REPO")) # e.g., "username/repository"
MEMORY_FILE_PATH = "memory.json"

st.set_page_config(page_title="NEXUS AI Core", layout="wide")

# --- GITHUB UTILITIES ---
def get_github_repo():
    if not GITHUB_TOKEN or not GITHUB_REPO_NAME:
        st.error("GitHub configuration missing. Please set GITHUB_TOKEN and GITHUB_REPO.")
        return None
    g = Github(GITHUB_TOKEN)
    return g.get_repo(GITHUB_REPO_NAME)

def update_github_file(file_path, commit_message, content):
    repo = get_github_repo()
    if not repo: return
    
    try:
        # Check if file exists to get SHA
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, commit_message, content, contents.sha)
        st.success(f"Successfully updated {file_path} on GitHub.")
    except GithubException as e:
        if e.status == 404:
            # File doesn't exist, create it
            repo.create_file(file_path, commit_message, content)
            st.success(f"Successfully created {file_path} on GitHub.")
        else:
            st.error(f"GitHub Error: {e}")

def load_memory():
    repo = get_github_repo()
    if not repo: return None
    try:
        contents = repo.get_contents(MEMORY_FILE_PATH)
        return json.loads(contents.decoded_content.decode())
    except:
        return {
            "name": "Unknown Entity",
            "goals": "Initialize Nexus Core",
            "evolutions": ["Core Initialization"]
        }

# --- SIDEBAR: NEWS ---
with st.sidebar:
    st.title("🌐 News Sidebar")
    try:
        # Example News API or RSS feed (using a placeholder if no key provided)
        st.info("Fetching latest tech updates...")
        st.markdown("---")
        st.write("1. **AI Evolution:** Large Language Models reaching new heights in reasoning.")
        st.write("2. **Open Source:** GitHub API integration patterns simplified.")
        st.write("3. **Streamlit:** New layout options for sidebar management released.")
    except Exception as e:
        st.error("Could not load news.")

# --- SIDEBAR: MEMORY ---
with st.sidebar:
    st.title("🧠 Memory Sidebar")
    memory_data = load_memory()
    
    if memory_data:
        st.subheader(f"👤 User: {memory_data.get('name')}")
        st.write(f"🎯 **Current Goals:**\n{memory_data.get('goals')}")
        
        st.write("📜 **Last 5 Evolutions:**")
        evols = memory_data.get('evolutions', [])[-5:] # Get last 5
        for i, evol in enumerate(reversed(evols)):
            st.caption(f"{len(evols)-i}. {evol}")

# --- MAIN UI ---
st.title("NEXUS AI Core")
st.markdown("### Interface for Repository Evolution & Memory Management")

with st.expander("Update Memory & Synchronize to GitHub"):
    with st.form("memory_form"):
        new_name = st.text_input("Entity Name", value=memory_data.get("name") if memory_data else "")
        new_goals = st.text_area("Project Goals", value=memory_data.get("goals") if memory_data else "")
        new_evolution = st.text_input("Log New Evolution")
        
        submit = st.form_submit_button("Sync to GitHub")
        
        if submit:
            # Prepare updated JSON
            updated_evols = memory_data.get('evolutions', [])
            if new_evolution:
                updated_evols.append(new_evolution)
            
            # Keep only the last 50 for storage efficiency, though we display 5
            updated_data = {
                "name": new_name,
                "goals": new_goals,
                "evolutions": updated_evols[-50:] 
            }
            
            # Convert to string and push
            json_content = json.dumps(updated_data, indent=4)
            update_github_file(MEMORY_FILE_PATH, "NEXUS Core: Update Memory.json", json_content)
            st.rerun()

# --- REPOSITORY CONTROL ---
st.divider()
st.subheader("System Status")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Repository:** `{GITHUB_REPO_NAME}`")
    st.write(f"**Memory File:** `{MEMORY_FILE_PATH}`")
with col2:
    if st.button("Manual Refresh"):
        st.rerun()

st.info("NEXUS AI Core is operational. All changes are version-controlled via GitHub API.")