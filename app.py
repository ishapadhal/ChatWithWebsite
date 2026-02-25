import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pathlib import Path

# ---------------------------
# LOAD ENV
# ---------------------------

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(" GEMINI_API_KEY not found in .env")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

for m in genai.list_models():
    print(m.name)

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(page_title="ChatWithWebsite (Gemini)", layout="wide")
st.title("🌐 ChatWithWebsite")

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def load_website_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch website. Status: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator="\n").strip()

    if not text:
        raise Exception("Website returned empty content.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
    )

    return splitter.create_documents([text])


def get_best_chunk(question, chunks):
    q_words = [w.lower() for w in question.split() if len(w) > 2]

    scores = []
    for c in chunks:
        text = c.page_content.lower()
        score = sum(1 for w in q_words if w in text)
        scores.append((score, c.page_content))

    scores.sort(reverse=True)

    return scores[0][1] if scores else ""


def answer_question_gemini(question, chunks):
    context = get_best_chunk(question, chunks)

    prompt = f"""
Answer the question using ONLY the website content below.

Website Content:
{context}

Question:
{question}
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f" Gemini API Error:\n{str(e)}"

# ---------------------------
# SIDEBAR
# ---------------------------

with st.sidebar:
    st.header("Settings")
    website_url = st.text_input("Website URL", placeholder="https://example.com")

    if st.button("Load Website"):
        if website_url:
            try:
                st.session_state.chunks = load_website_text(website_url)
                st.session_state.chat_history = [
                    {"role": "assistant", "content": "Website loaded! Ask anything 😊"}
                ]
                st.success("Website loaded successfully!")
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Enter a website URL.")

    if st.button("Clear Chat"):
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Website loaded! Ask anything 😊"}
        ]

# ---------------------------
# MAIN CHAT
# ---------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Load a website to start chatting."}
    ]

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if "chunks" in st.session_state:
    user_input = st.chat_input("Ask a question about the website...")

    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.spinner("Thinking with Gemini..."):
            reply = answer_question_gemini(user_input, st.session_state.chunks)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )

        st.rerun()