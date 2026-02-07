import streamlit as st

def load_theme():
    st.markdown("""
    <style>

    /* -----------------------------
       GLOBAL
    ------------------------------*/
    .stApp {
        background: linear-gradient(135deg, #0b0d10, #0f172a);
        font-family: 'Inter', sans-serif;
    }

    /* Global text */
    .stApp, div, p, label, h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }

    /* -----------------------------
       INPUTS
    ------------------------------*/
    input, textarea {
        background-color: #020617 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.9) !important;
        font-weight: 500;
    }

    input::placeholder,
    textarea::placeholder {
        color: #c7d2fe !important;
        opacity: 1;
    }

    /* -----------------------------
       CARDS
    ------------------------------*/
    .gitbro-card,
    .team-card {
        background: linear-gradient(145deg, #111827, #020617);
        padding: 1.8rem;
        border-radius: 18px;
        border: 1px solid rgba(59, 130, 246, 0.4);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.65);
        margin-bottom: 1.8rem;
    }

    /* -----------------------------
       BUTTONS
    ------------------------------*/
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #6366f1);
        color: #ffffff !important;
        font-weight: 700;
        border-radius: 14px;
        padding: 0.7rem 1.6rem;
        border: none;
    }

    /* -----------------------------
       ACCENT
    ------------------------------*/
    .gitbro-accent {
        color: #3b82f6 !important;
        font-weight: 600;
    }

    /* -----------------------------
       TEAM
    ------------------------------*/
    .team-name {
        font-size: 1.15rem;
        font-weight: 700;
    }

    .team-role {
        font-size: 0.95rem;
        color: #c7d2fe;
    }

    </style>
    """, unsafe_allow_html=True)
