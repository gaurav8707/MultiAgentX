# 🎙️ Voice Agents - Real-time Multi-Agent Voice System

A full-stack application for real-time voice conversations with AI agents using **Google ADK (Agent Development Kit)**, **FastAPI**, and **React**.

## 🌟 Features

- **8 Specialized AI Agents** for different learning scenarios
- **Real-time bidirectional audio streaming** with ultra-low latency
- **Live transcription** and text chat support
- **Detailed evaluation reports** with scores and feedback
- **Multi-language support** (English, Hindi, Hinglish)
- **Beautiful glassmorphism UI** with dark theme

## 🤖 Available Agents

| Agent | Description | Language |
|-------|-------------|----------|
| Debate Master | Engage in structured debates with real-time evaluation | English |
| Interview Architect | Build interview battle plans with STAR method coaching | English |
| Interview Helper | Practice behavioral interviews with confidence analysis | English |
| English Tutor | Improve spoken English through casual conversation | English |
| Parts of Speech Coach | Master grammar with Hinglish-style teaching | Hinglish |
| व्याकरण मित्र (Grammar Coach Hindi) | Learn English grammar in Hindi | Hindi |
| Past Tense Specialist | Master Past Indefinite vs Past Perfect | English |
| Past Tense Coach (Hindi) | Past tense mastery with Hindi explanations | Hindi |

## 🏗️ Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│                 │◄──────────────────►│                 │
│  React Frontend │     (Audio/Text)   │  FastAPI Server │
│                 │                    │                 │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                │ Google ADK
                                                │
                                       ┌────────▼────────┐
                                       │                 │
                                       │  Gemini 2.5     │
                                       │  Native Audio   │
                                       │                 │
                                       └─────────────────┘
```

## 📁 Project Structure

```
voice-agents-project/
├── backend/
│   ├── agents/                 # Agent definitions
│   │   ├── __init__.py         # Agent registry
│   │   ├── debate_master.py
│   │   ├── interview_architect.py
│   │   ├── interview_helper.py
│   │   ├── english_tutor.py
│   │   ├── parts_of_speech_coach.py
│   │   ├── parts_of_speech_coach_hindi.py
│   │   ├── past_tense_specialist.py
│   │   └── past_tense_specialist_hindi.py
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── audio.py            # Audio processing
│   │   └── session.py          # Session management
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── AgentCard.jsx
│   │   │   ├── VoiceInterface.jsx
│   │   │   └── EvaluationReport.jsx
│   │   ├── hooks/              # Custom hooks
│   │   │   ├── useWebSocket.js
│   │   │   └── useAudio.js
│   │   ├── utils/
│   │   │   └── api.js          # API utilities
│   │   ├── styles/
│   │   │   └── index.css       # Tailwind styles
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google API Key with Gemini access

### 1. Clone and Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Open in Browser

Navigate to `http://localhost:3000`

## ⚙️ Configuration

### Backend Environment Variables (.env)

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional
DEMO_AGENT_MODEL=gemini-2.5-flash-preview-native-audio-dialog
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📡 API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/agents` | List all agents |
| GET | `/api/agents/{id}` | Get agent details |
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{id}` | Get session info |
| DELETE | `/api/sessions/{id}` | End session |
| GET | `/api/stats` | Server statistics |

### WebSocket Protocol

Connect to `/ws/{session_id}` for real-time communication.

**Client → Server Messages:**
```json
{"type": "audio", "data": "<base64_pcm_audio>"}
{"type": "text", "data": "Hello!"}
{"type": "control", "action": "end_session"}
```

**Server → Client Messages:**
```json
{"type": "audio", "data": "<base64_pcm_audio>"}
{"type": "text", "data": "Agent response"}
{"type": "transcript", "data": "User said...", "is_final": true}
{"type": "evaluation_report", "data": {...}}
{"type": "status", "state": "connected"}
{"type": "error", "message": "Error details"}
```

## 🎨 UI Components

### AgentCard
Displays agent information with selection capability.

### VoiceInterface
Main voice interaction interface with:
- Real-time audio recording and playback
- Text chat input
- Audio level visualization
- Connection status indicator

### EvaluationReport
Modal displaying:
- Overall score with visual indicator
- Category-wise feedback
- Vocabulary improvements

## 🔧 Technical Details

### Audio Configuration

- **Input:** 16kHz, mono, 16-bit PCM
- **Output:** 24kHz, mono, 16-bit PCM
- **Chunk size:** 4096 samples (~256ms)

### Real-time Processing

1. Browser captures audio via `AudioWorklet`
2. Audio converted to base64 and sent via WebSocket
3. FastAPI receives and forwards to Google ADK
4. ADK processes with Gemini's native audio model
5. Response streamed back in real-time

## 🐛 Troubleshooting

### "Failed to load agents"
- Check if backend is running on port 8000
- Verify CORS settings allow frontend origin

### "Microphone access denied"
- Grant microphone permission in browser
- Ensure HTTPS in production (required for mic access)

### "WebSocket connection failed"
- Check if session was created successfully
- Verify WebSocket URL matches backend

### "No audio playback"
- Click anywhere on page first (browser autoplay policy)
- Check if speaker/headphones are connected

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

- [Google ADK](https://github.com/google/adk-python) - Agent Development Kit
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
