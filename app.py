import os
import json
import uuid
import streamlit as st
import chromadb
from google import genai

# ─── SETUP ───────────────────────────────────────────────────────────────────
api_key = "AQ.Ab8RN6LTbqwose4rUEKuJ5JlA7G2sOKihmODkEA_rvV92-Po8A"
os.environ["GEMINI_API_KEY"] = api_key
gemini = genai.Client()

db = chromadb.PersistentClient(path="./chroma_data")
collection = db.get_collection(name="notebook")

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, indent=2)

def chat_title(msgs):
    for m in msgs:
        if m["role"] == "user":
            t = m["content"][:30]
            return t + "…" if len(m["content"]) > 30 else t
    return "New Chat"

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mini NotebookLM",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ─── MINIMAL CSS — only styles the chat area, NOT the sidebar ────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, .stApp { font-family: 'Inter', sans-serif !important; }
#MainMenu, header, footer { visibility: hidden; }

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 6rem !important;
    max-width: 780px !important;
}

/* Welcome */
.welcome-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-height: 65vh; text-align: center; padding: 2rem 1rem;
}
.welcome-title {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -0.04em;
    line-height: 1.2; color: #ffffff; margin-bottom: 0.6rem;
}
.welcome-grad {
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.welcome-sub {
    font-size: 0.95rem; color: #71717a; margin-bottom: 2.5rem;
    max-width: 420px; line-height: 1.7;
}
.chips-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; max-width: 520px; width: 100%; }
.chip {
    background: #18181b; border: 1px solid #27272a; border-radius: 0.9rem;
    padding: 0.85rem 1rem; text-align: left; transition: all 0.2s ease;
}
.chip:hover { border-color: #3b82f6; background: #1a2744; transform: translateY(-2px); }
.chip-icon { font-size: 1.2rem; display: block; margin-bottom: 0.3rem; }
.chip-title { font-size: 0.82rem; font-weight: 600; color: #f4f4f5; display: block; }
.chip-desc { font-size: 0.73rem; color: #71717a; display: block; }

/* Chat messages */
.stChatMessage { background: transparent !important; border: none !important; }
.stChatMessage div[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    border-radius: 8px !important;
}
.stChatMessage div[data-testid="chatAvatarIcon-user"] {
    background: #27272a !important; border-radius: 8px !important;
}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) { flex-direction: row-reverse !important; }
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] p {
    background: #1e3a5f !important; color: #dbeafe !important;
    padding: 0.65rem 1.1rem !important; border-radius: 1.1rem 1.1rem 0.2rem 1.1rem !important;
    display: inline-block !important; font-size: 0.88rem !important; line-height: 1.6 !important;
}

/* Input */
.stChatInputContainer {
    border-radius: 1.2rem !important; border: 1px solid #27272a !important;
}
.stChatInputContainer:focus-within { border-color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

history = load_history()

if st.session_state.current_id is None:
    nid = str(uuid.uuid4())
    history[nid] = []
    save_history(history)
    st.session_state.current_id = nid
    st.session_state.messages = []

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — using plain st.sidebar, NO custom CSS on it
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("✨ NotebookLM")

    # New Chat button
    if st.button("＋  New Chat", use_container_width=True, type="primary"):
        nid = str(uuid.uuid4())
        history[nid] = []
        save_history(history)
        st.session_state.current_id = nid
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("RECENT CHATS")

    # List each saved chat as a button
    for cid in reversed(list(history.keys())):
        msgs = history[cid]
        title = chat_title(msgs) if msgs else "Empty Chat"
        is_active = (cid == st.session_state.current_id)
        label = f"▸ {title}" if is_active else title
        if st.button(label, key=f"h_{cid}", use_container_width=True):
            st.session_state.current_id = cid
            st.session_state.messages = history[cid]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
msgs = st.session_state.messages

# Welcome screen
if not msgs:
    st.markdown("""
<div class="welcome-wrap">
    <div class="welcome-title">Hi, <span class="welcome-grad">Usman</span> 👋</div>
    <div class="welcome-sub">
        Interact with your notes and explore your personal knowledge base. Ask me anything.
    </div>
    <div class="chips-grid">
        <div class="chip">
            <span class="chip-icon">📌</span>
            <span class="chip-title">What am I building?</span>
            <span class="chip-desc">Recap your current project</span>
        </div>
        <div class="chip">
            <span class="chip-icon">🎯</span>
            <span class="chip-title">What is my goal?</span>
            <span class="chip-desc">Understand your objective</span>
        </div>
        <div class="chip">
            <span class="chip-icon">🛠️</span>
            <span class="chip-title">What tools am I using?</span>
            <span class="chip-desc">See your tech stack</span>
        </div>
        <div class="chip">
            <span class="chip-icon">💡</span>
            <span class="chip-title">What is RAG?</span>
            <span class="chip-desc">Explained from your notes</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Display chat messages
for m in msgs:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat input
if question := st.chat_input("Ask anything about your notes…"):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            embed_r = gemini.models.embed_content(
                model="gemini-embedding-2", contents=question
            )
            q_vec = embed_r.embeddings[0].values
            results = collection.query(query_embeddings=[q_vec], n_results=2)
            context = "\n".join(results["documents"][0])

            prompt = f"""You are Mini NotebookLM, a helpful AI assistant.
Use ONLY the following Context (from the user's personal notes) to answer.
If the answer is not in the notes, say so politely. Be concise and friendly.

Context:
{context}

Question: {question}"""

            ans = gemini.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            st.markdown(ans.text)

    st.session_state.messages.append({"role": "assistant", "content": ans.text})
    history[st.session_state.current_id] = st.session_state.messages
    save_history(history)
