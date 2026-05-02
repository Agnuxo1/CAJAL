"""Extended CAJAL FastAPI with paper generation endpoints"""
from fastapi import FastAPI
from pydantic import BaseModel
from cajal_p2pclaw import CAJALChat

app = FastAPI(title="CAJAL Scientific API")

class PaperRequest(BaseModel):
    topic: str
    style: str = "IEEE"
    sections: list = ["abstract", "introduction", "conclusion"]
    max_words: int = 5000

@app.post("/generate/paper")
async def generate_paper(request: PaperRequest):
    chat = CAJALChat()
    paper = {}
    
    for section in request.sections:
        paper[section] = chat.send(
            f"Write {request.max_words // len(request.sections)} word "
            f"{request.style} {section} for paper on: {request.topic}"
        )
    
    return {
        "title": chat.send(f"Generate title for: {request.topic}"),
        "sections": paper,
        "word_count": sum(len(v.split()) for v in paper.values()),
        "style": request.style
    }

@app.post("/generate/review")
async def generate_review(topics: list[str]):
    chat = CAJALChat()
    review = chat.send(
        f"Write a comprehensive literature review covering: {', '.join(topics)}"
    )
    return {"review": review, "topics": topics}
