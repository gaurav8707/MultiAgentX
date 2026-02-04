/**
 * useWebSocket Hook - Optimized for Real-time Voice Interruption
 * This handles the bidirectional stream and forwards the 'interrupted' signal.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  ERROR: 'error',
};

export function useWebSocket(sessionId, onMessage, onError) {
  const [connectionState, setConnectionState] = useState(ConnectionState.DISCONNECTED);
  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 3;

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (!sessionId) {
      console.error('WebSocket Error: No session ID provided');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionState(ConnectionState.CONNECTING);

    try {
      const ws = new WebSocket(`${WS_BASE_URL}/ws/${sessionId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket Connected');
        setConnectionState(ConnectionState.CONNECTED);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // --- LOGGING INTERRUPTS FOR DEBUGGING ---
          if (data.type === 'interrupted') {
            console.warn('⚠️ INTERRUPT SIGNAL RECEIVED FROM BACKEND');
          }

          // Pass the data to the VoiceInterface component
          onMessage?.(data);
          
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionState(ConnectionState.ERROR);
        onError?.(error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setConnectionState(ConnectionState.DISCONNECTED);
        wsRef.current = null;

        // Auto-reconnect logic
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          const delay = 2000 * reconnectAttempts.current;
          console.log(`Attempting reconnect ${reconnectAttempts.current}/${maxReconnectAttempts} in ${delay}ms...`);
          setTimeout(connect, delay);
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setConnectionState(ConnectionState.ERROR);
      onError?.(err);
    }
  }, [sessionId, onMessage, onError]);

  /**
   * Manual Disconnect
   */
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    setConnectionState(ConnectionState.DISCONNECTED);
  }, []);

  /**
   * Send Binary Audio Data
   */
  const sendAudio = useCallback((audioData) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'audio',
        data: audioData,
      }));
    }
  }, []);

  /**
   * Send Text Data
   */
  const sendText = useCallback((text) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'text',
        data: text,
      }));
    }
  }, []);

  /**
   * Send Control Signals
   * (e.g., end_session or manual interrupt)
   */
  const sendControl = useCallback((action, payload = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'control',
        action,
        ...payload,
      }));
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connectionState,
    connect,
    disconnect,
    sendAudio,
    sendText,
    sendControl,
    isConnected: connectionState === ConnectionState.CONNECTED,
  };
}

export default useWebSocket;