import streamlit as st
import google.generativeai as genai
from github import Github, GithubException
import os

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Nexus Omni: Gemini Core",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Secrets securely
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    # Optional: GitHub Key for the "Push to Production" feature
    GITHUB_KEY = st.secrets.get("GITHUB_TOKEN", None) 
    REPO_NAME = st.secrets.get("REPO_NAME", "your-username/nexus-repo")
except FileNotFoundError:
    st.error("🚨 CRITICAL: `.streamlit/secrets.toml` not found. Please add your API keys!")
    st.stop()
except KeyError as e:
    st.error(f"🚨 MISSING SECRET: {e}. Check your Streamlit dashboard.")
    st.stop()

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
# We use 'gemini-1.5-flash' for speed and high free-tier limits
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. CORE FUNCTIONS ---

def get_gemini_response(prompt, history=[]):
    """
    Sends a message to Gemini while maintaining context history.
    """
    try:
        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Nexus Error: {str(e)}"

def push_to_github(filename, code, commit_msg):
    """
    Pushes generated code to your GitHub repo automatically.
    """
    if not GITHUB_KEY:
        return "❌ Error: GITHUB_TOKEN not found in secrets."
    
    try:
        g = Github(GITHUB_KEY)
        repo = g.get_repo(REPO_NAME)
        
        try:
            # Update existing file
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, commit_msg, code, contents.sha)
            return f"✅ Updated `{filename}` successfully!"
        except:
            # Create new file if it doesn't exist
            repo.create_file(filename, commit_msg, code)
            return f"✅ Created `{filename}` successfully!"
            
    except GithubException as e:
        return f"❌ GitHub Error: {e.data.get('message', str(e))}"

# --- 3. UI ARCHITECTURE ---

# Sidebar: System Status
with st.sidebar:
    st.header("🔮 Nexus System")
    st.success("Core: Gemini 1.5 Flash")
    st.info("Mode: Omni-Agent")
    
    st.divider()
    st.markdown("### 📂 Repository Vault")
    # Simulation of repo files (In real version, use repo.get_contents)
    st.code("app.py\nrequirements.txt\ntask_master.py", language="text")

# Main Interface
st.title("🧬 Nexus Omni")
st.markdown("*Self-Evolving AI Architecture powered by Google Gemini*")

# Create Tabs to organize the features neatly
tab1, tab2 = st.tabs(["💬 Nexus Chat", "🛠️ Code Architect"])

# --- TAB 1: INTELLIGENT CHAT ---
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Command the Nexus..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Convert Streamlit history to Gemini history format
                gemini_history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                
                response = get_gemini_response(prompt, gemini_history)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- TAB 2: CODE ARCHITECT (The Feature from your Screenshot) ---
with tab2:
    st.subheader("🚀 Autonomous Code Generator")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        target_file = st.text_input("Target Filename", value="new_tool.py")
        task_desc = st.text_area("Describe functionality", height=150, 
                               placeholder="e.g., Create a python script that scans the local folder for duplicate images.")
        
        generate_btn = st.button("✨ Generate Code")

    with col2:
        st.markdown("### Source Code Preview")
        if generate_btn and task_desc:
            with st.spinner("Architecting solution..."):
                # Specialized prompt for coding
                code_prompt = f"Write a production-ready Python script for: {task_desc}. Provide ONLY the code, no markdown formatting."
                generated_code = get_gemini_response(code_prompt)
                
                # Clean up if Gemini adds markdown blocks
                clean_code = generated_code.replace("```python", "").replace("```", "").strip()
                
                st.session_state['generated_code'] = clean_code
                st.code(clean_code, language="python")
        
        elif "generated_code" in st.session_state:
            st.code(st.session_state['generated_code'], language="python")
        
        # Push to Production Button
        if "generated_code" in st.session_state:
            if st.button("🚀 Push to Repository"):
                status = push_to_github(target_file, st.session_state['generated_code'], "Nexus Auto-Update")
                st.toast(status)
