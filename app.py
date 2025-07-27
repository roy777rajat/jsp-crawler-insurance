import os
import streamlit as st
import streamlit.components.v1 as components
import json
from utils.s3_utils import (
    list_jsp_files_s3,
    get_jsp_html,
    check_aws_connection,
    get_websocket_url_local,
    get_websocket_url_server
)
#import utils.s3_utils as s3_utils


# --- Config ---
st.set_page_config(layout="wide", page_title="I-Helper")
JSP_FOLDER = r"E:\01. Python Basic\jsp-crwaler-ai\jsp"

websocket_url =""
# --- Utils ---
# def list_jsp_files(directory):
#     try:
#         files = [f for f in os.listdir(directory) if f.endswith(".jsp")]
#         files.sort()
#         return files
#     except Exception as e:
#         st.error(f"Error listing JSP files: {e}")
#         return []

# jsp_files = list_jsp_files(JSP_FOLDER)
# jsp_files_json = json.dumps(jsp_files)


# --- Determine Environment (local or cloud) ---
def is_local_environment():
    # Streamlit Cloud sets SERVER_PORT to 80 or 8501; locally it's usually 8501
    return os.path.exists(JSP_FOLDER)

# --- JSP Loader: Local or S3 ---
if is_local_environment():
    websocket_url = get_websocket_url_local()
    if websocket_url is None:
        st.error("Running in local environment. Websocket URL not found.")
    else:
        st.info("Running in Local Environment. Websocket URL is set to: " + websocket_url)
    def list_jsp_files():
        try:
            files = [f for f in os.listdir(JSP_FOLDER) if f.endswith(".jsp")]
            files.sort()
            
            return files
        except Exception as e:
            st.error(f"Error listing local JSP files: {e}")
            return []
else:
    websocket_url = get_websocket_url_server()
    if websocket_url is None:
        st.error("Running in Server environment. Websocket URL not found.")
    
    def list_jsp_files():
        if not check_aws_connection():
            st.error("Unable to connect to AWS from streamlit. Please check your credentials.")
            return []
    
        try:
            files = list_jsp_files_s3("jsp-legacy-codes")
            files = [f.split("/")[-1] for f in files if f.endswith(".jsp")]
            files.sort()
            
            return files
        except Exception as e:
            st.error(f"Error listing S3 JSP files: {e}")
            return []

# --- Load JSP Files ---
jsp_files = list_jsp_files()
jsp_files_json = json.dumps(jsp_files)



# --- Display Notice ---
st.info("💬 Welcome to I-Helper, Where Insurance mixed with AI !!")

# --- Render HTML UI ---
jsp_buttons_html = "".join(
    f'<button class="jsp-btn" data-jsp="{jsp}">{jsp.replace(".jsp", "")}</button><br>'
    for jsp in jsp_files
)



components.html(f"""
<div id="jsp-panel">
    <h4>📄 Navigation Tree</h4>
    {jsp_buttons_html}
</div>

<div id="main-dashboard">
    <h1>📊 Insurance Intelligence Console
</h1>
    <div class="dashboard">
        <div class="kpi-card"><div class="kpi-title">Claims</div><div class="kpi-value">1,240</div></div>
        <div class="kpi-card"><div class="kpi-title">Quotations</div><div class="kpi-value">3,850</div></div>
        <div class="kpi-card"><div class="kpi-title">Policies</div><div class="kpi-value">2,135</div></div>
        <div class="kpi-card"><div class="kpi-title">Active Customers</div><div class="kpi-value">980</div></div>
        <div class="kpi-card"><div class="kpi-title">Payout</div><div class="kpi-value">$1.9M</div></div>
    </div>
</div>

<div id="floating-chat">
    <div id="chat-header">🤖 I-Helper</div>
    <div id="chat-messages">
        <div class="chat-message bot">👋 Hi! I'm your Insurance assistant.</div>
        <div class="chat-message user">How to launch a new Fund?</div>
        <div class="chat-message bot">I want to change Sum Assured for a policy. Help me?</div>
        <div class="chat-message bot">Where can I see Claim Intimation date?</div>
    </div>
    <div id="chat-input">
        <input type="text" id="userInput" placeholder="Ask your question..." maxlength="250">
        <button id="sendBtn">Send</button>
    </div>
</div>

<style>
body {{
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    background: #f2f4f8;
}}

#jsp-panel {{
    position: fixed;
    left: 10px;
    top: 10px;
    width: 220px;
    max-height: 92vh;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
    background: #f8f8f8;
    box-shadow: 1px 1px 6px rgba(0,0,0,0.08);
    font-size: 13px;
    z-index: 999;
}}

.jsp-btn {{
    width: 100%;
    margin: 3px 0;
    padding: 6px 8px;
    font-size: 12px;
    border-radius: 5px;
    border: 1px solid #ccc;
    background-color: #fff;
    cursor: pointer;
    text-align: left;
}}

#main-dashboard {{
    margin-left: 250px;
    margin-right: 400px;
    padding-top: 30px;
}}

#main-dashboard h1 {{
    margin-bottom: 30px;
    font-size: 28px;
    color: #333;
    text-align: center;
}}

.dashboard {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    max-width: 1000px;
    margin: auto;
}}

.kpi-card {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: all 0.3s ease;
}}

.kpi-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12);
}}

.kpi-title {{
    font-size: 16px;
    font-weight: 600;
    color: #555;
    margin-bottom: 10px;
}}

.kpi-value {{
    font-size: 24px;
    font-weight: bold;
    color: #0073e6;
}}

#floating-chat {{
    position: fixed;
    top: 20px;
    right: 20px;
    width: 360px;
    height: 420px;
    background: #fefefe;
    border: 1px solid #aaa;
    border-radius: 10px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    display: flex;
    flex-direction: column;
    font-size: 13px;
    z-index: 1000;
}}

#chat-header {{
    background: #2c3e50;
    color: white;
    padding: 10px;
    font-weight: bold;
    font-size: 14px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}}

#chat-messages {{
    flex: 1;
    padding: 8px;
    overflow-y: auto;
    background-color: #fff;
}}

#chat-input {{
    display: flex;
    padding: 8px;
    background: #f1f1f1;
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}}

#chat-input input {{
    flex: 1;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 5px;
}}

#chat-input button {{
    margin-left: 6px;
    padding: 6px 10px;
    background: #1e88e5;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}}

@keyframes blink {{
    0%, 100% {{ background-color: yellow; }}
    50% {{ background-color: transparent; }}
}}

.blink {{
    animation: blink 0.6s ease-in-out 3;
    border: 2px solid orange !important;
    font-weight: bold;
}}
</style>

<script>
var jspFiles = {jsp_files_json};

function scrollChat() {{
    var chatBox = document.getElementById("chat-messages");
    chatBox.scrollTop = chatBox.scrollHeight;
}}

function appendMessage(sender, msg) {{
    var p = document.createElement("p");
    p.innerHTML = "<strong>" + sender + ":</strong> " + msg;
    document.getElementById("chat-messages").appendChild(p);
    scrollChat();
}}

function blinkButtons(jspNames) {{
    const lowerSet = jspNames.map(j => j.toLowerCase().trim());
    const allButtons = document.querySelectorAll('.jsp-btn');
    allButtons.forEach(btn => {{
        const label = btn.textContent.toLowerCase().trim()+".jsp";
        console.log("Checking button:", label);
        console.log("Against set:", lowerSet);
        if (lowerSet.includes(label)) {{
            btn.classList.add("blink");
            console.log("Blinking button:", label);
            setTimeout(() => {{
                btn.classList.remove("blink");
            }}, 15000);
        }}
    }});
}}

var ws = new WebSocket("{websocket_url}");


ws.onopen = function() {{
    appendMessage("🟢", "Connected to I-Helper, Your 24x7 assistant !! @Powered by Rajat");
}};

ws.onmessage = function(event) {{
    try {{
        var data = JSON.parse(event.data);
        var botMsg = "";

        if (data.body) {{
            var body = JSON.parse(data.body);
            if (body.bot) botMsg = body.bot;
        }} else if (data.bot) {{
            botMsg = data.bot;
        }}

        if (botMsg) {{
            appendMessage("🤖 I-Helper(Rajat)", botMsg);

            var regex = /`?(\w+\.jsp)`?/gi;
            var match;
            var matchesSet = new Set();

            while ((match = regex.exec(botMsg)) !== null) {{
                
                const cleaned = match[1].replace(/[^\w.]/g, '');
                matchesSet.add(cleaned);
            }}
            var matches = Array.from(matchesSet);

            console.log("Raw unique matches:", matches);
            

            var valid = matches.filter(m => jspFiles.includes(m));
            
            console.log("Valid JSP files:", valid);
            if (valid.length > 0) {{
                console.log("Relevant JSP files found:", valid);
            }} else {{
                console.log("No Relevant JSP files found:", valid);
            }}
            if (valid.length > 0) {{
                blinkButtons(valid);
            }}
        }}
    }} catch (e) {{
        appendMessage("❓", event.data);
    }}
}};

ws.onerror = function() {{
    appendMessage("⚠️", "WebSocket error");
}};

ws.onclose = function() {{
    appendMessage("🔴", "Disconnected from AI");
}};

document.getElementById("sendBtn").onclick = sendMessage;
document.getElementById("userInput").addEventListener("keydown", function(e) {{
    if (e.key === "Enter") sendMessage();
}});

function sendMessage() {{
    var input = document.getElementById("userInput");
    var text = input.value.trim();
    if (!text) return;
    appendMessage("🧑‍💻 You", text);
    ws.send(JSON.stringify({{
        action: "qna",
        message: text
    }}));
    input.value = "";
}}
</script>
""", height=800)

