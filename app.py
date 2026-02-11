import streamlit as st
from google import genai
from tavily import TavilyClient
import requests
import base64
import datetime
from github import Github  # Correct import for the Master Key

# --- CONFIGURATION ---
st.set_page_config(page_title="NEXUS AI - God Tier", page_icon="🧬", layout="wide")

# Load Secrets safely
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    GH_TOKEN = st.secrets["GITHUB_TOKEN"]
    GH_REPO = st.secrets["GITHUB_REPO"]
except Exception as e:
    st.error("⚠️ Missing Secrets! Please check your Streamlit Cloud settings.")
    st.stop()

# Initialize Clients
client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
g = Github(GH_TOKEN)

# --- SYSTEM LOGIC ---
def update_nexus_code(new_code_content):
    repo = g.get_repo(GH_REPO)
    contents = repo.get_contents("app.py")
    repo.update_file(contents.path, "🧬 NEXUS SELF-EVOLUTION", new_code_content, contents.sha)
    st.success("Evolution Complete! Rebooting...")
    st.balloons()

# --- SIDEBAR & STATUS ---
with st.sidebar:
    st.title("🧬 NEXUS System")
    st.success(f"Repository: {GH_REPO}")
    st.info("Memory Mode: Active")
    st.divider()
    if st.button("🧹 Clear Draft"):
        if "draft_code" in st.session_state:
            del st.session_state.draft_code
            st.rerun()

# --- MAIN INTERFACE ---
st.title("🌐 NEXUS AI: Evolution & Memory")
st.write("Current Status: Operational. Ready for God-tier upgrades.")

# Memory Section
with st.expander("📝 System Memory & Logs"):
    st.write("Memory file `memory.json` is synced with GitHub.")
    # Here the AI can later add logic to read/write memories

st.divider()

# EVOLUTION ENGINE
st.subheader("🚀 Evolution Command")
task = st.text_area("What complex skill or upgrade should Nexus acquire tonight?", 
                    placeholder="e.g., Add a sidebar memory log that remembers my name.")

if st.button("Initiate Research & Coding"):
    with st.status("NEXUS is thinking...", expanded=True) as status:
        st.write("Searching 2026 Web Databases...")
        search_results = tavily.search(query=f"Python Streamlit code for {task}", search_depth="advanced")
        
        st.write("Synthesizing Code DNA...")
        prompt = f"Write a complete app.py including current logic and this new feature: {task}. Research: {search_results}. Output raw code only."
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        
        st.session_state.draft_code = response.text
        status.update(label="Evolution Drafted!", state="complete")

# SHOW DRAFT AND PERMIT
if "draft_code" in st.session_state:
    st.subheader("Proposed Upgrade")
    st.code(st.session_state.draft_code, language="python")
    if st.button("✅ PERMIT EVOLUTION"):
        update_nexus_code(st.session_state.draft_code)

st.divider()
st.caption(f"NEXUS Core | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
