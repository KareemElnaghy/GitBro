import streamlit as st
from theme import load_theme

st.set_page_config(
    page_title="GitBro • Team",
    page_icon="👥",
    layout="wide"
)

load_theme()

st.markdown("## 🚀 Built by")
st.markdown(
    "<span class='gitbro-accent'>The team behind GitBro (5 members)</span>",
    unsafe_allow_html=True
)

with st.container():
    st.markdown('<div class="team-card">', unsafe_allow_html=True)

    members = [
        ("👩‍💻 Areeg Elkholy", "Data Science • Senior"),
        ("👩‍💻 Kareem Elnaghi", "Computer Engineering • Senior"),
        ("👨‍💻 Malak Samer", "Data Science • Senior"),
        ("👨‍💻 Maha Shakshuki", "Computer Science • Senior"),
        ("👩‍💻 Yahia Elbanhawy", "Data Science • Senior"),
    ]

    for name, role in members:
        st.markdown(f"<div class='team-name'>{name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='team-role'>{role}</div>", unsafe_allow_html=True)
        st.divider()

    st.markdown("</div>", unsafe_allow_html=True)
