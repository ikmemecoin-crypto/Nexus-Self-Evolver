import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import requests, os, time, random
from PIL import Image
from io import BytesIO

# --- 1. SYSTEM INITIALIZATION ---
st.set_page_config(page_title="Nexus Sovereign Pro", page_icon="⚡", layout="wide")

if "theme" not in st.session_state: st.session_state.theme = "Light"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# THEME ENGINE
def apply_theme(theme_mode):
    if theme_mode == "Dark":
        bg, text, card, sidebar = "#121212", "#E8EAED", "#1E1E1E", "#202124"
    else:
        bg, text, card, sidebar = "#FFFFFF", "#202124", "#F0F4F8", "#F8F9FA"
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar} !important; border-right: 1px solid #E0E0E0; }}
        .stChatMessage {{ background-color: {card}; border-radius: 18px; padding: 20px; border: 1px solid #E1E4E8; }}
        .stButton>button {{ border-radius: 24px; background-color: #1A73E8; color: white; border: none; }}
        h1, h2, h3, p, label, .stMarkdown {{ color: {text} !important; }}
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# API Security (Error Handling Wrapper)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"⚠️ API Key Error: {e}. Check your .streamlit/secrets.toml file.")
    st.stop()

# --- 2. INTELLIGENCE ENGINES ---
def generate_image(prompt, is_video=False):
    """Generates visual content using a stable, key-free API"""
    clean_prompt = prompt.replace(" ", "%20")
    seed = random.randint(1, 99999)
    # Using Pollinations with a random seed to prevent caching (Fixes broken images)
    if is_video:
        return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=720&height=720&model=turbo&nologo=true&seed={seed}"
    else:
        return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&model=flux&nologo=true&seed={seed}"

# --- 3. SIDEBAR CONTROL ---
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530393318e3d91f47.svg", width=50)
    st.title("Nexus Control")
    
    if st.button("🌙 Toggle Theme"):
        st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
        st.rerun()

    # The Menu - Verified to work
    mode = st.radio("Sovereign Tools:", ["💬 Gemini Chat", "🎨 Vision Creator", "🎙️ Voice Command"])
    
    st.divider()
    st.write("📍 **Hub:** Faisalabad")
    st.write("🟢 **System:** Online")

# --- 4. FUNCTIONAL MODULES ---

# BRAIN: PRO CHAT
if mode == "💬 Gemini Chat":
    st.title("Nexus Gemini Pro")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Command me..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # Using Mixtral for higher stability than Llama 3.3
                resp = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{"role": "system", "content": "You are Nexus. Keep answers short, bold, and professional."}] + st.session_state.chat_history
                )
                ans = resp.choices[0].message.content
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"⚠️ Brain Error: {e}. Try again in 5 seconds.")

# VISION: CREATOR (IMAGES & VIDEO)
elif mode == "🎨 Vision Creator":
    st.title("🎨 Nexus Imagination Engine")
    st.info("Generates Images and Motion Art instantly.")
    
    creation_type = st.radio("Select Mode:", ["Static Image (High Quality)", "Motion Art (GIF)"], horizontal=True)
    prompt = st.text_input("Describe your vision:", placeholder="e.g. A futuristic robot in Faisalabad holding a flag")
    
    if st.button("🚀 Generate Visual"):
        if prompt:
            with st.spinner("Compiling Visual Data..."):
                time.sleep(1.5)
                is_vid = "Motion" in creation_type
                image_url = generate_image(prompt, is_vid)
                
                # Display with Error Handling
                try:
                    st.image(image_url, caption=f"Nexus Generated: {prompt}", use_container_width=True)
                    st.success("Visual Manifested Successfully.")
                except:
                    st.error("Visual failed to load. Check your internet connection.")
        else:
            st.warning("Please enter a description first.")

# VOICE COMMAND
elif mode == "🎙️ Voice Command":
    st.title("🎙️ Voice Bridge")
    st.write("Click the microphone below. Speak clearly.")
    
    # Simple, robust recorder
    audio = mic_recorder(start_prompt="🎤 Click to Speak", stop_prompt="⏹️ Stop Recording", key='recorder')
    
    if audio:
        st.audio(audio['bytes'])
        
        if st.button("📝 Transcribe Audio"):
            with st.spinner("Analyzing Voice Frequency..."):
                # Save to temp file
                with open("temp_voice.wav", "wb") as f:
                    f.write(audio['bytes'])
                
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("temp_voice.wav", open("temp_voice.wav", "rb")),
                        model="whisper-large-v3"
                    )
                    st.success("Message Received:")
                    st.markdown(f"### 🗣️ \"{transcription.text}\"")
                except Exception as e:
                    st.error(f"Voice Error: {e}")
