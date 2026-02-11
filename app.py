import streamlit as st
from google import genai
from tavily import TavilyClient
import requests
import base64
import json
from github import Github

# --- 1. CONFIG & SECRETS ---
st.set_page_config(page_title="NEXUS - God Tier", layout="wide")

try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    GH_TOKEN = st.secrets["GITHUB_TOKEN"]
    GH_REPO = st.secrets["GITHUB_REPO"]
except:
    st.error("Secrets missing! Check Streamlit Settings.")
    st.stop()

# Initialize
client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
g = Github(GH_TOKEN)

# --- 2. MEMORY LOGIC ---
def get_memory():
    try:
        repo = g.get_repo(GH_REPO)
        file = repo.get_contents("memory.json")
        return json.loads(file.decoded_content.decode())
    except:
        return {"user_name": "Explorer"}

def update_github_file(file_path, content, message):
    repo = g.get_repo(GH_REPO)
    try:
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, message, content, contents.sha)
    except:
        repo.create_file(file_path, message, content)

# --- 3. SIDEBAR (Identity) ---
mem = get_memory()
with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.write(f"Logged in as: **{mem.get('user_name')}**")
    new_name = st.text_input("Change Name:", value=mem.get('user_name'))
    if st.button("💾 Sync Identity"):
        update_github_file("memory.json", json.dumps({"user_name": new_name}), "Update Identity")
        st.success("Identity Updated! Refreshing...")
        st.rerun()

# --- 4. MAIN PAGE (The Command Center) ---
st.title(f"Welcome back, {mem.get('user_name')}!")
st.write("The Evolution Engine is online. Give your next command below.")

# THIS IS THE BOX THAT WAS MISSING
task = st.text_area("🚀 What should Nexus build or become next?", 
                    placeholder="e.g., Add a live crypto price tracker to the sidebar.")

if st.button("Initiate Evolution"):
    with st.status("NEXUS is researching and rewriting its DNA...", expanded=True):
        # Research
        search = tavily.search(query=f"Streamlit python code for {task}", search_depth="advanced")
        
        # Rewrite Code
        prompt = f"""
        You are NEXUS AI. Rewrite the ENTIRE 'app.py' to include the existing GitHub update logic, 
        the memory.json logic, and add this new feature: {task}. 
        Research: {search}. 
        Return ONLY the raw Python code.
        """
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        st.session_state.draft = response.text

if "draft" in st.session_state:
    st.subheader("🧬 New DNA Drafted")
    st.code(st.session_state.draft, language="python")
    if st.button("✅ PERMIT EVOLUTION"):
        update_github_file("app.py", st.session_state.draft, "🧬 NEXUS SELF-EVOLUTION")
        st.balloons()
        st.success("System updated. Please wait 60s for reboot.")
