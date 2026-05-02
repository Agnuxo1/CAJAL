"""CAJAL Paper Generator Streamlit App"""
import streamlit as st
from cajal_p2pclaw import CAJALChat

st.title("🧠 CAJAL Scientific Paper Generator")
st.markdown("Generate peer-reviewed quality papers locally")

with st.sidebar:
    st.header("Settings")
    topic = st.text_input("Research Topic", "P2P consensus mechanisms")
    style = st.selectbox("Paper Style", ["IEEE", "ACM", "Nature", "Science", "arXiv"])
    length = st.slider("Length (words)", 1000, 10000, 5000)

if st.button("Generate Paper"):
    with st.spinner("CAJAL is writing..."):
        chat = CAJALChat()
        
        # Generate sections
        abstract = chat.send(f"Write {length} word {style} abstract on {topic}")
        intro = chat.send(f"Write {length} word introduction")
        methods = chat.send("Describe methodology")
        results = chat.send("Present results")
        discussion = chat.send("Discuss findings")
        
        # Display
        st.header("Abstract")
        st.write(abstract)
        st.header("Introduction")
        st.write(intro)
        st.header("Methods")
        st.write(methods)
        st.header("Results")
        st.write(results)
        st.header("Discussion")
        st.write(discussion)
        
        # Export
        full_paper = f"# {topic}\\n\\n## Abstract\\n{abstract}\\n\\n## Introduction\\n{intro}\\n\\n## Methods\\n{methods}\\n\\n## Results\\n{results}\\n\\n## Discussion\\n{discussion}"
        st.download_button("Download Markdown", full_paper, f"{topic.replace(' ', '_')}.md")
