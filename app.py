import streamlit as st
import json
import os
import requests
import base64

# Configuration (Ensure these are set in .streamlit/secrets.toml)
# GITHUB_TOKEN = "your_github_personal_access_token"
# GITHUB_REPO = "username/repository_name"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
GITHUB_REPO = st.secrets.get("GITHUB_REPO")
FILE_PATH = "memory.json"

def save_to_github(data):
    """Saves dictionary to memory.json on GitHub using the REST API."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Get the current file SHA to perform an update
    res = requests.get(url, headers=headers)
    sha = None
    if res.status_code == 200:
        sha = res.json().get("sha")

    # 2. Encode content to Base64
    content_str = json.dumps(data, indent=4)
    encoded_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")

    # 3. Prepare the PUT request
    payload = {
        "message": "Update identity from Streamlit UI",
        "content": encoded_content
    }
    if sha:
        payload["sha"] = sha

    # 4. Push to GitHub
    put_res = requests.put(url, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

def load_local_memory():
    """Loads memory from local file if it exists."""
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- App Logic ---

st.set_page_config(page_title="Identity Sync Manager", layout="wide")

# Sidebar UI
st.sidebar.title("Settings")
current_memory = load_local_memory()
default_name = current_memory.get("name", "")

user_name_input = st.sidebar.text_input("My Name", value=default_name)

if st.sidebar.button("💾 Sync Identity"):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        st.sidebar.error("Error: GitHub credentials not found in secrets.")
    elif user_name_input:
        new_data = {"name": user_name_input}
        
        with st.sidebar.status("Syncing to GitHub...") as status:
            success = save_to_github(new_data)
            if success:
                # Update local file as well for immediate persistence
                with open(FILE_PATH, "w") as f:
                    json.dump(new_data, f)
                status.update(label="Sync Complete!", state="complete")
                st.sidebar.success(f"Identity saved: {user_name_input}")
                st.rerun()
            else:
                status.update(label="Sync Failed", state="error")
                st.sidebar.error("Could not sync to GitHub. Check your token/repo settings.")
    else:
        st.sidebar.warning("Please enter a name.")

# Main Page Display
st.title("Streamlit Workspace")

if current_memory.get("name"):
    st.header(f"Hello, {current_memory['name']}!")
    st.info("Your identity is synced across the repository via memory.json.")
else:
    st.header("Welcome!")
    st.write("Please set your name in the sidebar to sync your identity.")

# Example of existing logic/content
st.divider()
st.subheader("Current Session Data")
st.json(current_memory)

# Additional app features can go here
st.write("App is ready for further logic...")