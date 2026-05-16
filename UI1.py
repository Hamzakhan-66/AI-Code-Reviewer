import os
import streamlit as st
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #0f172a, #111827);
    color: white;
}

.code-box, .review-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
}

.stButton button {
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-weight: bold;
}

.stButton button:hover {
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD ENV
# =========================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY not found in .env")
    st.stop()

# =========================
# LOG SYSTEM
# =========================

logs = []

def log(msg):
    logs.append(msg)

# =========================
# HELPERS
# =========================

def truncate_code(code, max_chars=8000):
    if len(code) > max_chars:
        return code[:max_chars]
    return code

def invoke(client, messages):
    return client.invoke(messages)

# =========================
# UI HEADER
# =========================

st.title("🤖 AI Code Reviewer")

st.markdown(
    "Upload a Python file and detect REAL runtime or logical bugs only."
)

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "📂 Upload Python File",
    type=["py"]
)

# =========================
# MAIN UI
# =========================

if uploaded_file:

    try:
        code = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.stop()

    code = truncate_code(code)

    col1, col2 = st.columns(2)

    # =========================
    # CODE PREVIEW
    # =========================

    with col1:
        st.subheader("💻 Code Preview")

        st.markdown('<div class="code-box">', unsafe_allow_html=True)

        st.code(code, language="python")

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # RUN REVIEW
    # =========================

    if st.button("🚀 Run Review"):

        try:

            log("Initializing AI model...")

            client = ChatGroq(
                api_key=api_key,
                model="llama-3.1-8b-instant",
                temperature=0
            )

            # =====================================
            # PHASE 1 → CHECK IF BUG EXISTS
            # =====================================

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a deterministic Python correctness checker. "
                        "You ONLY determine whether code fails during normal execution. "
                        "Do not suggest improvements, edge cases, validations, or best practices."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Analyze this Python code.

FIRST:
Answer ONLY:
- BUG_FOUND
OR
- NO_BUG

A bug exists ONLY if:
- code crashes
- code gives wrong output
- syntax/runtime/logical error exists

Ignore:
- edge cases
- unsupported file types
- best practices
- optimizations
- validations

CODE:
```python
{code}"""
}
]

            log("Checking if bug exists...")

            response = invoke(client, messages)

            first_result = response.content.strip()

            # =====================================
            # PHASE 2 → ONLY IF REAL BUG EXISTS
            # =====================================

            if "BUG_FOUND" in first_result:

                log("Bug detected. Generating fix...")

                second_messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a strict Python bug fixer. "
                            "Only explain REAL bugs and provide corrected code. "
                            "Do not suggest improvements or extra validations."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""
FIX THE REAL BUGS ONLY IN THIS CODE.
Do NOT add extra features, validations, or edge case handling.
Only fix what is broken.

CODE:
```python
{code}
```"""
                    }
                ]

                second_response = invoke(client, second_messages)
                final_content = second_response.content

            else:
                # NO BUG → return clean NO_BUG message
                final_content = "NO_BUG"

            # =========================
            # OUTPUT REVIEW
            # =========================

            with col2:
                st.subheader("🤖 Review")

                st.markdown('<div class="review-box">', unsafe_allow_html=True)

                if final_content == "NO_BUG":
                    st.success("✅ NO BUG FOUND — Code is correct")
                else:
                    st.markdown(final_content)

                st.markdown('</div>', unsafe_allow_html=True)

            st.success("✅ Done")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            log(f"Error: {e}")

    # =========================
    # LOGS SECTION
    # =========================

    st.subheader("📋 Logs")
    for l in logs:
        st.text(l)