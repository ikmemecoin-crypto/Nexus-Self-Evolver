# FEATURE 3: PYTHON LAB (Local Sandbox with Console)
if usage_mode == "Python Lab":
    st.info("🧪 **Python Lab Mode**: Run local scripts without using API tokens.")
    
    # Use a form to capture the "Run" action better
    with st.form("lab_form"):
        code_input = st.text_area("Write Python Code here...", 
                                  value='print("Nexus is ready")', 
                                  height=200,
                                  help="Type your code and click Run below.")
        run_submitted = st.form_submit_button("▶️ Run Script")

    if run_submitted:
        st.markdown("### 🖥️ Console Output")
        # We use a container to make it look like a real terminal
        with st.container():
            st.markdown('<div style="background-color: #000; color: #0f0; padding: 15px; border-radius: 10px; font-family: monospace;">', unsafe_allow_html=True)
            try:
                # This captures print statements so they show up in the app
                from contextlib import redirect_stdout
                import io
                f = io.StringIO()
                with redirect_stdout(f):
                    exec(code_input)
                s = f.getvalue()
                st.text(s if s else "Script executed successfully with no output.")
            except Exception as e:
                st.error(f"Execution Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
