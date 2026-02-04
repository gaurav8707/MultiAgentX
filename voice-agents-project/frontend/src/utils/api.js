/**
 * API Utilities - Functions for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Fetch all available agents
 */
export async function fetchAgents() {
  const response = await fetch(`${API_BASE_URL}/api/agents`);
  if (!response.ok) {
    throw new Error('Failed to fetch agents');
  }
  const data = await response.json();
  return data.agents;
}

/**
 * Fetch a specific agent's information
 */
export async function fetchAgent(agentId) {
  const response = await fetch(`${API_BASE_URL}/api/agents/${agentId}`);
  if (!response.ok) {
    throw new Error(`Agent ${agentId} not found`);
  }
  return response.json();
}

/**
 * Create a new session
 */
export async function createSession(agentId, metadata = {}) {
  const response = await fetch(`${API_BASE_URL}/api/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_id: agentId,
      metadata,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create session');
  }
  
  return response.json();
}

/**
 * Get session information
 */
export async function fetchSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);
  if (!response.ok) {
    throw new Error('Session not found');
  }
  return response.json();
}

/**
 * End a session
 */
export async function endSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error('Failed to end session');
  }
  
  return response.json();
}

/**
 * Get server statistics
 */
export async function fetchStats() {
  const response = await fetch(`${API_BASE_URL}/api/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }
  return response.json();
}
