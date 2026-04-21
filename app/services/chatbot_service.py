from __future__ import annotations


def generate_chat_reply(message: str) -> str:
    text = message.strip().lower()
    if not text:
        return "Please type a question. I can explain risk scores, preventive measures, or when to consult a doctor."

    if any(k in text for k in ["urgent", "emergency", "chest pain", "severe breathing"]):
        return (
            "If symptoms are severe or rapidly worsening (like chest pain or major breathing difficulty), "
            "seek urgent medical care immediately."
        )

    if "risk score" in text or "score" in text:
        return (
            "Risk scores range from 0 to 1. Higher values mean stronger risk signals from your entered data, "
            "but they do not confirm diagnosis."
        )

    if "prevent" in text or "prevention" in text or "reduce risk" in text:
        return (
            "General prevention: stop smoking, stay active (target 150 min/week), improve sleep, "
            "eat high-fiber whole foods, and monitor key vitals like blood pressure and glucose."
        )

    if "doctor" in text or "consult" in text:
        return (
            "Medical consultation is recommended for moderate/high/urgent risk, persistent symptoms, "
            "or abnormal measurements like high BP or glucose."
        )

    return (
        "I can help with: understanding a disease risk result, explaining contributors, suggesting preventive actions, "
        "and deciding when consultation is recommended."
    )

