import streamlit as st
import json
from groq import Groq
from github import Github
import google.generativeai as genai
from openai import OpenAI

# --- 1. CORE SYNC & CLIENTS ---
@st.cache_resource
def init_nexus():
    try:
        # Groq Client
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        # Gemini Client
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        gem_model = genai.GenerativeModel('gemini-1.5-flash')
        # OpenAI Client
        oa_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # GitHub
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        
        return {"groq": g_client, "gemini": gem_model, "openai": oa_client}, r
    except Exception as e:
        st.error(f"Sync Offline: {e}")
        return None, None

clients, repo = init_nexus()

# Initialize the Model Cycle State
if "model_cycle" not in st.session_state:
    st.session_state.model_cycle = ["groq", "gemini", "openai"]
if "current_model_idx" not in st.session_state:
    st.session_state.current_model_idx = 0

# --- 2. THEME & UI (Same as Standard) ---
st.set_page_config(page_title="Nexus Pro", layout="wide", initial_sidebar_state="collapsed")
if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text, accent = ("#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF")

st.markdown(f"""<style>
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{ background: {card}; border-radius: 16px; padding: 24px; border: 1px solid rgba(128,128,128,0.2); }}
    .main-title {{ font-size: 36px; font-weight: 600; background: linear-gradient(120deg, #58a6ff, #bc8cff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    [data-testid="stSidebar"], #MainMenu, footer, header {{ visibility: hidden; }}
</style>""", unsafe_allow_html=True)

# --- 3. LOGIC ENGINE ---
def get_ai_response(prompt):
    # Try models in a circular fashion starting from current index
    attempts = 0
    while attempts < 3:
        current_provider = st.session_state.model_cycle[st.session_state.current_model_idx]
        try:
            if current_provider == "groq":
                resp = clients["groq"].chat.completions.create(
                    model="llama-3.3-70b-versatile", 
                    messages=[{"role": "user", "content": prompt}]
                )
                return resp.choices[0].message.content, "Groq (Llama 3.3)"
            
            elif current_provider == "gemini":
                resp = clients["gemini"].generate_content(prompt)
                return resp.text, "Google (Gemini 1.5)"
            
            elif current_provider == "openai":
                resp = clients["openai"].chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                return resp.choices[0].message.content, "OpenAI (GPT-4o)"
                
        except Exception as e:
            # If error is rate limit or API issue, move to next model
            st.warning(f"{current_provider} limit reached. Cycling to next AI...")
            st.session_state.current_model_idx = (st.session_state.current_model_idx + 1) % 3
            attempts += 1
    
    return "All AI nodes are currently at capacity. Please wait for limits to reset.", "System"

# --- 4. HEADER & LAYOUT ---
c_head1, c_head2 = st.columns([8, 2])
with c_head1:
    current_name = st.session_state.model_cycle[st.session_state.current_model_idx].upper()
    st.markdown(f'<div class="main-title">Nexus Omni <span style="font-size:14px; color:gray;">Active: {current_name}</span></div>', unsafe_allow_html=True)
with c_head2:
    st.session_state.theme_mode = st.selectbox("Appearance", ["Dark", "Light"], label_visibility="collapsed")

col_writer, col_chat = st.columns([4, 6], gap="large")

with col_writer:
    st.subheader("✍️ Code Architect")
    fname = st.text_input("Filename", value="nexus_logic.py")
    code_body = st.text_area("Source Code", height=300)
    if st.button("🚀 Push to Production", use_container_width=True):
        try:
            try:
                f = repo.get_contents(fname)
                repo.update_file(fname, "Update", code_body, f.sha)
            except:
                repo.create_file(fname, "Deploy", code_body)
            st.toast("Success!")
        except Exception as e: st.error(e)

with col_chat:
    st.subheader("💬 Nexus Intelligent Chat")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    chat_box = st.container(height=500, border=True)
    for m in st.session_state.messages:
        with chat_box.chat_message(m["role"]): st.markdown(m["content"])

    query = st.chat_input("Command the Nexus...")
    if query and clients:
        st.session_state.messages.append({"role": "user", "content": query})
        with chat_box.chat_message("user"): st.markdown(query)
        
        with chat_box.chat_message("assistant"):
            with st.spinner("Cycling AI Nodes..."):
                answer, provider_label = get_ai_response(query)
                st.markdown(f"**[{provider_label}]**\n\n{answer}")
                st.session_state.messages.append({"role": "assistant", "content": answer})
