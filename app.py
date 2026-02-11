import streamlit as st

st.title("Nexus Voice Diagnostic")

# Simplified audio input to test hardware access
audio_data = st.audio_input("Test Microphone")

if audio_data:
    st.success("✅ Nexus hears you! Processing audio...")
    st.audio(audio_data) # This will play your voice back to you
else:
    st.info("Waiting for voice input... Please click the mic.")
