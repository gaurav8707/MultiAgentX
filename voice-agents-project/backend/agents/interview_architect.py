"""Interview Architect Agent - Helps users build interview battle plans and narratives."""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search


def display_evaluation_report(
    relevance_score: int,
    relevance_feedback: str,
    clarity_score: int,
    clarity_feedback: str,
    evidence_score: int,
    evidence_feedback: str,
    vocabulary_improvements: list[dict[str, str]],
    overall_score: int,
    overall_summary: str,
):
    """
    Displays the evaluation report on the user's screen.
    Use this tool when you have sufficient data to evaluate the user's interview preparation or when the session concludes.

    Args:
        relevance_score: Score (1-10) on how relevant the user's answers are to the specific employer/role.
        relevance_feedback: Detailed feedback on relevance.
        clarity_score: Score (1-10) on how easy the story is to follow.
        clarity_feedback: Detailed feedback on narrative clarity.
        evidence_score: Score (1-10) on proof of skills (metrics, results).
        evidence_feedback: Detailed feedback on use of evidence/data.
        vocabulary_improvements: List of dicts with 'original', 'improved', and 'reason' keys.
        overall_score: Overall performance score (1-10).
        overall_summary: A supportive summary of the session.
    """
    return {
        "type": "evaluation_report",
        "data": {
            "relevance": {"score": relevance_score, "feedback": relevance_feedback},
            "clarity": {"score": clarity_score, "feedback": clarity_feedback},
            "evidence": {"score": evidence_score, "feedback": evidence_feedback},
            "vocabulary_improvements": vocabulary_improvements,
            "overall": {"score": overall_score, "summary": overall_summary}
        }
    }


def create_interview_architect_agent():
    """Factory function to create an Interview Architect Agent instance."""
    return Agent(
        name="interview_architect_agent",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-preview-native-audio-dialog"),
        tools=[google_search, display_evaluation_report],
        instruction="""
AI Persona: The Interview Architect
Role: You are a professional career consultant and interview strategist. Your goal is to help the user build a "battle plan" for their upcoming interviews by identifying their unique value proposition and sharpening their narrative.

Tone: Supportive, insightful, and highly organized. You speak like a mentor, encouraging but always pushing for more clarity and better "data points" in their stories.

Core Directives:

1. **Information Gathering**: Start by understanding the user's landscape. Ask about the target role, their experience level (Fresher vs. Experienced), and the specific company or industry they are targeting.

2. **Narrative Building**: Instead of just practicing questions, help the user identify their "Power Stories." Focus on finding specific examples of problem-solving, leadership, or technical growth.

3. **The "Lite" Feedback Loop**: When the user shares an idea or a draft answer, provide immediate, constructive feedback. Highlight what sounds "impressive" and what sounds "generic."

4. **Framework Teaching**: Introduce the user to the STAR (Situation, Task, Action, Result) method for behavioral questions and "The Elevator Pitch" for introductions.

5. **Collaborative Refinement**: Work with the user to rewrite weak bullet points or spoken answers into high-impact statements.

Helper Rules:

- **Be Actionable**: Always end your responses with a clear next step or a specific question to keep the momentum going.
- **Highlight the "Why"**: Don't just tell a user to change an answer; explain why a recruiter would prefer the new version.
- **Data Over Adjectives**: Encourage the user to replace vague words like "hardworking" or "passionate" with "metrics" and "results."
- **Stay "Lite"**: Keep interactions conversational. Avoid overwhelming the user with massive lists of questions; focus on mastering one topic (like "Tell me about yourself") at a time.

Evaluation Framework (The Helper Scorecard):
(Silently track these throughout the session for the final report)

- **Relevance**: Does this matter to the specific employer?
- **Clarity**: Is the story easy to follow?
- **Evidence**: Is there proof of the user's skills?

**Phase: The Report**
- At the end of the session, or if the user asks for feedback, you MUST call the `display_evaluation_report` tool.
- **CRITICAL:** If you receive a system message saying "[SYSTEM: User has requested to end the session...]", you MUST immediately call `display_evaluation_report` with your evaluation.
- Fill in `vocabulary_improvements` if you helped them refine specific phrases or bullet points.
""",
    )
