import streamlit as st
from google import genai
from tavily import TavilyClient
import json
import datetime
from github import Github

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="NEXUS | AI COMMAND", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for the "Unique & Attractive" Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button {
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        color: white; border: none; border-radius: 20px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 15px #4facfe; }
    .stTextArea textarea { background-color: #1a1c24; color: #00f2fe; border: 1px solid #4facfe; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    h1 { color: #4facfe; text-shadow: 0px 0px 10px #4facfe; }
    </style>
    """, unsafe_call_unsafe_javascript=True)

# --- 2. AUTH & KEYS ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    GH_TOKEN = st.secrets["GITHUB_TOKEN"]
    GH_REPO = st.secrets["GITHUB_REPO"]
except:
    st.error("📡 CONNECTION ERROR: Secrets missing in Streamlit Cloud.")
    st.stop()

client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
g = Github(GH_TOKEN)

# --- 3. SYSTEM FUNCTIONS ---
def get_memory():
    try:
        repo = g.get_repo(GH_REPO)
        file = repo.get_contents("memory.json")
        return json.loads(file.decoded_content.decode())
    except:
        return {"user_name": "Commander", "history": []}

def update_file(path, content, msg):
    repo = g.get_repo(GH_REPO)
    try:
        sha = repo.get_contents(path).sha
        repo.update_file(path, msg, content, sha)
    except:
        repo.create_file(path, msg, content)

# --- 4. SIDEBAR IDENTITY ---
mem = get_memory()
with st.sidebar:
    st.title("🧬 NEXUS CORE")
    st.markdown("---")
    st.write(f"📡 **STATUS:** Operational")
    st.write(f"👤 **USER:** {mem.get('user_name')}")
    
    with st.expander("⚙️ Identity Settings"):
        new_name = st.text_input("Change Alias", value=mem.get('user_name'))
        if st.button("Update DNA"):
            mem['user_name'] = new_name
            update_file("memory.json", json.dumps(mem), "Update Identity")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"Nexus OS v4.0.26 | {datetime.date.today()}")

# --- 5. MAIN INTERFACE ---
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.title(f"Greetings, {mem.get('user_name')}")
    st.write("### 🚀 Evolution Command Center")
    
    task = st.text_area("Input the next phase of your AI's evolution:", 
                        placeholder="e.g. Add a 3D glass-card style dashboard for weather and news...",
                        height=150)
    
    if st.button("⚡ INITIATE SYSTEM EVOLUTION"):
        if task:
            with st.status("📡 NEXUS is researching & rewriting...", expanded=True):
                st.write("Scanning global 2026 tech trends...")
                search = tavily.search(query=f"Modern Streamlit python UI code for {task}", search_depth="advanced")
                
                st.write("Synthesizing New Code Architecture...")
                prompt = f"""
                You are NEXUS AI. Rewrite the entire 'app.py' to include all current GitHub/Memory logic 
                plus this new feature: {task}. 
                Current context: {search}.
                Ensure the UI remains attractive with the custom CSS provided.
                Return ONLY raw code.
                """
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                st.session_state.draft = response.text
        else:
            st.warning("Please enter a command first.")

with col_stats:
    st.write("### 📊 System Intel")
    st.info(f"**Current Focus:** {task if task else 'Awaiting Input'}")
    if "draft" in st.session_state:
        st.success("✨ New DNA Sequence Ready")

# --- 6. DEPLOYMENT ZONE ---
if "draft" in st.session_state:
    st.divider()
    st.subheader("🧬 Proposed Evolution DNA")
    st.code(st.session_state.draft, language="python")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ PERMIT OVERWRITE"):
            update_file("app.py", st.session_state.draft, "🧬 NEXUS EVOLUTION")
            st.balloons()
            st.toast("System updating... Refresh in 60 seconds.")
    with col2:
        if st.button("❌ ABORT"):
            del st.session_state.draft
            st.rerun()
