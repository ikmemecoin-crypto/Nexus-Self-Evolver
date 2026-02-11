import streamlit as st
from google import genai
from tavily import TavilyClient
import os

st.set_page_config(page_title="NEXUS: Self-Evolving AI", layout="wide")
st.title("🌐 NEXUS CORE: Phase 1")

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
TAVILY_KEY = st.secrets["TAVILY_API_KEY"]

client = genai.Client(api_key=GEMINI_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

query = st.text_input("What should Nexus learn or do today?", placeholder="e.g., Research the latest AI breakthroughs today...")

if st.button("Execute Command"):
    with st.spinner("Searching the global net..."):
        search_result = tavily.search(query=query, search_depth="advanced")
        context = str(search_result)

    with st.spinner("NEXUS is processing knowledge..."):
        prompt = f"Using this internet data: {context}. Answer the user request: {query}. Also, suggest one way you could update your own code to better handle this type of task in the future."
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        st.subheader("Knowledge Synthesis")
        st.write(response.text)
        st.info("💡 Self-Evolution Suggestion logged. Waiting for your permission to update code.")
