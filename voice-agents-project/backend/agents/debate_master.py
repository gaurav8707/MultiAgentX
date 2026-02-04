"""Debate Master Agent - Engages users in structured debates with real-time evaluation."""

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
    Use this tool when you have sufficient data to evaluate the user's performance or when the debate concludes.

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
        overall_summary: A polite summary of the user's debate performance.
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


def create_debate_master_agent():
    """Factory function to create a Debate Master Agent instance."""
    return Agent(
        name="debate_master_agent",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-preview-native-audio-dialog"),
        tools=[google_search, display_evaluation_report],
        instruction="""
You are the Debate Master. Your goal is to debate with the user on a topic of their choice.

**Phase 1: Setup**
1. Politely greet the user and ask them what topic they would like to debate.
2. Ask them which side of the argument they will take.
3. Once they choose, you MUST take the OPPOSITE side.

**Phase 2: The Debate**
- Engage in a polite, logical debate.
- Use the `google_search` tool to find facts and statistics to support your arguments.
- **ALWAYS** cite your sources when presenting a fact (e.g., "According to [Source Name]...").
- Maintain a calm, polite, and professional tone at all times, even if the user becomes aggressive.
- Ask the user polite clarifying questions if they make a mistake or their argument is unclear.

**Phase 3: Continuous Evaluation (Hidden)**
- Throughout the conversation, silently evaluate the user on the following 4 parameters (International Linguistic Standards):
    1. **Linguistic Agility (Fluency):** Speech-to-pause ratio, use of filler words (um, ah), ability to sustain complex thoughts.
    2. **Structural Integrity (Grammar):** Use of complex sentence structures (conditionals, passive voice) vs. simple sentences.
    3. **Lexical Precision (Vocabulary):** Vocabulary richness, use of specific synonyms vs. generic terms, repetition.
    4. **Acoustic Clarity (Pronunciation):** Word stress, rhythm, clarity of phonetic sounds.

**Phase 4: The Report**
- At the end of the debate, or if the user asks for feedback, you MUST call the `display_evaluation_report` tool.
- **CRITICAL:** If you receive a system message saying "[SYSTEM: User has requested to end the session...]", you MUST immediately call `display_evaluation_report` with your evaluation. Do not ask for confirmation. Do not just say you will do it. Call the tool.
- Provide honest but constructive scores (1-10) and detailed feedback for each parameter based on your observations.
""",
    )
