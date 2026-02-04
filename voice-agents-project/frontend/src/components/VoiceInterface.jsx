/**
 * VoiceInterface Component - Main voice interaction interface
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Mic, MicOff, Phone, PhoneOff, Send, Volume2, VolumeX,
  Loader2, AlertCircle, MessageSquare, X
} from 'lucide-react';
import { useWebSocket, ConnectionState, useAudio } from '../hooks';
import { createSession, endSession } from '../utils/api';
import EvaluationReport from './EvaluationReport';

export function VoiceInterface({ agent, onClose }) {
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [isMuted, setIsMuted] = useState(false);
  const [evaluationReport, setEvaluationReport] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((data) => {
    switch (data.type) {
      case 'text':
        setMessages(prev => [...prev, { role: 'assistant', content: data.data }]);
        break;
      
      case 'audio':
        if (!isMuted) {
          queueAudio(data.data);
        }
        break;
      
      case 'transcript':
        if (data.is_final) {
          setMessages(prev => [...prev, { role: 'user', content: data.data }]);
          setCurrentTranscript('');
        } else {
          setCurrentTranscript(data.data);
        }
        break;
      
      case 'evaluation_report':
        setEvaluationReport(data.data);
        break;
      
      case 'tool_call':
        console.log('Tool call:', data.name, data.result);
        break;
      
      case 'status':
        console.log('Status update:', data.state);
        break;
      
      case 'error':
        setError(data.message);
        break;
      
      default:
        console.log('Unknown message type:', data.type);
    }
  }, [isMuted]);

  // Handle WebSocket errors
  const handleError = useCallback((err) => {
    console.error('WebSocket error:', err);
    setError('Connection error. Please try reconnecting.');
  }, []);

  // Initialize hooks
  const {
    connectionState,
    connect,
    disconnect,
    sendAudio,
    sendText,
    sendControl,
    isConnected,
  } = useWebSocket(sessionId, handleMessage, handleError);

  const {
    isRecording,
    audioLevel,
    startRecording,
    stopRecording,
    queueAudio,
    clearAudioQueue,
    error: audioError,
  } = useAudio(sendAudio);

  // Start session
  const startSession = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const session = await createSession(agent.id);
      setSessionId(session.session_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Connect when session is created
  useEffect(() => {
    if (sessionId && connectionState === ConnectionState.DISCONNECTED) {
      connect();
    }
  }, [sessionId, connectionState, connect]);

  // End session
  const handleEndSession = async () => {
    // Send end session signal
    sendControl('end_session');
    
    // Wait a moment for the agent to respond
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Stop recording
    if (isRecording) {
      stopRecording();
    }
    
    // Clear audio queue
    clearAudioQueue();
    
    // Disconnect WebSocket
    disconnect();
    
    // End session on server
    if (sessionId) {
      try {
        await endSession(sessionId);
      } catch (err) {
        console.error('Error ending session:', err);
      }
    }
  };

  // Handle text input submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && isConnected) {
      sendText(inputText.trim());
      setMessages(prev => [...prev, { role: 'user', content: inputText.trim() }]);
      setInputText('');
      inputRef.current?.focus();
    }
  };

  // Toggle microphone
  const toggleMic = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // Toggle mute
  const toggleMute = () => {
    setIsMuted(prev => !prev);
    if (!isMuted) {
      clearAudioQueue();
    }
  };

  // Close the interface
  const handleClose = () => {
    handleEndSession();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-4xl h-[90vh] glass rounded-3xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-4">
            <span className="text-4xl">{agent.icon}</span>
            <div>
              <h2 className="font-display font-bold text-xl text-white">
                {agent.name}
              </h2>
              <div className="flex items-center gap-2">
                <span className={`
                  w-2 h-2 rounded-full
                  ${isConnected ? 'bg-emerald-400' : 'bg-red-400'}
                `} />
                <span className="text-sm text-gray-400">
                  {connectionState === ConnectionState.CONNECTING ? 'Connecting...' :
                   isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={handleClose}
            className="p-2 rounded-full hover:bg-white/10 transition-colors"
          >
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        {/* Main content area */}
        <div className="flex-1 flex flex-col min-h-0">
          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`
                    max-w-[80%] px-4 py-3
                    ${message.role === 'user' ? 'message-user' : 'message-agent'}
                  `}
                >
                  <p className="text-sm text-white whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>
              </div>
            ))}
            
            {/* Current transcript (while speaking) */}
            {currentTranscript && (
              <div className="flex justify-end">
                <div className="max-w-[80%] px-4 py-3 message-user opacity-60">
                  <p className="text-sm text-white italic">
                    {currentTranscript}...
                  </p>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Error display */}
          {(error || audioError) && (
            <div className="mx-6 mb-4 p-4 rounded-xl bg-red-500/20 border border-red-500/30 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-400">{error || audioError}</p>
            </div>
          )}

          {/* Controls area */}
          <div className="p-6 border-t border-white/10">
            {!sessionId ? (
              /* Start session button */
              <div className="flex justify-center">
                <button
                  onClick={startSession}
                  disabled={isLoading}
                  className="btn-primary flex items-center gap-3 px-8 py-4 text-lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Phone className="w-6 h-6" />
                      Start Session
                    </>
                  )}
                </button>
              </div>
            ) : (
              /* Active session controls */
              <div className="space-y-4">
                {/* Text input */}
                <form onSubmit={handleSubmit} className="flex gap-3">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Type a message..."
                    disabled={!isConnected}
                    className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 
                             text-white placeholder-gray-500 focus:outline-none focus:border-primary-500
                             disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={!isConnected || !inputText.trim()}
                    className="btn-primary px-4 disabled:opacity-50"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </form>

                {/* Voice controls */}
                <div className="flex items-center justify-center gap-4">
                  {/* Mute button */}
                  <button
                    onClick={toggleMute}
                    className={`
                      p-4 rounded-full transition-all
                      ${isMuted 
                        ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }
                    `}
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                    {isMuted ? <VolumeX className="w-6 h-6" /> : <Volume2 className="w-6 h-6" />}
                  </button>

                  {/* Mic button */}
                  <button
                    onClick={toggleMic}
                    disabled={!isConnected}
                    className={`
                      relative p-6 rounded-full transition-all disabled:opacity-50
                      ${isRecording 
                        ? 'bg-red-500 text-white animate-pulse' 
                        : 'bg-primary-500 text-white hover:bg-primary-600'
                      }
                    `}
                  >
                    {isRecording ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
                    
                    {/* Audio level indicator */}
                    {isRecording && (
                      <div 
                        className="absolute inset-0 rounded-full border-4 border-white/50"
                        style={{
                          transform: `scale(${1 + audioLevel * 0.3})`,
                          opacity: 0.5 + audioLevel * 0.5,
                          transition: 'transform 0.1s, opacity 0.1s'
                        }}
                      />
                    )}
                  </button>

                  {/* End session button */}
                  <button
                    onClick={handleEndSession}
                    className="p-4 rounded-full bg-red-500/20 text-red-400 
                             hover:bg-red-500/30 transition-all"
                    title="End Session"
                  >
                    <PhoneOff className="w-6 h-6" />
                  </button>
                </div>

                {/* Recording status */}
                {isRecording && (
                  <div className="flex justify-center">
                    <div className="flex items-center gap-2 text-red-400">
                      <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
                      <span className="text-sm">Recording...</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Evaluation Report Modal */}
        {evaluationReport && (
          <EvaluationReport 
            report={evaluationReport} 
            onClose={() => setEvaluationReport(null)} 
          />
        )}
      </div>
    </div>
  );
}

export default VoiceInterface;