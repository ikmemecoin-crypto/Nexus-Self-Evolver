import streamlit as st
from google import genai
from tavily import TavilyClient
import requests
import base64
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="NEXUS AI - Evolution Hub", page_icon="🧬", layout="wide")

# Load Secrets safely
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TAVILY_KEY = st.secrets["TAVILY_API_KEY"]
    GH_TOKEN = st.secrets["GITHUB_TOKEN"]
    GH_REPO = st.secrets["GITHUB_REPO"]
except Exception as e:
    st.error("⚠️ Missing Secrets! Please add GEMINI_API_KEY, TAVILY_API_KEY, GITHUB_TOKEN, and GITHUB_REPO to Streamlit Secrets.")
    st.stop()

# Initialize Clients
client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

# --- THE "HANDS" (GitHub API) ---
def update_nexus_code(new_code_content):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/app.py"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Get current file SHA for the update
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    
    encoded_content = base64.b64encode(new_code_content.encode('utf-8')).decode('utf-8')
    data = {"message": "🧬 NEXUS SELF-EVOLUTION: System Upgrade", "content": encoded_content, "sha": sha}
    
    update_res = requests.put(url, headers=headers, json=data)
    if update_res.status_code == 200:
        st.success("✅ EVOLUTION SUCCESSFUL. The Nexus is rebooting with new skills...")
        st.balloons()
    else:
        st.error(f"Evolution Failed: {update_res.text}")

# --- AI NEWS FEED LOGIC ---
def get_top_ai_news():
    # Use Tavily to fetch real news instead of mock data
    search = tavily.search(query="Top AI news today February 2026", search_depth="basic", max_results=5)
    return search.get('results', [])

# --- SIDEBAR ---
with st.sidebar:
    st.title("🧬 NEXUS AI Status")
    st.success("Brain: Connected")
    st.success("Hands: Master Key Active")
    st.divider()
    st.subheader("Real-Time AI Feed")
    
    if st.button("Refresh News"):
        st.session_state.news = get_top_ai_news()
    
    news = st.session_state.get('news', get_top_ai_news())
    for item in news:
        st.markdown(f"**[{item['title']}]({item['url']})**")
        st.caption(f"Relevance: {item.get('score', 'High')}")
        st.divider()

# --- MAIN UI ---
st.title("🌐 NEXUS AI Evolution Engine")
st.write("Synthesizing real-time research into evolutionary breakthroughs.")

# Evolution Input
task = st.text_area("What new skill or power should Nexus acquire?", 
                    placeholder="e.g., Add a data visualization dashboard for crypto prices.")

# THE BUTTON (Fixed placement)
if st.button("🚀 Initiate Research & Evolution"):
    with st.status("Analyzing and Evolving...", expanded=True) as status:
        st.write("Searching Global 2026 Databases...")
        search_results = tavily.search(query=f"Python Streamlit code for {task} 2026", search_depth="advanced")
        
        st.write("Synthesizing New DNA (Code)...")
        evolution_prompt = f"""
        You are the NEXUS AI Core. Task: {task}. 
        Research: {search_results}.
        Write a COMPLETE new app.py file. 
        Ensure you keep the GitHub update function and the News Sidebar.
        Return ONLY the raw Python code.
        """
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=evolution_prompt)
        st.session_state.draft_code = response.text
        status.update(label="DNA Drafted!", state="complete", expanded=False)

# Deployment Trigger
if "draft_code" in st.session_state:
    st.subheader("Proposed System Upgrade")
    st.code(st.session_state.draft_code, language="python")
    st.warning("⚠️ Permitting evolution will overwrite the current system.")
    if st.button("✅ PERMIT EVOLUTION"):
        update_nexus_code(st.session_state.draft_code)

# --- FOOTER ---
st.divider()
st.caption(f"NEXUS AI Core v4.0.26 | Last Sync: {datetime.datetime.now().strftime('%H:%M:%S')}")
