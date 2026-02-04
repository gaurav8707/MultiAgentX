"""
Voice Agents API - FastAPI Backend with Real-time Bidirectional Streaming
OPTIMIZED FOR LOW-LATENCY INTERRUPTIONS
"""

import os
import json
import asyncio
import base64
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- RELIABLE ENV LOADING ---
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "❌ GOOGLE_API_KEY not found in environment."
    )

print("✅ Environment variables loaded. Google ADK ready.")

# Google ADK imports
from google.adk.agents import LiveRequestQueue
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from google.genai.types import Content, Part, Blob

# Local imports
from agents import get_agent, get_all_agent_metadata, get_agent_metadata, AGENT_METADATA
from utils import session_manager, SessionState

# Constants
APP_NAME = "voice_agents"

# Pydantic models for API
class SessionCreateRequest(BaseModel):
    agent_id: str
    metadata: Optional[dict] = None

class SessionResponse(BaseModel):
    session_id: str
    agent_id: str
    status: str

class AgentListResponse(BaseModel):
    agents: list

# Global session service
session_service = InMemorySessionService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    print("🚀 Starting Voice Agents API...")
    await session_manager.start_cleanup_task()
    yield
    print("🛑 Shutting down Voice Agents API...")
    await session_manager.stop_cleanup_task()

# Create FastAPI app
app = FastAPI(
    title="Voice Agents API",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def start_agent_session(user_id: str, agent_id: str, is_audio: bool = True):
    """Starts an ADK agent session with optimized interruption settings."""
    agent = get_agent(agent_id)
    
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=user_id,
    )
    
    modality = "AUDIO" if is_audio else "TEXT"
    
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=[modality],
        # --- OPTIMIZATION: Keep responses concise to make them easier to interrupt ---
        max_output_tokens=200, 
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Aoede"
                )
            )
        ) if is_audio else None,
        output_audio_transcription=types.AudioTranscriptionConfig() if is_audio else None,
        input_audio_transcription=types.AudioTranscriptionConfig() if is_audio else None,
    )
    
    live_request_queue = LiveRequestQueue()
    
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    return live_events, live_request_queue, runner

async def agent_to_client_messaging(websocket: WebSocket, live_events, session_id: str):
    """Forwards events from ADK agent to client with EMERGENCY BRAKE logic."""
    try:
        async for event in live_events:
            
            # --- HANDLE SERVER CONTENT (AUDIO & INTERRUPTS) ---
            if hasattr(event, 'server_content') and event.server_content:
                sc = event.server_content
                
                # 1. EMERGENCY BRAKE: Check for interruption signal
                if hasattr(sc, 'interrupted') and sc.interrupted:
                    print(f"🔴 BARGE-IN: User interrupted agent in session {session_id}")
                    # Tell frontend to flush its audio buffer INSTANTLY
                    await websocket.send_json({"type": "interrupted", "data": True})
                    # Set state back to active listening
                    await session_manager.update_session_state(session_id, SessionState.ACTIVE)
                    # Skip processing the rest of this event (kills stale audio)
                    continue 

                # 2. TURN COMPLETE: Agent finished talking
                if hasattr(sc, 'turn_complete') and sc.turn_complete:
                    await websocket.send_json({"type": "turn_complete", "data": True})
                    await session_manager.update_session_state(session_id, SessionState.ACTIVE)

                # 3. MODEL AUDIO/TEXT: Agent is generating output
                if hasattr(sc, 'model_turn') and sc.model_turn:
                    for part in sc.model_turn.parts or []:
                        # Text Output
                        if hasattr(part, 'text') and part.text:
                            await websocket.send_json({"type": "text", "data": part.text})
                        
                        # Audio Output
                        if hasattr(part, 'inline_data') and part.inline_data:
                            if 'audio' in (part.inline_data.mime_type or ''):
                                # Update state to SPEAKING
                                await session_manager.update_session_state(session_id, SessionState.SPEAKING)
                                audio_b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                                await websocket.send_json({"type": "audio", "data": audio_b64})
                
                # 4. TRANSCRIPTIONS
                if hasattr(sc, 'output_transcription') and sc.output_transcription:
                    await websocket.send_json({
                        "type": "output_transcript",
                        "data": sc.output_transcription.text,
                        "is_final": getattr(sc.output_transcription, 'finished', False)
                    })
                
                if hasattr(sc, 'input_transcription') and sc.input_transcription:
                    await websocket.send_json({
                        "type": "transcript",
                        "data": sc.input_transcription.text,
                        "is_final": getattr(sc.input_transcription, 'finished', False)
                    })

            # --- HANDLE ACTIONS (Evaluation Reports, etc) ---
            if hasattr(event, 'actions') and event.actions:
                if hasattr(event.actions, 'function_responses'):
                    for fr in event.actions.function_responses or []:
                        if 'evaluation_report' in fr.name:
                            await websocket.send_json({"type": "evaluation_report", "data": fr.response})
                            await session_manager.set_evaluation_report(session_id, fr.response)
                            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in agent-to-client: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})

async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue, session_id: str):
    """Forwards messages from client to ADK agent, respecting CRITICAL states."""
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            # Check current session state
            session = await session_manager.get_session(session_id)
            
            # GATE: Ignore microphone if agent is in a non-interruptible CRITICAL state
            if session and session.state == SessionState.CRITICAL and message_type == "audio":
                continue

            if message_type == "audio":
                audio_b64 = data.get("data")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    live_request_queue.send_realtime(
                        Blob(mime_type="audio/pcm;rate=16000", data=audio_bytes)
                    )
            
            elif message_type == "text":
                text = data.get("data", "")
                if text:
                    await session_manager.add_message(session_id, "user", text)
                    live_request_queue.send_content(
                        Content(role="user", parts=[Part(text=text)])
                    )
            
            elif message_type == "control":
                action = data.get("action")
                if action == "end_session":
                    # Lock the session so the final goodbye/report isn't interrupted
                    await session_manager.update_session_state(session_id, SessionState.CRITICAL)
                    end_msg = "[SYSTEM: User has requested to end the session. Please provide your evaluation report now.]"
                    live_request_queue.send_content(
                        Content(role="user", parts=[Part(text=end_msg)])
                    )
                    
    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in client-to-agent: {e}")

# --- REST API Endpoints ---
@app.get("/")
async def root():
    return {"status": "healthy", "service": "Voice Agents API"}

@app.get("/api/agents", response_model=AgentListResponse)
async def list_agents():
    return {"agents": get_all_agent_metadata()}

@app.get("/api/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    try:
        return get_agent_metadata(agent_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    if request.agent_id not in AGENT_METADATA:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
    session_id = await session_manager.create_session(agent_id=request.agent_id, metadata=request.metadata)
    return SessionResponse(session_id=session_id, agent_id=request.agent_id, status="created")

@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    session = await session_manager.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.session_id, "state": session.state.value}

@app.delete("/api/sessions/{session_id}")
async def end_session_endpoint(session_id: str):
    session = await session_manager.end_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "ended"}

# --- WebSocket endpoint ---
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, is_audio: str = "true"):
    session = await session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=4004)
        return
    
    use_audio = is_audio.lower() == "true"
    await websocket.accept()
    
    try:
        live_events, live_request_queue, runner = await start_agent_session(
            user_id=session_id,
            agent_id=session.agent_id,
            is_audio=use_audio
        )
        
        await session_manager.update_session_state(session_id, SessionState.ACTIVE)
        
        await websocket.send_json({
            "type": "status",
            "state": "connected",
            "agent_id": session.agent_id,
            "mode": "audio" if use_audio else "text"
        })
        
        agent_task = asyncio.create_task(agent_to_client_messaging(websocket, live_events, session_id))
        client_task = asyncio.create_task(client_to_agent_messaging(websocket, live_request_queue, session_id))
        
        done, pending = await asyncio.wait(
            [agent_task, client_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()
            try: await task
            except asyncio.CancelledError: pass
        
        live_request_queue.close()
        
    except WebSocketDisconnect:
        pass
    finally:
        await session_manager.update_session_state(session_id, SessionState.ENDED)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)