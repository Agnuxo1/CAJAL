"""CAJAL Gradio Demo for HuggingFace Spaces"""
import gradio as gr
from cajal_p2pclaw import CAJALChat

def generate_paper(topic, style, sections):
    chat = CAJALChat()
    paper = {}
    
    if "Abstract" in sections:
        paper["Abstract"] = chat.send(f"Write {style} abstract on {topic}")
    if "Introduction" in sections:
        paper["Introduction"] = chat.send(f"Write {style} introduction on {topic}")
    if "Methods" in sections:
        paper["Methods"] = chat.send("Describe methodology")
    if "Results" in sections:
        paper["Results"] = chat.send("Present results")
    if "Discussion" in sections:
        paper["Discussion"] = chat.send("Discuss implications")
    
    output = ""
    for section, content in paper.items():
        output += f"## {section}\\n\\n{content}\\n\\n"
    
    return output

demo = gr.Interface(
    fn=generate_paper,
    inputs=[
        gr.Textbox(label="Research Topic", placeholder="e.g., Byzantine consensus in P2P"),
        gr.Dropdown(["IEEE", "ACM", "Nature", "Science", "arXiv"], label="Style"),
        gr.Checkboxgroup(["Abstract", "Introduction", "Methods", "Results", "Discussion"], 
                        label="Sections", value=["Abstract", "Introduction"])
    ],
    outputs=gr.Markdown(label="Generated Paper"),
    title="🧠 CAJAL-4B Scientific Paper Generator",
    description="Local, open-source, peer-reviewed quality papers"
)

if __name__ == "__main__":
    demo.launch()
