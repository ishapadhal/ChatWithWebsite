import streamlit as st
from datetime import datetime
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import AIMessage, HumanMessage

# ---------------------------
# PAGE + CSS
# ---------------------------
st.set_page_config(page_title="ChatWithWebsite", page_icon="🌐", layout="wide")

# CSS styling
st.markdown(
    """
    <style>
    /* Page layout */
    .main > div { max-width: 1100px; margin: auto; }

    /* Header */
    .header {
        display:flex; align-items:center; gap:12px;
    }
    .logo {
        width:48px; height:48px; border-radius:10px; background:linear-gradient(135deg,#6EE7B7,#3B82F6);
        display:inline-block; text-align:center; color:white; line-height:48px; font-weight:700;
    }
    .title { font-size:20px; font-weight:700; margin-bottom:4px; }
    .subtitle { font-size:12px; color:#6b7280; margin-top:0; }

    /* Sidebar */
    .stSidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc, #ffffff);
        padding: 18px;
        border-radius: 10px;
    }

    /* Chat area */
    .chat-container { padding: 20px 12px; }
    .bubble {
        display:inline-block;
        padding:12px 14px;
        border-radius:12px;
        margin:6px 0;
        max-width:75%;
        line-height:1.4;
        white-space:pre-wrap;
    }
    .bubble.ai {
        background: #0f172a;
        color: #f8fafc;
        border-bottom-left-radius:12px;
        float:left;
        clear:both;
    }
    .bubble.human {
        background: #eef2ff;
        color:#0f172a;
        border-bottom-right-radius:12px;
        float:right;
        clear:both;
    }
    .meta {
        font-size:11px; color:#6b7280; margin-top:4px;
    }

    /* Summary card */
    .summary {
    background: var(--background-color, #1e293b); /* dark mode support */
    border: 1px solid #334155;
    padding: 12px;
    border-radius: 10px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.4);
    color: var(--text-color, #f1f5f9);    }

    /* Small controls row */
    .controls { display:flex; gap:8px; align-items:center; }
    .btn { padding:8px 12px; border-radius:8px; border:none; cursor:pointer; font-weight:600; }
    .btn.primary { background:#0ea5e9; color:white; }
    .btn.ghost { background:transparent; border:1px solid #e6edf3; color:#0f172a; }

    </style>
    """,
    unsafe_allow_html=True,
)

# header
st.markdown(
    """
    <div class="header">
      <div class="logo">CW</div>
      <div>
        <div class="title">ChatWithWebsite (Offline)</div>
        <div class="subtitle">Load a website and ask questions — runs fully offline after load.</div>
      </div>
    </div>
    <hr/>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Helper functions
# ---------------------------

def load_website_text(url):
    """Load site text and return list of Document chunks"""
    loader = WebBaseLoader(url)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    return splitter.split_documents(docs)

def get_best_chunk(question, chunks, top_n=2):
    """
    Lightweight keyword scoring: counts occurrences of question words in chunks.
    Returns combined text (top_n) cleaned and truncated.
    """
    q_words = [w.strip() for w in question.lower().split() if len(w) > 2]
    if not q_words:
        # fallback: return first chunk
        selected = chunks[:top_n]
        combined = "\n\n".join(c.page_content for c in selected)
        return clean_text(combined)

    scores = []
    for c in chunks:
        text = c.page_content.lower()
        score = sum(1 for w in q_words if w in text)
        scores.append((score, c.page_content))

    # sort descending by score
    scores.sort(key=lambda x: x[0], reverse=True)
    # take top_n with positive score otherwise use first chunks
    top_texts = [t for s, t in scores[:top_n] if s > 0]
    if not top_texts:
        top_texts = [c.page_content for c in chunks[:top_n]]

    combined = "\n\n".join(top_texts)
    return clean_text(combined)

def clean_text(txt):
    # Remove duplicate lines and overly long whitespace, then truncate to safe length
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    unique = list(dict.fromkeys(lines))
    cleaned = "\n".join(unique)
    return cleaned[:7000]

def answer_question_offline(question, chunks):
    context = get_best_chunk(question, chunks, top_n=2)
    # Build short "answer" by returning the most relevant context snippet (no LLM)
    snippet = context[:1500]
    return f"Relevant excerpt from website:\n\n{snippet}"

def render_chat_message(msg, is_ai=True, time=None):
    # Renders a chat bubble using safe HTML
    cls = "ai" if is_ai else "human"
    time_str = time or datetime.now().strftime("%H:%M")
    html = f"""
    <div style="clear:both"></div>
    <div class="bubble {cls}">{msg}</div>
    <div class="meta" style="{'text-align:left' if is_ai else 'text-align:right'}">{time_str}</div>
    <div style="clear:both"></div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Sidebar: controls
# ---------------------------
with st.sidebar:
    st.markdown("### Settings")
    website_url = st.text_input("Website URL", placeholder="https://example.com")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Load Website", key="load_site"):
            if website_url:
                try:
                    st.session_state.chunks = load_website_text(website_url)
                    st.session_state.chat_history = [AIMessage(content="Website loaded! Ask anything 😊")]
                    st.success("Website loaded and indexed (lightweight).")
                except Exception as e:
                    st.error(f"Failed to load website: {e}")
            else:
                st.warning("Please enter a website URL.")

    with col2:
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat_history = [AIMessage(content="Website loaded! Ask anything 😊")]

    st.markdown("---")
    st.markdown("### Quick summary")
    if "chunks" in st.session_state:
        # show a short summary: first 400 chars of the first chunk
        summary_text = st.session_state.chunks[0].page_content[:600].replace("\n", " ")
        st.markdown(f'<div class="summary"><strong>Top snippet:</strong><br/>{summary_text}...</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="summary">No website loaded yet.</div>', unsafe_allow_html=True)

# ---------------------------
# Main chat area
# ---------------------------
st.markdown("<div class='chat-container'></div>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content="Load a website to start chatting.")]

# Chat input area and logic
if "chunks" in st.session_state:
    user_input = st.chat_input("Ask a question about the website...")
    if user_input:
        # append human message
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        # generate offline answer (fast)
        reply = answer_question_offline(user_input, st.session_state.chunks)
        st.session_state.chat_history.append(AIMessage(content=reply))

# display chat messages (most recent last)
for msg in st.session_state.chat_history:
    if isinstance(msg, AIMessage):
        render_chat_message(msg.content, is_ai=True)
    else:
        render_chat_message(msg.content, is_ai=False)
