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

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

if st.session_state.theme_mode == "Dark":
    bg, card, text, accent = "#0E1117", "#1A1C23", "#E0E0E0", "#58a6ff"
else:
    bg, card, text, accent = "#F0F2F6", "#FFFFFF", "#1E1E1E", "#007BFF"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; background-color: {bg} !important; color: {text} !important; }}
    
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
c_head1, c_head2, c_head3 = st.columns([6, 2, 2])
with c_head1:
    st.markdown('<div class="main-title">Nexus Omni <span style="font-size:14px; color:gray;">v2.3 Agent</span></div>', unsafe_allow_html=True)
with c_head2:
    st.session_state.theme_mode = st.selectbox("Appearance", ["Dark", "Light"], label_visibility="collapsed")
with c_head3:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. TOOL DEFINITIONS ---
def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "list_repo_files",
                "description": "List all files in the repository (top-level only).",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the full content of a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Exact filename or path"}
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or overwrite a file.",
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
                "description": "Delete a file.",
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

# --- 5. TOOL EXECUTION ---
def execute_tool(tool_call, repo):
    func_name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in tool arguments"})
    
    try:
        if func_name == "list_repo_files":
            files = [f.path for f in repo.get_contents("")]
            return json.dumps({"files": files})
        
        elif func_name == "read_file":
            path = args["path"]
            file = repo.get_contents(path)
            content = file.decoded_content.decode("utf-8")
            return json.dumps({"content": content[:20000] + ("..." if len(content) > 20000 else "")})
        
        elif func_name == "write_file":
            path = args["path"]
            content = args["content"]
            message = args.get("message", "Agent write")
            try:
                existing = repo.get_contents(path)
                repo.update_file(path, message, content, existing.sha)
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

# --- 6. CONTROL CENTER ---
col_writer, col_chat = st.columns([4, 6], gap="large")

with col_writer:
    st.subheader("✍️ Code Architect")
    fname = st.text_input("Filename", value="new_tool.py")
    code_body = st.text_area("Source Code", height=300, placeholder="# Your code...")
    if st.button("🚀 Push to Production", use_container_width=True):
        if repo:
            with st.spinner("Deploying..."):
                try:
                    try:
                        f = repo.get_contents(fname)
                        repo.update_file(fname, "Manual update", code_body, f.sha)
                    except:
                        repo.create_file(fname, "Manual create", code_body)
                    st.toast("Success!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(e)
        else:
            st.error("Repo offline")

    st.markdown("---")
    st.subheader("📁 Repository Vault")
    if repo:
        try:
            files = repo.get_contents("")
            for f in files:
                if f.type == "file":
                    with st.expander(f"📄 {f.name} ({f.size} bytes)"):
                        st.code(f.decoded_content.decode("utf-8")[:1500] + ("..." if f.size > 1500 else ""), language="python")
                        # UNIQUE KEY USING PATH (fixes duplicate key error)
                        safe_key = f"del_{f.path.replace('/', '__').replace('.', '_')}"
                        if st.button("Delete", key=safe_key):
                            repo.delete_file(f.path, "Manual delete", f.sha)
                            st.rerun()
        except Exception as e:
            st.error(f"Vault error: {str(e)}")
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

    s1, s2, s3, s4 = st.columns(4)
    p_cmd = None
    if s1.button("🔍 Audit Code"): 
        p_cmd = "List all files, then audit the main Python files for bugs or improvements and fix them."
    if s2.button("📐 UI UX"): 
        p_cmd = "Suggest 3 advanced UI improvements for this Streamlit app (e.g., tabs, file tree, voice input)."
    if s3.button("🧠 Sync Memory"): 
        p_cmd = "If memory_general.json exists, read it and summarize progress. If not, create it with initial goals: build the world's most powerful AI app."
    if s4.button("🚀 Build Tool"): 
        p_cmd = "Create a new Python utility script (e.g., text summarizer or calculator) and save it to the repo."

    query = st.chat_input("Command the Nexus...") or p_cmd

# --- 7. AGENT PROCESSING ---
if query and client and repo:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_box.chat_message("user"): 
        st.markdown(query)
    
    with chat_box.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = [
                {"role": "system", "content": """You are Nexus Omni v2.3, an autonomous AI agent with full control over the GitHub repo via tools.
Use tools ONLY when needed. Always reason step-by-step.
CRITICAL: Tool arguments MUST exactly match the schema:
- read_file, write_file, delete_file: use "path" (string, exact filename)
- list_repo_files: no arguments
- write_file: "path" and "content" required

Examples:
To read: {"name": "read_file", "arguments": {"path": "memory_general.json"}}
To write: {"name": "write_file", "arguments": {"path": "new.py", "content": "print('hello')"}}

Persistent memory: use memory_general.json (create if missing).
Be proactive and ambitious."""}
            ]
            messages.extend(st.session_state.messages[-20:])  # Longer context
            
            final_response = ""
            tool_feedback = ""
            max_loops = 8  # Prevent infinite loop
            for _ in range(max_loops):
                try:
                    comp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        tools=get_tools(),
                        tool_choice="auto",
                        max_tokens=4096,
                        temperature=0.6
                    )
                    choice = comp.choices[0].message
                    
                    if choice.content:
                        final_response += choice.content + "\n\n"
                    
                    if not getattr(choice, "tool_calls", None):
                        break
                    
                    tool_feedback = ""
                    for tool_call in choice.tool_calls:
                        result = execute_tool(tool_call, repo)
                        result_obj = json.loads(result) if result.startswith("{") else {"raw": result}
                        status = result_obj.get("status", result_obj.get("error", "done"))
                        tool_feedback += f"**{tool_call.function.name}** → {status}\n"
                        
                        messages.append(choice)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": result
                        })
                
                except Exception as e:
                    error_msg = str(e)
                    if "validation failed" in error_msg.lower():
                        final_response += f"\n⚠️ Tool validation error detected. Correcting and retrying...\n"
                        messages.append({"role": "system", "content": f"Previous tool call failed validation: {error_msg}. Fix the arguments and try again."})
                    else:
                        final_response += f"\n❌ Error: {error_msg}"
                        break
            
            full_output = (tool_feedback + "\n" + final_response).strip() or "Task complete."
            st.markdown(full_output)
            st.session_state.messages.append({"role": "assistant", "content": full_output})
            st.rerun()
