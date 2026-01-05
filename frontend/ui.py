import streamlit as st
import requests
import sys
import os

#hardcoded url to skip config issues
BACKEND_URL = "http://localhost:8000/api/v1/rag"
GITHUB_LINK = "https://github.com"

# 🎨 Page Setup
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Enterprise RAG Chatbot")
st.caption("🚀 Powered by FastAPI, MongoDB, Gemini & Streamlit")
st.markdown("---")

# 🗂️ TABS
tab_chat, tab_run, tab_arch, tab_theory = st.tabs([
    "💬 Chatbot", 
    "🚀 Getting Started", 
    "⚙️ Architecture", 
    "🧠 The Math & Theory"
])

# ==========================================
# TAB 1: THE CHATBOT
# ==========================================
with tab_chat:
    # SIDEBAR
    with st.sidebar:
        st.header("📚 Knowledge Base")
        st.markdown("Teach the AI new facts here.")
        
        with st.form("ingest_form", clear_on_submit=True):
            source_name = st.text_input("Source Name")
            doc_text = st.text_area("Content", height=150)
            submitted = st.form_submit_button("Ingest Document", type="primary")
            
            if submitted:
                if not source_name or not doc_text:
                    st.warning("⚠️ Please fill in BOTH fields.")
                else:
                    with st.spinner("Ingesting..."):
                        try:
                            payload = {"text": doc_text, "source_name": source_name}
                            response = requests.post(f"{BACKEND_URL}/ingest", json=payload)
                            if response.status_code == 200:
                                st.success("✅ Document saved!")
                            else:
                                st.error(f"❌ Failed: {response.text}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")
        st.markdown("---")
        st.info("ℹ️ **Note:** This sidebar is for Admin/Ingestion only.")

    # MAIN CHAT
    st.header("🔍 Ask the Knowledge Base")
    
    with st.form("search_form"):
        query = st.text_input("Query", label_visibility="collapsed")
        search_submitted = st.form_submit_button("Search", type="primary", use_container_width=True)

    if search_submitted:
        if query:
            with st.spinner("Thinking... (Searching Vector DB + Gemini)"):
                try:
                    params = {"query": query}
                    response = requests.get(f"{BACKEND_URL}/search", params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.subheader("💡 Answer")
                        st.success(data["answer"])
                        
                        if data.get("sources"):
                            with st.expander("View Sources"):
                                for s in data["sources"]:
                                    st.markdown(f"- `{s}`")
                    else:
                        st.error(f"Backend Error ({response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: Is the backend running? \n\n{e}")
        else:
            st.warning("⚠️ Please enter a question.")


# ==========================================
# TAB 2: GETTING STARTED
# ==========================================
with tab_run:
    st.header("🚀 How to Run This Project")
    st.markdown("Welcome to the **FastRAG** documentation. Follow these steps to set up the environment.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Backend Setup")
        st.code("""
# Activate Virtual Environment
.\\.venv\\Scripts\\activate

# Start the API Server
python main.py
        """, language="bash")
        
    with col2:
        st.subheader("2. Frontend Setup")
        st.code("""
# In a new terminal
.\\.venv\\Scripts\\activate

# Start Streamlit UI
streamlit run frontend/ui.py
        """, language="bash")

    st.markdown("---")
    st.subheader("🔗 Source Code")
    st.markdown(f"Access the full source code and contribute on GitHub: [**Project Repository**]({GITHUB_LINK})")

# ==========================================
# TAB 3: ARCHITECTURE
# ==========================================
with tab_arch:
    st.header("⚙️ System Architecture")
    st.markdown("This project follows a **Microservices-ready** architecture using the **Retrieval-Augmented Generation (RAG)** pattern.")
    
    st.markdown("""
    ### 🔄 Data Flow
    1. **Ingestion:** User Input → HuggingFace (Vectorization) → MongoDB (Storage)
    2. **Retrieval:** User Query → HuggingFace (Vectorization) → MongoDB (Vector Search) → Gemini (Synthesis)
    """)
    
    st.markdown("---")
    
    st.subheader("🛠️ The Tech Stack")
    st.markdown("""
    | Component | Technology | Role |
    | :--- | :--- | :--- |
    | **Frontend** | `Streamlit` | Rapid UI Prototyping |
    | **Backend** | `FastAPI` | High-performance Async API |
    | **Database** | `MongoDB (Local)` | Local Vector & Document Storage |
    | **Embeddings** | `HuggingFace` | Text-to-Vector Conversion (`all-MiniLM-L6-v2`) |
    | **LLM** | `Google Gemini` | Answer Synthesis & Reasoning |
    """)

    st.info("💡 **Why this stack?** We chose **HuggingFace Inference API** over local models to keep the Docker container lightweight (~200MB vs 4GB). Using Local MongoDB ensures data privacy and zero cloud storage costs during development.")

# ==========================================
# TAB 4: THEORY
# ==========================================
with tab_theory:
    st.header("🧠 The Theory: Why RAG?")
    
    # 1. THE PROBLEM
    st.markdown("""
    Large Language Models (LLMs) like Gemini are powerful, but they have two major flaws in a business context:
    1.  **Knowledge Cutoff:** They don't know events that happened after their training.
    2.  **No Private Knowledge:** They don't know your company's internal PDFs, emails, or strategy documents.
    3.  **Hallucinations:** When they don't know an answer, they often confidently make one up.
    """)

    # 2. THE SOLUTION
    st.subheader("💡 The Solution: Retrieval-Augmented Generation (RAG)")
    st.info("""
    **RAG** is a technique that gives the AI a "Reference Book" (our MongoDB database). 
    Before answering, the AI **retrieves** the relevant internal pages and uses them to generate the answer.
    """)

    # 3. THE BUSINESS CASE
    st.markdown("### 🚀 Business Impact & ROI")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        st.markdown("#### 💰 Cost Efficiency")
        st.markdown("""
        **"It's too expensive to build a custom model."**
        
        Training a custom LLM costs millions in GPU compute. RAG allows us to leverage powerful, pre-trained models (like Gemini) for pennies, connecting them to our data without retraining.
        """)
        
    with col_b2:
        st.markdown("#### ⚡ Operational Speed")
        st.markdown("""
        **"Save weeks of screening time."**
        
        Employees spend up to 20% of their time just searching for information. This tool reduces weeks of manual document screening into seconds of instant retrieval.
        """)
        
    with col_b3:
        st.markdown("#### 🔐 Data Leverage")
        st.markdown("""
        **"Your Data + Their Brains."**
        
        We don't need to reinvent the wheel. We use the world's smartest AI reasoning capabilities and simply point it at our private, secure data.
        """)

    st.markdown("---")

    # 4. THE COMPARISON
    st.markdown("### 🆚 RAG vs. Standard LLM")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔴 Standard LLM (ChatGPT)**")
        st.caption("Query: 'What is the budget for Project Apollo?'")
        st.error("❌ Answer: 'I do not have access to internal financial documents.'")
    
    with col2:
        st.markdown("**🟢 RAG System (Our Chatbot)**")
        st.caption("Query: 'What is the budget for Project Apollo?'")
        st.success("✅ Answer: 'According to the Q4 Finance Report, the allocated budget for Project Apollo is $50,000.'")

    st.markdown("---")

    # 5. THE MATH
    st.header("🧮 The Math Under the Hood")
    
    st.subheader("1. What is a Vector?")
    st.markdown("""
    Computers cannot understand words; they only understand numbers. 
    We use an **Embedding Model** to transform text into a list of **384 numbers** (coordinates in a high-dimensional space).
    
    - **Concept:** Words with similar meanings are mathematically closer together.
    - **Example:** `Vector("Revenue")` is closer to `Vector("Profit")` than `Vector("Banana")`.
    """)
    
    st.subheader("2. Cosine Similarity Formula")
    st.markdown("To find relevant documents, we calculate the **angle** between the Query Vector ($A$) and Document Vector ($B$).")
    
    st.latex(r'''
    \text{similarity} = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}
    ''')
    
    st.subheader("3. Optimization Strategy")
    st.markdown("""
    1.  **Pre-Filter:** MongoDB ignores irrelevant sources immediately.
    2.  **Threshold Gate:** We drop results with similarity **< 0.5** to filter out noise.
    """)