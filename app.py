import streamlit as st
from google import genai
from google.genai import types

# --- 1. App Configuration ---
st.set_page_config(page_title="Nexus Ultra", page_icon="🚀", layout="wide")

# Retrieve API Key from Streamlit Secrets
# Setup: In Streamlit Cloud, go to Settings -> Secrets and add GEMINI_API_KEY = "your_key"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

# Primary Model: Gemini 2.5 Flash (Balanced speed and high limits)
MODEL_ID = "gemini-2.5-flash"

# --- 2. Initialize Nexus Engine ---
def get_nexus_response(prompt, chat_history):
    if not GEMINI_API_KEY:
        return "Error: API Key not found. Please check your Streamlit Secrets."
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    try:
        # Create a chat session with the provided history
        chat = client.chats.create(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            ),
            history=chat_history
        )
        
        response = chat.send_message(prompt)
        return response.text
    
    except Exception as e:
        return f"Nexus System Error: {str(e)}"

# --- 3. Streamlit UI Layout ---
st.title("🌐 Nexus Ultra Alpha")
st.caption("Powered by Gemini 2.5 Flash | Status: Optimal")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Logic
if user_query := st.chat_input("Ask Nexus anything..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("user"):
        st.markdown(user_query)

    # Convert Streamlit history to Google GenAI format
    # Note: 'user' messages stay 'user', but 'assistant' must be 'model' for Gemini
    formatted_history = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        formatted_history.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Processing through Nexus nodes..."):
            response_text = get_nexus_response(user_query, formatted_history)
            st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
