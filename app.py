import streamlit as st
import json
from groq import Groq
from github import Github

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
st.set_page_config(page_title="Nexus Omni", layout="wide", initial_sidebar_state="collapsed")

# Theme Selection
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

# CSS Variables based on Theme
if st.session_state.theme_mode == "Dark":
    bg, card, text, accent = "#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff"
else:
    bg, card, text, accent = "#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
    /* Professional Card Glassmorphism */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {{
        background: {card}; border-radius: 16px; padding: 24px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }}

    .main-title {{
        font-size: 36px; font-weight: 600;
        background: linear-gradient(120deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    
    [data-testid="stSidebar"] {{ display: none; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PROFESSIONAL HEADER ---
c_head1, c_head2 = st.columns([8, 2])
with c_head1:
    st.markdown('<div class="main-title">Nexus Omni <span style="font-size:14px; color:gray;">v2.2 Agent</span></div>', unsafe_allow_html=True)
with c_head2:
    st.session_state.theme_mode = st.selectbox("Appearance", ["Dark", "Light"], label_visibility="collapsed")

# --- 4. THE CONTROL CENTER ---
col_writer, col_chat = st.columns([4, 6], gap="large")

# --- NEW: TOOL DEFINITIONS ---
def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "list_repo_files",
                "description": "List all files in the repository vault.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the full content of a file from the repo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path/name"}
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or update a file in the repo. Detects if it exists automatically.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "message": {"type": "string", "description": "Optional commit message"}
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": "Delete a file from the repo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"],
                },
            },
        },
    ]

# --- NEW: TOOL EXECUTION HANDLERS ---
def execute_tool(tool_call, repo):
    func_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    try:
        if func_name == "list_repo_files":
            files = [f.path for f in repo.get_contents("")]
            return json.dumps({"files": files})
        
        elif func_name == "read_file":
            path = args["path"]
            file = repo.get_contents(path)
            content = file.decoded_content.decode()
            return json.dumps({"content": content[:15000] + ("..." if len(content) > 15000 else "")})
        
        elif func_name == "write_file":
            path = args["path"]
            content = args["content"]
            message = args.get("message", "Agent update")
            try:
                file = repo.get_contents(path)
                repo.update_file(path, message, content, file.sha)
                return json.dumps({"status": "updated", "path": path})
            except:
                repo.create_file(path, message, content)
                return json.dumps({"status": "created", "path": path})
        
        elif func_name == "delete_file":
            path = args["path"]
            file = repo.get_contents(path)
            repo.delete_file(path, "Agent delete", file.sha)
            return json.dumps({"status": "deleted", "path": path})
            
    except Exception as e:
        return json.dumps({"error": str(e)})

with col_writer:
    st.subheader("✍️ Code Architect")
    with st.container():
        fname = st.text_input("Filename", value="new_logic.py", help="Name your file for GitHub")
        code_body = st.text_area("Source Code", height=300, placeholder="# Enter your logic here...")
        if st.button("🚀 Push to Production", use_container_width=True):
            if repo:
                with st.spinner("Syncing with Vault..."):
                    try:
                        try:
                            f = repo.get_contents(fname)
                            repo.update_file(fname, "Architect Update", code_body, f.sha)
                        except:
                            repo.create_file(fname, "Architect Deploy", code_body)
                        st.toast("Deployment Successful!", icon='✅')
                        st.rerun()
                    except Exception as e: 
                        st.error(e)
            else:
                st.error("Repo not connected")

    st.markdown("---")
    st.subheader("📁 Repository Vault")
    with st.container():
        if repo:
            try:
                files = repo.get_contents("")
                for f in files:
                    if f.type == "file":
                        with st.expander(f"📄 {f.name} ({f.size} bytes)"):
                            st.code(f.decoded_content.decode()[:1000] + ("..." if len(f.decoded_content) > 1000 else ""), language='python')
                            if st.button("Delete", key=f"del_{f.sha}"):
                                repo.delete_file(f.path, "Manual remove", f.sha)
                                st.rerun()
            except Exception as e:
                st.info(f"Error loading files: {e}")
        else:
            st.info("Repo not connected")

with col_chat:
    st.subheader("💬 Nexus Intelligent Agent")
    chat_box = st.container(height=580, border=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with chat_box.chat_message(m["role"]):
            st.markdown(m["content"])

    # PRO SUGGESTIONS
    s1, s2, s3, s4 = st.columns(4)
    p_cmd = None
    if s1.button("🔍 Audit Code"): 
        p_cmd = "Audit the most recent Python file in the repo for issues and fix them if needed."
    if s2.button("📐 UI UX"): 
        p_cmd = "Suggest 3 concrete ways to make this Streamlit app look even more professional and modern."
    if s3.button("🧠 Sync Memory"): 
        p_cmd = "Read memory_general.json (create it if missing), summarize our current progress and goals, then suggest next steps."
    if s4.button("🚀 Build Tool"): 
        p_cmd = "Create a useful utility script (e.g., data analyzer or text processor) and save it to the repo."

    # Define query BEFORE the processing block
    query = st.chat_input("Command the Nexus...") or p_cmd

# === AGENT PROCESSING (outside the column to avoid ordering issues) ===
if query and client and repo:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_box.chat_message("user"): 
        st.markdown(query)
    
    with chat_box.chat_message("assistant"):
        with st.spinner("Nexus Thinking..."):
            messages = [
                {"role": "system", "content": """You are Nexus Omni, an ultra-powerful autonomous AI agent with full read/write access to the GitHub repository vault via tools.
Use tools proactively to list, read, write, and delete files as needed to complete tasks.
Always reason step-by-step before acting.
Store persistent knowledge, progress, and goals in memory_general.json.
Be ambitious, concise, and effective. If a file doesn't exist when needed, create it."""}
            ]
            # Add recent history for context (increased to 15)
            messages.extend(st.session_state.messages[-15:])
            
            final_response = ""
            tool_feedback = ""
            while True:
                try:
                    comp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        tools=get_tools(),
                        tool_choice="auto",
                        max_tokens=4096,
                        temperature=0.7
                    )
                    choice = comp.choices[0].message
                    
                    if choice.content:
                        final_response += choice.content + "\n\n"
                    
                    if not hasattr(choice, "tool_calls") or not choice.tool_calls:
                        break
                    
                    # Handle parallel tool calls
                    for tool_call in choice.tool_calls:
                        result = execute_tool(tool_call, repo)
                        result_obj = json.loads(result)
                        status = result_obj.get("status", "done")
                        path = result_obj.get("path", "")
                        tool_feedback += f"**Executed {tool_call.function.name}** → {status} {path}\n"
                        
                        messages.append(choice)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": result
                        })
                
                except Exception as e:
                    final_response += f"\nError during processing: {str(e)}"
                    break
            
            # Combine response with tool feedback
            full_output = tool_feedback + final_response if tool_feedback else final_response
            full_output = full_output.strip() or "Task complete. No further actions needed."
            
            st.markdown(full_output)
            st.session_state.messages.append({"role": "assistant", "content": full_output})
            st.rerun()
