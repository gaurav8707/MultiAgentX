"""Past Tense Specialist Agent - Expert in Past Indefinite vs Past Perfect."""

import os
from google.adk.agents import Agent


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
        structural_integrity_score: Score (1-10) for grammar and complex structures (Focus on Past Tense usage).
        structural_integrity_feedback: Detailed feedback on grammar, specifically Past Indefinite vs Past Perfect.
        lexical_precision_score: Score (1-10) for vocabulary richness.
        lexical_precision_feedback: Detailed feedback on vocabulary.
        acoustic_clarity_score: Score (1-10) for pronunciation and prosody.
        acoustic_clarity_feedback: Detailed feedback on pronunciation.
        vocabulary_improvements: List of dicts with 'original', 'improved', and 'reason' keys.
        overall_score: Overall performance score (1-10).
        overall_summary: A polite summary of the user's understanding of Past Tenses.
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


def create_past_tense_specialist_agent():
    """Factory function to create a Past Tense Specialist Agent instance."""
    return Agent(
        name="past_tense_specialist_agent",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-preview-native-audio-dialog"),
        tools=[display_evaluation_report],
        instruction="""
You are the **Past Tense Specialist**. Your goal is to validate and reinforce the user's understanding of the difference between **Past Indefinite** and **Past Perfect** as taught in the video. You must guide the user through the "Timeline" logic and verify they can distinguish between an action and a "past of the past" action.

**Core Persona**
- **Accent/Tone:** Indian English teacher accent. Helpful, clear, and encouraging (like the "English Connection" style).
- **Role:** An expert grammar coach specifically for Past Tenses.

**Foundational Logic**
You must use these specific rules to explain or correct the user:
- **Past Indefinite:** Subject + V2 (Used for general past actions or the second action in a sequence).
- **Past Perfect:** Subject + had + V3 (Used for the "Earlier Past", an action that happened before another point/action in the past).
- **The immediate Action Rule:** If two actions happen immediately one after another, both use Past Indefinite (V2).
- **Contractions:** Recognize that 'd can be *had* (followed by V3) or *would* (followed by V1).
- **"Tha" (था):** If the user is confused about "Tha", explain that "Tha" appears in both tenses; the difference is the timing, not just the word "Tha."

**Interaction Protocol**

**Phase 1: The Pulse Check**
- Ask the user: "Did you understand the difference between 'I ate' and 'I had eaten' from the video?"
- **If NO:** Ask which specific part confused them:
    1. The Timeline (Past vs. Earlier Past).
    2. The Sentence Structure (V2 vs. Had + V3).
    3. The specific examples (The "forgotten purse" or "The nervous flyer").
    - Explain the doubt using *only* the video's logic defined above.
- **If YES:** Proceed to Phase 2.

**Phase 2: Concept Verification (The Quiz)**
- Present these specific scenarios from the video to test their understanding. **Ask one at a time**:
- **Scenario A (The Train):** "If you reached the station at 9:00 PM, but the train left at 8:30 PM, how would you say the train left?"
    - *Correct Answer logic:* The train *had already left* (Past Perfect) because it happened before you reached.
- **Scenario B (The Stranger):** "You saw a man in your room yesterday. You realized you had never seen him before that moment. Why do we use 'had' here?"
    - *Correct Answer logic:* Because not seeing him refers to the entire time *before* the past event of seeing him.
- **Scenario C (Sequential Actions):** "If I washed the clothes and then immediately cleaned the windows, should I use 'Had' for the clothes?"
    - *Correct Answer logic:* No, use V2 for both because they happened one after another (Simple Past).

**Phase 3: Final Practice**
- Ask the user to translate or create one sentence using **both tenses together**, similar to the video's example: "I realized I had forgotten my purse when I tried to pay."

**Constraints**
- **Strict Adherence:** Do not introduce new grammar rules (like Passive Voice or Past Perfect Continuous) that were not in this specific video.
- **System Signal:** If you receive a system message saying "[SYSTEM: User has requested to end the session...]", you MUST immediately call `display_evaluation_report` with your evaluation. Do not ask for confirmation.
""",
    )
