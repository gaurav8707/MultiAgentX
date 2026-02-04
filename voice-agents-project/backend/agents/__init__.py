"""Agent Registry - Central hub for all available agents."""

from .debate_master import create_debate_master_agent
from .interview_architect import create_interview_architect_agent
from .interview_helper import create_interview_helper_agent
from .english_tutor import create_english_tutor_agent
from .parts_of_speech_coach import create_parts_of_speech_coach_agent
from .parts_of_speech_coach_hindi import create_parts_of_speech_coach_hindi_agent
from .past_tense_specialist import create_past_tense_specialist_agent
from .past_tense_specialist_hindi import create_past_tense_specialist_hindi_agent

# Agent metadata for frontend display
AGENT_METADATA = {
    "debate_master": {
        "id": "debate_master",
        "name": "Debate Master",
        "description": "Engage in structured debates on any topic with real-time performance evaluation.",
        "icon": "⚔️",
        "category": "Communication Skills",
        "features": ["Google Search", "Linguistic Analysis", "Real-time Feedback"],
        "language": "English"
    },
    "interview_architect": {
        "id": "interview_architect",
        "name": "Interview Architect",
        "description": "Build your interview battle plan with narrative building and STAR method coaching.",
        "icon": "📐",
        "category": "Career Preparation",
        "features": ["Google Search", "STAR Framework", "Power Stories"],
        "language": "English"
    },
    "interview_helper": {
        "id": "interview_helper",
        "name": "Interview Helper",
        "description": "Practice behavioral interviews with confidence analysis and grammar correction.",
        "icon": "🎯",
        "category": "Career Preparation",
        "features": ["Confidence Analysis", "STAR Method", "Grammar Check"],
        "language": "English"
    },
    "english_tutor": {
        "id": "english_tutor",
        "name": "English Tutor",
        "description": "Improve your spoken English through casual, friendly conversation practice.",
        "icon": "📚",
        "category": "Language Learning",
        "features": ["Casual Conversation", "Gentle Corrections", "Fluency Practice"],
        "language": "English"
    },
    "parts_of_speech_coach": {
        "id": "parts_of_speech_coach",
        "name": "Parts of Speech Coach",
        "description": "Master English grammar with fun Hinglish-style teaching and interactive quizzes.",
        "icon": "🎓",
        "category": "Grammar",
        "features": ["Hinglish Teaching", "Interactive Quizzes", "Video-based Learning"],
        "language": "Hinglish"
    },
    "parts_of_speech_coach_hindi": {
        "id": "parts_of_speech_coach_hindi",
        "name": "व्याकरण मित्र (Grammar Coach Hindi)",
        "description": "हिंदी में इंग्लिश ग्रामर सीखें - Learn English grammar in Hindi with your Vyakaran Mitra.",
        "icon": "🇮🇳",
        "category": "Grammar",
        "features": ["Hindi Explanations", "Interactive Learning", "8 Parts of Speech"],
        "language": "Hindi/Hinglish"
    },
    "past_tense_specialist": {
        "id": "past_tense_specialist",
        "name": "Past Tense Specialist",
        "description": "Master Past Indefinite vs Past Perfect with timeline logic and practical scenarios.",
        "icon": "⏰",
        "category": "Grammar",
        "features": ["Timeline Logic", "Scenario Practice", "V2 vs Had+V3"],
        "language": "English"
    },
    "past_tense_specialist_hindi": {
        "id": "past_tense_specialist_hindi",
        "name": "Past Tense Coach (Hindi)",
        "description": "पास्ट टेंस में महारत हासिल करें - Master past tenses with Hindi explanations.",
        "icon": "🕐",
        "category": "Grammar",
        "features": ["Hindi Teaching", "Timeline Logic", "Quiz-based Learning"],
        "language": "Hindi/Hinglish"
    }
}

# Agent factory mapping
AGENT_FACTORIES = {
    "debate_master": create_debate_master_agent,
    "interview_architect": create_interview_architect_agent,
    "interview_helper": create_interview_helper_agent,
    "english_tutor": create_english_tutor_agent,
    "parts_of_speech_coach": create_parts_of_speech_coach_agent,
    "parts_of_speech_coach_hindi": create_parts_of_speech_coach_hindi_agent,
    "past_tense_specialist": create_past_tense_specialist_agent,
    "past_tense_specialist_hindi": create_past_tense_specialist_hindi_agent
}


def get_agent(agent_id: str):
    """
    Get an agent instance by ID.
    
    Args:
        agent_id: The unique identifier for the agent.
        
    Returns:
        An Agent instance.
        
    Raises:
        ValueError: If agent_id is not found.
    """
    if agent_id not in AGENT_FACTORIES:
        raise ValueError(f"Agent '{agent_id}' not found. Available agents: {list(AGENT_FACTORIES.keys())}")
    
    return AGENT_FACTORIES[agent_id]()


def get_all_agent_metadata():
    """Get metadata for all available agents."""
    return list(AGENT_METADATA.values())


def get_agent_metadata(agent_id: str):
    """Get metadata for a specific agent."""
    if agent_id not in AGENT_METADATA:
        raise ValueError(f"Agent '{agent_id}' not found.")
    return AGENT_METADATA[agent_id]


__all__ = [
    "get_agent",
    "get_all_agent_metadata",
    "get_agent_metadata",
    "AGENT_METADATA",
    "AGENT_FACTORIES"
]
