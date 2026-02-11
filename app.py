import streamlit as st
from google import genai
from tavily import TavilyClient
import requests
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="NEXUS: Evolution Phase", layout="wide", page_icon="🧬")
st.title("🌐 NEXUS CORE: Evolution Mode")

# Load Secrets
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    GH_TOKEN = st.secrets["GITHUB_TOKEN"]
    GH_REPO = st.secrets["GITHUB_REPO"] # Should be "YourUsername/Nexus-Self-Evolver"
except Exception as e:
    st.error("Missing Secrets! Check your Streamlit Cloud settings.")
    st.stop()

client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

# --- THE "HANDS" (GitHub API) ---
def update_nexus_code(new_code_content):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/app.py"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Get the current file "SHA" (required by GitHub to update)
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    
    # Encode code to Base64
    encoded_content = base64.b64encode(new_code_content.encode('utf-8')).decode('utf-8')
    
    data = {
        "message": "🧬 NEXUS SELF-EVOLUTION: System Upgrade",
        "content": encoded_content,
        "sha": sha
    }
    
    update_res = requests.put(url, headers=headers, json=data)
    if update_res.status_code == 200:
        st.success("✅ EVOLUTION SUCCESSFUL. The Nexus is rebooting with new skills...")
        st.balloons()
    else:
        st.error(f"Evolution Failed: {update_res.text}")

# --- UI INTERFACE ---
st.sidebar.header("System Status")
st.sidebar.success("Brain: Connected")
st.sidebar.success("Hands: Master Key Active")

task = st.text_area("What new skill or power should Nexus acquire?", 
                    placeholder="e.g., Add a beautiful dark-mode 3D dashboard with a live crypto price tracker.")

if st.button("🚀 Initiate Research & Coding"):
    with st.spinner("NEXUS is researching the latest 2026 code libraries..."):
        # 1. Search for the best way to do the task
        search_results = tavily.search(query=f"Python Streamlit code for {task} 2026 best practices", search_depth="advanced")
        
    with st.spinner("Drafting new DNA (Code)..."):
        # 2. Tell Gemini to write the new version of the app
        evolution_prompt = f"""
        You are the NEXUS AI. Your current task is: {task}.
        Using this research: {search_results}.
        Write a COMPLETE, single-file 'app.py' using Streamlit. 
        It MUST include all previous logic (the search and evolution functions) but add the new requested feature flawlessly.
        Output ONLY the raw Python code. No explanations.
        """
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=evolution_prompt)
        st.session_state.draft_code = response.text

if "draft_code" in st.session_state:
    st.subheader("Proposed System Upgrade")
    st.code(st.session_state.draft_code, language="python")
    
    st.warning("⚠️ Clicking 'PERMIT' will overwrite the current system code.")
    if st.button("✅ PERMIT EVOLUTION"):
        update_nexus_code(st.session_state.draft_code)
