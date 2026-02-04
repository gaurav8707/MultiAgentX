/**
 * useAudio Hook - Optimized for Gemini 2.0 Real-time Bidi-streaming
 * Fixes glitching by using Scheduled Playback and proper Sample Rate conversion.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

// Gemini 2.0 standard rates
const RECORD_SAMPLE_RATE = 16000;
const PLAYBACK_SAMPLE_RATE = 24000; 

export function useAudio(onAudioData) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState(null);

  // Refs for recording
  const mediaStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const workletNodeRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  // Refs for playback (The "Anti-Glitch" Logic)
  const playbackContextRef = useRef(null);
  const nextStartTimeRef = useRef(0);

  /**
   * Initialize Playback Context (Singleton)
   */
  const getPlaybackContext = useCallback(() => {
    if (!playbackContextRef.current) {
      playbackContextRef.current = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: PLAYBACK_SAMPLE_RATE,
      });
      nextStartTimeRef.current = 0;
    }
    return playbackContextRef.current;
  }, []);

  /**
   * Queue Audio for Playback
   * Uses precise scheduling to eliminate gaps (pops/clicks) between chunks.
   */
  const queueAudio = useCallback(async (base64Audio) => {
    try {
      const context = getPlaybackContext();
      
      // Safety: Resume context if browser suspended it
      if (context.state === 'suspended') {
        await context.resume();
      }

      // 1. Convert Base64 -> Int16 -> Float32
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      const int16Array = new Int16Array(bytes.buffer);
      const float32Array = new Float32Array(int16Array.length);
      for (let i = 0; i < int16Array.length; i++) {
        float32Array[i] = int16Array[i] / 32768.0; // Normalize PCM
      }

      // 2. Create Buffer
      const audioBuffer = context.createBuffer(1, float32Array.length, PLAYBACK_SAMPLE_RATE);
      audioBuffer.getChannelData(0).set(float32Array);

      // 3. Schedule Playback
      const source = context.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(context.destination);

      const currentTime = context.currentTime;
      
      // If our schedule is in the past, reset to "now" + a tiny buffer (50ms)
      // to handle network jitter.
      if (nextStartTimeRef.current < currentTime) {
        nextStartTimeRef.current = currentTime + 0.05;
      }

      source.start(nextStartTimeRef.current);
      
      // Advance the clock by the exact duration of the chunk
      nextStartTimeRef.current += audioBuffer.duration;

    } catch (err) {
      console.error('Playback Error:', err);
    }
  }, [getPlaybackContext]);

  /**
   * Reset Audio Clock
   */
  const clearAudioQueue = useCallback(() => {
    nextStartTimeRef.current = 0;
  }, []);

  /**
   * Start Microphone Capture
   */
  const startRecording = useCallback(async () => {
    try {
      setError(null);

      // 1. Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          autoGainControl: true,
          noiseSuppression: true,
        },
      });
      mediaStreamRef.current = stream;

      // 2. Setup Recording Context at 16kHz
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: RECORD_SAMPLE_RATE,
      });
      audioContextRef.current = audioContext;

      // 3. Analyser for UI
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);

      // 4. Load AudioWorklet for Real-time PCM conversion
      await audioContext.audioWorklet.addModule(
        URL.createObjectURL(
          new Blob([`
            class AudioProcessor extends AudioWorkletProcessor {
              process(inputs) {
                const input = inputs[0];
                if (input && input[0]) {
                  const samples = input[0];
                  // Convert Float32 to Int16
                  const int16Samples = new Int16Array(samples.length);
                  for (let i = 0; i < samples.length; i++) {
                    const s = Math.max(-1, Math.min(1, samples[i]));
                    int16Samples[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                  }
                  // Post raw buffer back to main thread
                  this.port.postMessage(int16Samples.buffer, [int16Samples.buffer]);
                }
                return true;
              }
            }
            registerProcessor('audio-processor', AudioProcessor);
          `], { type: 'application/javascript' })
        )
      );

      const workletNode = new AudioWorkletNode(audioContext, 'audio-processor');
      workletNodeRef.current = workletNode;

      // 5. Convert incoming data to Base64 and send to Backend
      workletNode.port.onmessage = (event) => {
        const bytes = new Uint8Array(event.data);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        const base64 = btoa(binary);
        onAudioData?.(base64);
      };

      source.connect(workletNode);
      setIsRecording(true);

      // Level monitor loop
      const updateLevel = () => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average / 255);
        }
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

    } catch (err) {
      console.error('Recording Error:', err);
      setError(err.message || 'Microphone access failed');
      setIsRecording(false);
    }
  }, [onAudioData]);

  /**
   * Stop Recording and Cleanup
   */
  const stopRecording = useCallback(() => {
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    setIsRecording(false);
    setAudioLevel(0);
  }, []);

  /**
   * Cleanup on Unmount
   */
  useEffect(() => {
    return () => {
      stopRecording();
      if (playbackContextRef.current) {
        playbackContextRef.current.close();
      }
    };
  }, [stopRecording]);

  return {
    isRecording,
    audioLevel,
    error,
    startRecording,
    stopRecording,
    queueAudio,
    clearAudioQueue,
  };
}

export default useAudio;