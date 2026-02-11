st.markdown("""
<style>

/* ---------------- GLOBAL THEME ---------------- */

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

html, body, [class*="st-"] {
    font-family: 'Outfit', sans-serif;
    background-color: #1e1f20;
    color: #e3e3e3;
}

/* ---------------- HIDE STREAMLIT DEFAULT ELEMENTS ---------------- */

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---------------- SIDEBAR STYLING ---------------- */

section[data-testid="stSidebar"] {
    background-color: #131314 !important;
    border-right: 1px solid #2a2b2d;
}

/* Keep collapse button working but clean */
[data-testid="collapsedControl"] span {
    display: none !important;   /* remove text glitch */
}

/* ---------------- MAIN AREA ---------------- */

.main {
    background-color: #1e1f20;
}

/* Gradient Header */
.nexus-header {
    font-size: 2.8rem;
    font-weight: 600;
    background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2rem;
}

/* ---------------- CHAT MESSAGE STYLE ---------------- */

div[data-testid="stChatMessage"] {
    background-color: #2b2d2f !important;
    border-radius: 18px !important;
    padding: 16px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

/* User message differentiation */
div[data-testid="stChatMessage"][aria-label="user"] {
    background-color: #232425 !important;
}

/* ---------------- CHAT INPUT ---------------- */

.stChatInputContainer {
    position: fixed;
    bottom: 20px;
    left: 0;
    right: 0;
    padding-left: 300px; /* adjust if sidebar width changes */
    padding-right: 30px;
    background-color: #1e1f20;
}

/* Input box styling */
textarea {
    border-radius: 25px !important;
}

/* ---------------- BUTTONS ---------------- */

button[kind="primary"] {
    background: linear-gradient(90deg, #4285f4, #9b72cb);
    border: none !important;
    border-radius: 20px !important;
}

/* ---------------- SCROLLBAR ---------------- */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #3a3b3d;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}

</style>
""", unsafe_allow_html=True)
