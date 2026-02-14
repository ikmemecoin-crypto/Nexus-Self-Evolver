import json
from groq import Groq
from github import Github
import streamlit as st

# ... (keep your existing init_nexus, theme, header, etc.)

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
                "description": "Create or update a file in the repo. Detects if it exists.",
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
            return json.dumps({"content": content[:10000] + ("..." if len(content) > 10000 else "")})  # Truncate if huge
        
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

# --- UPGRADED CHAT WITH AGENT LOOP ---
if query and client:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_box.chat_message("user"): 
        st.markdown(query)
    
    with chat_box.chat_message("assistant"):
        with st.spinner("Nexus Thinking..."):
            # System prompt for powerful agent behavior
            messages = [
                {"role": "system", "content": "You are Nexus Omni, an ultra-powerful AI agent. You have full access to the GitHub repository vault via tools. Use tools proactively to read/write/manage files when needed. Reason step-by-step, then act. For memory, use memory_general.json. Be concise but thorough."}
            ]
            # Add recent chat history for context
            messages.extend(st.session_state.messages[-10:])  # Last 10 for context
            
            final_response = ""
            while True:
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
                    final_response += choice.content
                
                if not choice.tool_calls:
                    break  # Final answer
                
                # Handle tool calls (supports parallel)
                for tool_call in choice.tool_calls:
                    result = execute_tool(tool_call, repo)
                    messages.append(choice)  # Append assistant message with tool call
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result
                    })
                    final_response += f"\n[Used tool: {tool_call.function.name}]\n"
            
            st.markdown(final_response or "Task complete.")
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            st.rerun()
