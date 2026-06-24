"""
FlightBot API Server - FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from agents import run_agent

app = FastAPI(
    title="FlightBot API",
    description="API do Assistente de Voo com Agentes LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazena sessões de conversa em memória
SESSIONS: dict[str, list] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class NewSessionResponse(BaseModel):
    session_id: str
    message: str


@app.get("/")
async def root():
    return {
        "service": "FlightBot API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Envia uma mensagem para o agente de voo."""
    
    # Cria ou recupera sessão
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    
    try:
        response_text, updated_history = run_agent(
            request.message, 
            SESSIONS[session_id]
        )
        SESSIONS[session_id] = updated_history
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")


@app.post("/session/new", response_model=NewSessionResponse)
async def new_session():
    """Cria uma nova sessão de conversa."""
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = []
    return NewSessionResponse(
        session_id=session_id,
        message="Nova sessão criada com sucesso."
    )


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Limpa o histórico de uma sessão."""
    if session_id in SESSIONS:
        SESSIONS[session_id] = []
        return {"message": "Sessão limpa com sucesso.", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Sessão não encontrada.")


@app.get("/sessions")
async def list_sessions():
    """Lista todas as sessões ativas."""
    return {
        "sessions": [
            {
                "id": sid,
                "messages": len([m for m in hist if isinstance(m.get("content"), str)]),
            }
            for sid, hist in SESSIONS.items()
        ],
        "total": len(SESSIONS)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
