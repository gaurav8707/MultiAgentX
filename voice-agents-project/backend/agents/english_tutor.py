"""English Tutor Agent - Casual conversation coach for spoken English improvement."""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search


def display_evaluation_report(
    linguistic_agility_score: int,
    linguistic_agility_feedback: str,
    structural_integrity_score: int,
    structural_integrity_feedback: str,
    lexical_precision_score: int,
    lexical_precision_feedback: str,
    acoustic_clarity_score: int,
    acoustic_clarity_feedback: str,
    vocabulary_improvements: list[dict[str, str]],
    overall_score: int,
    overall_summary: str,
):
    """
    Displays the evaluation report on the user's screen.
    Use this tool when you have sufficient data to evaluate the user's performance or when the session concludes.

    Args:
        linguistic_agility_score: Score (1-10) for speech-to-pause ratio and fluency.
        linguistic_agility_feedback: Detailed feedback on fluency.
        structural_integrity_score: Score (1-10) for grammar and complex structures.
        structural_integrity_feedback: Detailed feedback on grammar.
        lexical_precision_score: Score (1-10) for vocabulary richness.
        lexical_precision_feedback: Detailed feedback on vocabulary.
        acoustic_clarity_score: Score (1-10) for pronunciation and prosody.
        acoustic_clarity_feedback: Detailed feedback on pronunciation.
        vocabulary_improvements: List of dicts with 'original', 'improved', and 'reason' keys.
        overall_score: Overall performance score (1-10).
        overall_summary: A friendly summary of the session.
    """
    return {
        "type": "evaluation_report",
        "data": {
            "linguistic_agility": {"score": linguistic_agility_score, "feedback": linguistic_agility_feedback},
            "structural_integrity": {"score": structural_integrity_score, "feedback": structural_integrity_feedback},
            "lexical_precision": {"score": lexical_precision_score, "feedback": lexical_precision_feedback},
            "acoustic_clarity": {"score": acoustic_clarity_score, "feedback": acoustic_clarity_feedback},
            "vocabulary_improvements": vocabulary_improvements,
            "overall": {"score": overall_score, "summary": overall_summary}
        }
    }


def create_english_tutor_agent():
    """Factory function to create an English Tutor Agent instance."""
    return Agent(
        name="english_tutor_agent",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-preview-native-audio-dialog"),
        tools=[google_search, display_evaluation_report],
        instruction="""
You are a friendly and encouraging English Tutor. Your goal is to help the user improve their spoken English through casual conversation.

**Phase 1: Setup**
1. Warmly greet the user and ask how their day is going or what they'd like to talk about.
2. Keep the tone light, supportive, and conversational.

**Phase 2: Conversation & Coaching**
- Engage in a natural dialogue.
- If the user makes a grammar mistake or uses awkward phrasing, gently correct them in the flow of conversation or gently suggest a better way to say it.
- Do not be overly pedantic; prioritize communication flow.
- Encourage them to elaborate on their thoughts to practice fluency.

**Phase 3: Continuous Evaluation (Hidden)**
- Silently track their performance on:
    1. **Linguistic Agility:** Fluency and flow.
    2. **Structural Integrity:** Grammar correctness.
    3. **Lexical Precision:** Vocabulary choice.
    4. **Acoustic Clarity:** Pronunciation.
- Specifically note down words or phrases they used that could be improved ("original") and your suggested alternative ("improved") with a reason ("reason").

**Phase 4: The Report**
- At the end of the session, or if the user asks for feedback, you MUST call the `display_evaluation_report` tool.
- **CRITICAL:** If you receive a system message saying "[SYSTEM: User has requested to end the session...]", you MUST immediately call `display_evaluation_report` with your evaluation.
- Fill in the `vocabulary_improvements` list with specific examples collected during the chat.
""",
    )
