import streamlit as st
from theme import load_theme

st.set_page_config(
    page_title="GitBro",
    page_icon="🤖",
    layout="wide"
)

load_theme()

# =========================================================
# Header
# =========================================================
st.markdown("""
<div class="gitbro-card">
    <h1>🤖 GitBro</h1>
    <p class="gitbro-accent">
        Agentic AI for Codebase Understanding & Engineer Onboarding
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# Repository Input
# =========================================================
st.markdown('<div class="gitbro-card">', unsafe_allow_html=True)
st.subheader("GitHub Repository")

repo_url = st.text_input(
    "Repository URL",
    placeholder="https://github.com/org/repo"
)

if st.button("Analyze Repository"):
    if not repo_url:
        st.warning("Please enter a GitHub repository URL.")
    else:
        with st.spinner("GitBro is analyzing the repository..."):
            st.session_state["architecture_summary"] = """
            This repository follows a modular layered architecture.
            The API layer handles routing and validation, the service
            layer encapsulates business logic, and the data layer
            manages persistence.
            """
        st.success("Repository analyzed successfully.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# Architecture Summary + Q&A
# =========================================================
if "architecture_summary" in st.session_state:
    st.markdown('<div class="gitbro-card">', unsafe_allow_html=True)
    st.subheader("Architecture Overview")
    st.markdown(st.session_state["architecture_summary"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="gitbro-card">', unsafe_allow_html=True)
    st.subheader("Ask GitBro")

    question = st.text_input(
        "How / Why Question",
        placeholder="Why was this service split from the monolith?"
    )

    if st.button("Ask GitBro"):
        if question:
            st.markdown("This service was separated to reduce coupling and improve scalability.")
        else:
            st.warning("Please enter a question.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# Footer
# =========================================================
st.markdown(
    "<div style='text-align:center; font-size:0.85rem;'>"
    "GitBro • McKinsey × QuantumBlack AI Inspired"
    "</div>",
    unsafe_allow_html=True
)
