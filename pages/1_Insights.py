import streamlit as st
from theme import load_theme

st.set_page_config(
    page_title="GitBro • Insights",
    page_icon="📊",
    layout="wide"
)

load_theme()

# Remove Streamlit default white markdown background
st.markdown("""
<style>
div[data-testid="stMarkdownContainer"],
section[data-testid="stMarkdown"] {
    background: transparent !important;
}
.agent-divider {
    border: none;
    height: 1px;
    background: linear-gradient(
        to right,
        transparent,
        rgba(59,130,246,0.35),
        transparent
    );
    margin: 1.2rem 0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="gitbro-card">
<h1>📊 GitBro Insights</h1>
<p class="gitbro-accent">
AI-Powered Codebase Analyzer & Onboarding System
</p>
</div>
""", unsafe_allow_html=True)

# Description
st.markdown("""
<div class="gitbro-card">
<h2>🏗️ Description</h2>
<p>
Modern software teams struggle to onboard new developers into large, complex codebases.
Documentation is often outdated, architectural decisions are unclear, and understanding
<strong>why</strong> the code works the way it does can take weeks.
</p>
<p>
<strong>GitBro</strong> uses a <strong>multi-agent AI architecture</strong> that reasons over
GitHub repositories. Specialized agents collaborate to analyze structure, context,
and intent — accelerating onboarding and knowledge transfer.
</p>
</div>
""", unsafe_allow_html=True)

# Agent Architecture (NO WHITE BOXES, TEAM STYLE)
st.markdown("""
<div class="gitbro-card">
<h2>🤖 Agent Architecture</h2>

<p><strong>👑 Orchestrator Agent</strong></p>
<p>
Acts as the brain of the system. It decomposes user requests into tasks,
assigns them to specialized agents, and ensures consistency and correctness.
</p>

<div class="agent-divider"></div>

<p><strong>🧭 Navigator Agent</strong></p>
<p>
Explores repository structure to identify key directories, files,
modules, and dependencies.
</p>

<div class="agent-divider"></div>

<p><strong>🧠 Context Agent</strong></p>
<p>
Analyzes commit history, configuration, and documentation to explain
why the system evolved the way it did.
</p>

<div class="agent-divider"></div>

<p><strong>📐 Visualizer Agent</strong></p>
<p>
Generates architecture diagrams and dependency graphs to help engineers
understand the system at a glance.
</p>

<div class="agent-divider"></div>

<p><strong>📘 Explainer Agent</strong></p>
<p>
Answers how and why questions with step-by-step explanations tailored
to the user’s experience level.
</p>

</div>
""", unsafe_allow_html=True)
