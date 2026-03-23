import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai

app = FastAPI(title="PulseTasks AI Service")

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    model = None

class TaskSuggestionRequest(BaseModel):
    raw_title: str
    raw_description: Optional[str] = ""
    context: Optional[dict] = {}

class TaskSuggestionResponse(BaseModel):
    rewritten_title: str
    checklist: List[str]
    suggested_priority: int
    suggested_due_date: Optional[str] = None
    confidence: float
    explanation: str

@app.post("/ai/suggest/task", response_model=TaskSuggestionResponse)
async def suggest_task(request: TaskSuggestionRequest):
    if not model:
        # Fallback to scaffold if no API key
        return {
            "rewritten_title": f"Refined: {request.raw_title}",
            "checklist": ["Break down task into steps", "Set milestones", "Review progress"],
            "suggested_priority": 3,
            "suggested_due_date": None,
            "confidence": 0.7,
            "explanation": "Scaffolded response (GOOGLE_API_KEY missing)."
        }

    prompt = f"""
    Act as an expert project manager. Optimize the following task for a professional workspace.
    
    Task Title: {request.raw_title}
    Task Description: {request.raw_description}
    
    Return a JSON object with:
    - rewritten_title: A more professional and clear title.
    - checklist: A list of 3-5 specific, actionable sub-tasks.
    - suggested_priority: An integer from 1 (Low) to 5 (Urgent).
    - explanation: A brief 1-sentence reason for these suggestions.
    - confidence: A float between 0 and 1.
    
    Format: Strict JSON only.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        # Extract JSON if Gemini wraps it in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        suggestion = json.loads(text)
        return {
            "rewritten_title": suggestion.get("rewritten_title", request.raw_title),
            "checklist": suggestion.get("checklist", []),
            "suggested_priority": suggestion.get("suggested_priority", 3),
            "suggested_due_date": None,
            "confidence": suggestion.get("confidence", 0.9),
            "explanation": suggestion.get("explanation", "Optimized by AI Agent.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/prioritize")
async def prioritize_tasks(tasks: List[dict]):
    # Pass-through for now
    return {"prioritized_tasks": tasks}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_active": model is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
