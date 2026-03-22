# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from reviewer import CodeReviewer, ReviewRequest


app = FastAPI(
    title="Big-O Code Reviewer",
    version="1.0.0",
)

reviewer = CodeReviewer(model="gemini-3-flash-preview")



@app.get("/health")
def health():
    return {"status": "ok", "model": reviewer.model}


@app.post("/review")
def review(request: ReviewRequest):
    try:
        return reviewer.review(request.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review/stream")
def review_stream(request: ReviewRequest):
    def generate():
        try:
            yield from reviewer.review_stream(request.code)
        except Exception as e:
            yield f"Error: {str(e)}"
    
    return StreamingResponse(generate(), media_type="text/plain")

