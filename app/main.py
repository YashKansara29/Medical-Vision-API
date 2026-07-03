import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from sqlmodel import Session
from PIL import Image, UnidentifiedImageError

from app.database import create_db_and_tables, get_session
from app.models import ChatSession, ChatMessage
from app.ai_service import generate_clinical_summary

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Medical Vision API", lifespan=lifespan)

@app.post("/api/sessions", status_code=201)
def create_session(db: Session = Depends(get_session)):
    session = ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}

@app.post("/api/sessions/{session_id}/analyze")
async def analyze_scan(
    session_id: int, 
    file: UploadFile = File(...), 
    symptoms: str = Form("Not provided"), 
    db: Session = Depends(get_session)
):
    chat_session = db.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # Process image
    raw_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        visual_findings = f"Scan metadata - Format: {image.format}, Resolution: {image.size}, Mode: {image.mode}."
    except UnidentifiedImageError:
        raise HTTPException(status_code=422, detail="Invalid image.")

    db.add(ChatMessage(session_id=session_id, role="user", content=visual_findings))

    # Send raw bytes + symptoms to AI
    ai_response = generate_clinical_summary(raw_bytes, symptoms)

    # Log AI summary
    db.add(ChatMessage(session_id=session_id, role="ai", content=ai_response))
    db.commit()

    return {"session_id": session_id, "clinical_summary": ai_response}

@app.get("/api/sessions/{session_id}/history")
def get_session_history(session_id: int, db: Session = Depends(get_session)):
    chat_session = db.get(ChatSession, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"history": chat_session.messages}