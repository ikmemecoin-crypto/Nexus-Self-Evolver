# --- TAB 4: MEDIA STUDIO (100% FREE TIER) ---
with tab_media:
    st.subheader("🎨 Free Media Studio")
    st.markdown("Generates images natively without paid API keys.")
    
    m_type = st.radio("Media Type", ["Picture", "Video Generation Prompt"], horizontal=True)
    m_prompt = st.text_input("Creative Prompt", placeholder="e.g., A futuristic city at sunset...")
    
    if st.button("✨ Generate Asset", use_container_width=True):
        if not m_prompt:
            st.warning("Please enter a prompt first.")
        elif m_type == "Picture":
            with st.spinner("Generating Image via Open-Source Engine..."):
                try:
                    # Uses a free URL-based generation service requiring no API key
                    formatted_prompt = m_prompt.replace(" ", "%20")
                    image_url = f"https://image.pollinations.ai/prompt/{formatted_prompt}"
                    st.image(image_url, caption=m_prompt, use_container_width=True)
                    st.success("Image generated successfully! Right-click to save.")
                except Exception as e:
                    st.error(f"Generation failed: {e}")
        
        elif m_type == "Video Generation Prompt":
            st.info("High-fidelity video requires massive server power. To get a free Veo video, copy the optimized prompt below and paste it into the Gemini chat.")
            st.code(f"Gemini, please use your Veo model to generate a high-fidelity video with audio based on this description: {m_prompt}")
