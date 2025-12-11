📘 ChatWithWebsite — A Simple Offline Website Q&A Assistant

A fast, offline, lightweight chatbot that answers questions based on any website you provide — without needing Google API, OpenAI API, or embeddings.

This project lets users paste a website URL, extract the content, split it into readable chunks, and answer questions using a simple, offline keyword-based retrieval system.

It is designed for:

✔ People with low RAM laptops (4GB)
✔ No API keys
✔ Zero costs
✔ Very fast response time
✔ Works entirely on your local machine using Streamlit

⭐ Features
🔹 1. Paste Any Website URL

Load any publicly available webpage and extract its content automatically.

🔹 2. No API Keys Required

This version uses offline keyword-matching logic instead of Gemini/OpenAI embeddings, making it:

100% free

Private

Fast

Lightweight

🔹 3. Smart Chunking

Uses LangChain’s RecursiveCharacterTextSplitter to chunk website text into meaningful pieces.

🔹 4. Ask Unlimited Questions

Each question is answered based on the chunk most related to your query.

🔹 5. Chat UI Built With Streamlit

A friendly dark-themed interface with chat bubbles.

🔹 6. Fully Offline Processing

No data is sent to any external server.

🖼 App Preview
Homepage – Enter Website URL
Chat Interface
🧠 How It Works (Offline RAG Logic)

User enters website URL

Website content is loaded using WebBaseLoader

Text is split into chunks (1500 characters each)

For each question:

We check which chunk contains the most matching keywords

That chunk is returned as the answer

Chat history is saved inside st.session_state

✔ No Embeddings
✔ No Vector Databases
✔ No AI API Keys
✔ No Internet required after loading the website
🛠 Tech Stack
Component	Technology
Frontend	Streamlit
Backend Logic	Python
Web Scraping	LangChain WebBaseLoader
Text Processing	LangChain Text Splitter
State Management	Streamlit Session State
OS	Windows / Mac / Linux
📂 Project Folder Structure
ChatWithWebsite/
│
├── src/
│   ├── app.py
│   └── requirements.txt (optional)
│
├── .gitignore
├── .env  (ignored)
└── README.md

🚀 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/ishapadhal/ChatWithWebsite.git
cd ChatWithWebsite/src

2️⃣ Create Conda Environment
conda create -n chatweb python=3.10 -y
conda activate chatweb

3️⃣ Install Dependencies
pip install streamlit langchain-community langchain-text-splitters

4️⃣ Run the Application
streamlit run app.py

✔ Local URL
http://localhost:8501

💬 Usage

Enter any website URL in the sidebar

Wait for the content to load

Ask any question related to the website

Get instant offline answers

Chat history stays until page refresh

🔐 Security

No API keys needed

No data sent to cloud servers

Everything runs on your laptop

📘 Code Overview
Load Website Text
loader = WebBaseLoader(url)
docs = loader.load()

Split Into Chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
chunks = splitter.split_documents(docs)

Offline Question Answering
score = sum(word in text for word in question_words)

Streamlit Chat Interface
user_query = st.chat_input("Ask your question...")

🧩 Future Improvements

Add real embeddings using sentence-transformers

Add Gemini/OpenAI support (optional)

Use ChromaDB for vector search

Add website screenshot preview

Add caching for faster load time

Add theme switch (dark/light mode)

Mobile responsive UI
<img width="1909" height="871" alt="Screenshot 2025-12-11 204308" src="https://github.com/user-attachments/assets/b892fd1e-c91a-4244-a598-c3e153a9c34b" />


❤️ Contributions

Pull requests are welcome!
If you have ideas to improve this, feel free to open an issue.

⭐ If you like the project, give it a star!

It motivates me to improve it more.
