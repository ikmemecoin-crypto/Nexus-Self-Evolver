import streamlit as st
import json
import io
from groq import Groq
from github import Github
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import base64

# --- 1. CORE SYNC ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Nexus Sync Offline: {e}")
        return None, None

client, repo = init_nexus()

# --- 2. THEME & USER-FRIENDLY UI ---
st.set_page_config(page_title="Nexus Pro v2.5", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #0E1117 !important; color: #E0E0E0 !important; }
    
    /* Clean Sidebar */
    [data-testid="stSidebar"] { background-color: #1A1C23 !important; border-right: 1px solid #30363d; }
    
    /* Human Chat Bubble Style */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; padding: 10px; }
    
    .main-title {
        font-size: 32px; font-weight: 600; background: linear-gradient(120deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (REPOSITORY VAULT) ---
with st.sidebar:
    st.markdown('<div class="main-title">Nexus Vault</div>', unsafe_allow_html=True)
    st.success("Target: $2,000 / Current: $0")
    st.markdown("---")
    st.subheader("📁 Repository Files")
    try:
        for f in repo.get_contents(""):
            if f.type == "file":
                with st.expander(f"📄 {f.name}"):
                    st.code(f.decoded_content.decode()[:150] + "...")
                    if st.button("Delete", key=f"del_{f.name}"):
                        repo.delete_file(f.path, "Remove", f.sha); st.rerun()
    except: st.info("Scanning Vault...")

# --- 4. MAIN INTERFACE (CONSOLIDATED TABS) ---
tab_conv, tab_architect, tab_media, tab_test = st.tabs([
    "🤝 Conversation Hub", "✍️ Code Architect", "🎨 Media Studio", "🧪 Live Sandbox"
])

# --- TAB 1: HUMAN CONVERSATION (VOICE + CHAT) ---
with tab_conv:
    col_chat, col_voice = st.columns([7, 3])
    
    with col_chat:
        if "messages" not in st.session_state: st.session_state.messages = []
        chat_box = st.container(height=500, border=True)
        for m in st.session_state.messages:
            with chat_box.chat_message(m["role"]): st.markdown(m["content"])
    
    with col_voice:
        st.subheader("🎙️ Human Voice")
        st.write("Speak naturally. I use Roman Urdu & English.")
        audio = mic_recorder(start_prompt="🎤 Start Talking", stop_prompt="🛑 Stop Talking", key='nexus_voice')
    
    # Input Processing
    query = st.chat_input("Message Nexus...")
    user_input = query if query else None

    # Voice to Text Conversion
    if audio and client:
        with st.spinner("Listening..."):
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = "audio.wav"
            user_input = client.audio.transcriptions.create(model="whisper-large-v3", file=audio_bio).text

    if user_input and client:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_box.chat_message("user"): st.markdown(user_input)
        
        with chat_box.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # SYSTEM PROMPT: Forces Roman Urdu and Human-like persona
                system_instr = "You are Nexus, a helpful human-like AI. Respond ONLY in a mix of English and Roman Urdu (Urdu written in English script). Never use Urdu/Arabic script. Be friendly and conversational."
                
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_instr}] + st.session_state.messages
                ).choices[0].message.content
                
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                
                # Human Voice Output (TTS)
                tts = gTTS(text=res, lang='en') # 'en' handles Roman Urdu better than 'ur' (script-based)
                b_io = io.BytesIO(); tts.write_to_fp(b_io)
                st.audio(b_io.getvalue(), format="audio/mp3", autoplay=True)
                st.rerun()

# --- TAB 2: ARCHITECT ---
with tab_architect:
    st.subheader("🚀 Production Deployment")
    fn = st.text_input("Filename", "earning_logic.py")
    cb = st.text_area("Source Code", height=300)
    if st.button("Push to Production", use_container_width=True):
        try:
            try: f = repo.get_contents(fn); repo.update_file(fn, "Sync", cb, f.sha)
            except: repo.create_file(fn, "Init", cb)
            st.toast("Success!"); st.rerun()
        except Exception as e: st.error(e)

# --- TAB 3: MEDIA STUDIO ---
with tab_media:
    m_p = st.text_input("Media Prompt", placeholder="A professional office for Adil...")
    if st.button("Generate Image"):
        url = f"https://image.pollinations.ai/prompt/{m_p.replace(' ', '%20')}"
        st.image(url, use_container_width=True)

# --- TAB 4: SANDBOX ---
with tab_test:
    tc = st.text_area("Test Code", value='st.balloons()')
    if st.button("Run Test"): exec(tc)
