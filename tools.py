# tools.py
# Groq LLM client + the three agent tools

import os
from dotenv import load_dotenv
from groq import Groq

# Reads GROQ_API_KEY from the .env file in the project folder
load_dotenv()

if not os.environ.get("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY not found. Create a file named .env in the project "
        "folder containing:  GROQ_API_KEY=your_key_here"
    )

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


# -------------------------
# Tool 1 — Explanation
# -------------------------
def explain_topic(topic, level="beginner"):

    prompt = f"""
Explain the topic "{topic}" to a {level} student.

Requirements:
- Use very simple English.
- Explain step by step.
- Give a simple real-world example.
- Give one small coding/example problem.
- Do not assume advanced knowledge.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a patient AI teacher."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


# -------------------------
# Tool 2 — Quiz Generator
# -------------------------
def generate_quiz(topic, difficulty="beginner"):

    prompt = f"""
Create a short quiz for a student.

Topic: {topic}
Difficulty: {difficulty}

Create exactly 5 multiple-choice questions.

Format:

Q1. Question
A) option
B) option
C) option
D) option
Answer: X

Do this for all 5 questions.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an educational quiz generator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )

    return response.choices[0].message.content


# -------------------------
# Tool 3 — Study Plan Generator
# -------------------------
def create_study_plan(topic, days, hours_per_day):

    prompt = f"""
Create a personalized study plan.

Topic: {topic}
Number of days: {days}
Hours available per day: {hours_per_day}

The plan should contain:
1. Topic for each day
2. Learning activity
3. Practice activity
4. Revision
5. A small assessment

Keep it realistic for a student.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an AI learning planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content
