import streamlit as st
import json
import base64
from io import BytesIO
from groq import Groq
from github import Github
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

# --- 1. CORE SYNC ---
@st.cache_resource
def init_nexus():
    try:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        gh = Github(st.secrets["GH_TOKEN"])
        r = gh.get_repo(st.secrets["GH_REPO"])
        return g_client, r
    except Exception as e:
        st.error(f"Sync Offline: {e}")
        return None, None

client, repo = init_nexus()

# --- 2. THEME & PROFESSIONAL STYLING ---
st.set_page_config(page_title="Nexus Pro v2.6", layout="wide", initial_sidebar_state="collapsed")

if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"
bg, card, text, accent = ("#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff") if st.session_state.theme_mode == "Dark" else ("#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: {card}; border-radius: 16px; padding: 24px;
        border: 1px solid rgba(128, 128, 128, 0.2); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }}
    .main-title {{
        font-size: 36px; font-weight: 600; background: linear-gradient(120deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PROFESSIONAL HEADER ---
c_head1, c_head2 = st.columns([8, 2])
with c_head1: st.markdown('<div class="main-title">Nexus Omni <span style="font-size:14px; color:gray;">v2.6 Pro</span></div>', unsafe_allow_html=True)
with c_head2: st.session_state.theme_mode = st.selectbox("Appearance", ["Dark", "Light"], label_visibility="collapsed")

# --- 4. THE 5-TAB ARCHITECTURE ---
tab_code, tab_chat, tab_voice, tab_media, tab_test = st.tabs([
    "✍️ Architect & Vault", "💬 Intelligent Chat", "🎙️ Human Voice (En/Ur)", "🎨 Media Studio", "🧪 Live Sandbox"
])

# --- TAB 1: CODE ARCHITECT ---
with tab_code:
    st.subheader("Deploy to Production")
    fname = st.text_input("Filename", value="new_logic.py")
    code_body = st.text_area("Source Code", height=250)
    if st.button("🚀 Push to GitHub", use_container_width=True):
        try:
            try:
                f = repo.get_contents(fname); repo.update_file(fname, "Update", code_body, f.sha)
            except: repo.create_file(fname, "Deploy", code_body)
            st.success("Deployed!")
        except Exception as e: st.error(e)

# --- TAB 2: INTELLIGENT CHAT ---
with tab_chat:
    if "messages" not in st.session_state: st.session_state.messages = []
    chat_box = st.container(height=400, border=True)
    for m in st.session_state.messages:
        with chat_box.chat_message(m["role"]): st.markdown(m["content"])
    
    query = st.chat_input("Command the Nexus...")
    if query and client:
        st.session_state.messages.append({"role": "user", "content": query})
        with chat_box.chat_message("user"): st.markdown(query)
        with chat_box.chat_message("assistant"):
            try:
                # Force Roman Urdu/English personality
                ans = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Nexus. A human-like assistant. Respond ONLY in English or Roman Urdu. Never use Urdu script."}] + st.session_state.messages
                ).choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except Exception as e: st.error(e)

# --- TAB 3: HUMAN VOICE BOT (EN/UR) ---
with tab_voice:
    st.subheader("🎙️ Nexus Voice Intelligence")
    st.write("Mera naam Nexus hai. Baat karein English ya Roman Urdu mein!")
    audio = mic_recorder(start_prompt="🎤 Start Talking", stop_prompt="🛑 Stop Talking", key='recorder')
    
    if audio and client:
        with st.spinner("Listening..."):
            # 1. Transcribe Voice to Text
            audio_file = BytesIO(audio['bytes'])
            audio_file.name = "voice.wav"
            transcript = client.audio.transcriptions.create(model="whisper-large-v3", file=audio_file).text
            
            # 2. Get AI Response
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Nexus. Speak like a human. Use ONLY English and Roman Urdu. If the user talks to you, respond naturally like a friend."},
                    {"role": "user", "content": transcript}
                ]
            ).choices[0].message.content
            
            # 3. Output Text and Voice
            st.markdown(f"**You said:** {transcript}")
            st.markdown(f"**Nexus:** {response}")
            
            # 4. Generate Human-like Speech
            tts = gTTS(text=response, lang='en') # 'en' works best for Roman Urdu phonetics
            audio_out = BytesIO()
            tts.write_to_fp(audio_out)
            st.audio(audio_out.getvalue(), format="audio/mp3", autoplay=True)

# --- TAB 4: MEDIA STUDIO ---
with tab_media:
    st.subheader("🎨 Free Media Studio")
    m_prompt = st.text_input("What should I create for you?", placeholder="A futuristic car in Lahore...")
    if st.button("✨ Generate Image", use_container_width=True):
        url = f"https://image.pollinations.ai/prompt/{m_prompt.replace(' ', '%20')}"
        st.image(url, caption=m_prompt, use_container_width=True)

# --- TAB 5: LIVE SANDBOX ---
with tab_test:
    st.subheader("🧪 Production Testing")
    test_code = st.text_area("Test Code:", height=150, value='st.balloons()\nst.success("System 100% Active!")')
    if st.button("⚙️ Execute Code"):
        try: exec(test_code)
        except Exception as e: st.error(e)
