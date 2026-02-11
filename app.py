import streamlit as st
from google import genai
from tavily import TavilyClient
import json
import datetime
from github import Github

# --- 1. SETTINGS & STYLING (The "Attractive" Fix) ---
st.set_page_config(page_title="NEXUS COMMAND", layout="wide", initial_sidebar_state="expanded")

# CORRECTED PARAMETER: unsafe_allow_html=True
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white; border: none; border-radius: 12px;
        padding: 10px; font-weight: bold; width: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stTextArea textarea { background-color: rgba(255, 255, 255, 0.05); color: #00d2ff; border: 1px solid #3a7bd5; border-radius: 10px; }
    [data-testid="stSidebar"] { background-color: #0b0e14; border-right: 1px solid #3a7bd5; }
    h1, h2, h3 { color: #00d2ff; font-family: 'Courier New', Courier, monospace; }
    .css-1kyxreq { background-color: rgba(0,0,0,0); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTH & KEYS ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    GH_TOKEN = st.secrets["GITHUB_TOKEN"]
    GH_REPO = st.secrets["GITHUB_REPO"]
except Exception as e:
    st.error(f"📡 CONNECTION OFFLINE: {e}")
    st.stop()

client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
g = Github(GH_TOKEN)

# --- 3. PERSISTENT MEMORY ---
def get_memory():
    try:
        repo = g.get_repo(GH_REPO)
        file = repo.get_contents("memory.json")
        return json.loads(file.decoded_content.decode())
    except:
        return {"user_name": "Azhan & Zohan"}

def update_file(path, content, msg):
    repo = g.get_repo(GH_REPO)
    try:
        sha = repo.get_contents(path).sha
        repo.update_file(path, msg, content, sha)
    except:
        repo.create_file(path, msg, content)

# --- 4. THE INTERFACE ---
mem = get_memory()
user = mem.get('user_name', 'Commander')

with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.success("BRAIN: CONNECTED")
    st.info(f"USER: {user}")
    st.markdown("---")
    
    with st.expander("👤 IDENTITY SETTINGS"):
        new_name = st.text_input("Change Alias", value=user)
        if st.button("SYNC DNA"):
            mem['user_name'] = new_name
            update_file("memory.json", json.dumps(mem), "Update Identity")
            st.rerun()

# Main Dashboard
st.title(f"Welcome to the Nexus, {user}")
st.write("### ⚡ Command & Evolution Center")

# Create a clean layout
col1, col2 = st.columns([2, 1])

with col1:
    task = st.text_area("What is your next command for the system?", 
                        placeholder="Example: Add a live world clock and a weather widget...",
                        height=180)
    
    if st.button("🚀 INITIATE SYSTEM EVOLUTION"):
        if task:
            with st.status("🧬 Synthesis in progress...", expanded=True):
                st.write("Researching 2026 patterns...")
                res = tavily.search(query=f"Python Streamlit UI code for {task}", search_depth="advanced")
                
                st.write("Rewriting System Code...")
                prompt = f"Rewrite the whole app.py. Keep GitHub and Memory logic. Add: {task}. Use {res}. Output RAW Python code only."
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                st.session_state.draft = response.text
        else:
            st.warning("Please enter a command.")

with col2:
    st.write("### 📊 System Intel")
    st.metric("Version", "4.0.26")
    st.metric("Latency", "Optimal")
    if "draft" in st.session_state:
        st.success("✨ New DNA Sequence Prepared")

# Deployment Logic
if "draft" in st.session_state:
    st.divider()
    st.subheader("🧬 Proposed Evolution DNA")
    st.code(st.session_state.draft, language="python")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ PERMIT OVERWRITE"):
            update_file("app.py", st.session_state.draft, "🧬 NEXUS EVOLUTION")
            st.balloons()
            st.toast("Evolving... Check back in 60 seconds!")
    with c2:
        if st.button("❌ DISCARD"):
            del st.session_state.draft
            st.rerun()
