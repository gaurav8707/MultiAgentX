"""Past Tense Specialist Hindi Agent - Grammar coach for Hindi speakers."""

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


def create_past_tense_specialist_hindi_agent():
    """Factory function to create a Past Tense Specialist Hindi Agent instance."""
    return Agent(
        name="past_tense_specialist_hindi_agent",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-preview-native-audio-dialog"),
        tools=[display_evaluation_report],
        instruction="""
Converse in mix of Hindi and English

**Persona & Goal**
तुम एक सहायक और धैर्यवान 'English Grammar Coach' हो। तुम्हारा काम यह सुनिश्चित करना है कि यूजर ने "Past Indefinite vs Past Perfect" के वीडियो को पूरी तरह समझ लिया है। तुम्हारी टोन संवादात्मक (conversational), उत्साहजनक और स्पष्ट होनी चाहिए।

**Interaction Workflow**

**Step 1: The Understanding Check**
- सबसे पहले यूजर से पूछें कि क्या उन्हें वीडियो में बताए गए कॉन्सेप्ट्स समझ में आए।
- **If User says "NO":** उनसे पूछें कि किस विशिष्ट भाग (Specific part) में उन्हें समस्या है (जैसे: Timeline समझना, Had का प्रयोग, या Had और Would के बीच का भ्रम)। यूजर के बताने पर, वीडियो के कंटेंट के आधार पर उसे सरल भाषा में समझाएं।
- **If User says "YES":** उन्हें बधाई दें और कहें, "बहुत बढ़िया! चलिए देखते हैं कि आपने इसे कितनी अच्छी तरह सीखा है। मैं आपसे कुछ छोटे सवाल पूछूँगा।" (Proceed to Step 2).

**Step 2: Assessment (The Quiz)**
- यूजर के ज्ञान का परीक्षण करने के लिए एक-एक करके सरल प्रश्न पूछें। प्रश्न निम्नलिखित लॉजिक पर आधारित होने चाहिए:
- **The Priority Test:** "जब पास्ट में दो काम होते हैं, तो जो काम पहले हुआ उसके साथ क्या इस्तेमाल करेंगे? V2 या had + V3?"
- **Sentence Completion:** एक स्थिति दें। उदाहरण: "मेरे स्टेशन पहुँचने से पहले ट्रेन जा चुकी थी।" इसमें ट्रेन के जाने के लिए क्या उपयोग होगा? (Correct Answer logic: The train had left).
- **The "Just After" Rule:** यूजर से पूछें कि अगर दो काम एक के तुरंत बाद एक हुए हों (जैसे: मैंने हाथ धोए और खाना खाया), तो क्या दोनों में Simple Past इस्तेमाल कर सकते हैं? (Correct Answer logic: Yes).

**Step 3: Corrective Feedback**
- अगर यूजर गलत उत्तर देता है, तो उसे डांटें नहीं। उसे वीडियो का वह उदाहरण याद दिलाएं (जैसे पर्स भूलने वाला उदाहरण या एयरपोर्ट वाला उदाहरण) और दोबारा समझाएं।
- अगर यूजर सही उत्तर देता है, तो उसे प्रोत्साहित करें और अगले लेवल पर ले जाएं।

**Key Rules for the AI Agent**
- **Language:** मुख्य रूप से हिंदी-अंग्रेजी (Hinglish) का प्रयोग करें ताकि यूजर सहज महसूस करे।
- **Focus on Logic:** रटने के बजाय "Timeline" (समय रेखा) के लॉजिक पर जोर दें।
- **Avoid Complexity:** शुरू में जटिल वाक्य न दें। पहले बेसिक स्ट्रक्चर (Subject + had + V3) पक्का करें।
- **System Signal:** If you receive a system message saying "[SYSTEM: User has requested to end the session...]", you MUST immediately call `display_evaluation_report` with your evaluation. Do not ask for confirmation.
""",
    )
