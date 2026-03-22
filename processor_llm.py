from dotenv import load_dotenv
import os
from groq import Groq
import json

# Load .env file
load_dotenv()

# Get and validate API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

api_key = api_key.strip()

# Initialize Groq client
groq = Groq(api_key=api_key)


def classify_with_llm(log_msg):
    prompt = f"""
You are a strict classifier.

Classify the log message into EXACTLY one of:
- Workflow Error
- Deprecation Warning
- Unclassified

Return ONLY valid JSON in this format:
{{"category": "Workflow Error"}}

Do NOT add explanations or extra text.

Log message:
{log_msg}
"""

    try:
        chat_completion = groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
    except Exception as e:
        print("API ERROR:", e)
        return "Unclassified"

    content = chat_completion.choices[0].message.content.strip()

    # Debug output
    print("RAW RESPONSE:", content)

    # Try parsing JSON
    try:
        result = json.loads(content)
        return result.get("category", "Unclassified")
    except Exception:
        # Fallback in case model breaks format
        if "Workflow Error" in content:
            return "Workflow Error"
        elif "Deprecation Warning" in content:
            return "Deprecation Warning"
        else:
            return "Unclassified"


if __name__ == "__main__":
    print(classify_with_llm(
        "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."
    ))

    print(classify_with_llm(
        "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025"
    ))

    print(classify_with_llm(
        "System reboot initiated by user 12345."
    ))