# agent.py
# Agent = Planner + Context management + Conditional workflow + Error handling

import json
import re

from memory import StudentMemory
from tools import (
    client,
    MODEL,
    explain_topic,
    generate_quiz,
    create_study_plan
)

# Create memory
memory = StudentMemory()


# =====================================================
# Agent Planning
# =====================================================
def planner(user_input):

    text = user_input.lower()

    if any(word in text for word in [
        "explain",
        "teach",
        "what is",
        "meaning",
        "understand"
    ]):
        return "EXPLAIN"

    elif any(word in text for word in [
        "quiz",
        "test",
        "questions",
        "mcq"
    ]):
        return "QUIZ"

    elif any(word in text for word in [
        "study plan",
        "schedule",
        "plan my",
        "timetable"
    ]):
        return "PLAN"

    elif any(word in text for word in [
        "progress",
        "memory",
        "what have i learned",
        "my status"
    ]):
        return "MEMORY"

    else:
        return "CHAT"


# =====================================================
# Context Management
# =====================================================
def build_context():

    return f"""
Student Profile:
Name: {memory.profile["name"]}
Level: {memory.profile["level"]}
Learning Style: {memory.profile["learning_style"]}

Topics Studied:
{memory.progress["topics_studied"]}

Topics Mastered:
{memory.progress["topics_mastered"]}

Quiz Scores:
{memory.progress["quiz_scores"]}

Current Topic:
{memory.current_state["current_topic"]}

Last Action:
{memory.current_state["last_action"]}
"""


# =====================================================
# Main Agent
# =====================================================
def learning_agent(user_input):

    try:

        action = planner(user_input)

        memory.set_action(action)

        # -------------------------
        # EXPLANATION
        # -------------------------

        if action == "EXPLAIN":

            topic = user_input

            for phrase in [
                "explain",
                "teach me",
                "what is",
                "what are",
                "meaning of"
            ]:

                topic = topic.lower().replace(phrase, "")

            topic = topic.strip()

            memory.add_topic(topic)

            result = explain_topic(
                topic,
                memory.profile["level"]
            )

            return result


        # -------------------------
        # QUIZ
        # -------------------------

        elif action == "QUIZ":

            topic = memory.current_state["current_topic"]

            if not topic:

                # CHANGED from input(): input() would freeze the web UI,
                # so the agent now asks the question in the chat instead.
                return (
                    "Which topic should I create a quiz for? "
                    "Ask me to explain a topic first (for example: "
                    "**Explain Python loops**), then ask for a quiz."
                )

            memory.add_topic(topic)

            result = generate_quiz(
                topic,
                memory.current_state["difficulty"]
            )

            return result


        # -------------------------
        # STUDY PLAN
        # -------------------------

        elif action == "PLAN":

            topic_match = re.search(
                r"(?:for|on)\s+(.+)",
                user_input,
                re.IGNORECASE
            )

            if topic_match:
                topic = topic_match.group(1)
            else:
                topic = memory.current_state["current_topic"]

            if not topic:

                # CHANGED from input(): same reason as the quiz branch.
                return (
                    "Which topic should I create a plan for? "
                    "Try: **Create a study plan for Python decorators**"
                )

            memory.add_topic(topic)

            result = create_study_plan(
                topic,
                days=7,
                hours_per_day=2
            )

            return result


        # -------------------------
        # MEMORY
        # -------------------------

        elif action == "MEMORY":

            return json.dumps(
                memory.show_memory(),
                indent=2
            )


        # -------------------------
        # GENERAL CHAT
        # -------------------------

        else:

            context = build_context()

            response = client.chat.completions.create(

                model=MODEL,

                messages=[

                    {
                        "role": "system",
                        "content": f"""
You are an AI Learning and Personalized Education Agent.

You help students learn technical subjects.

Student context:

{context}

Adapt your explanation to the student's level.

Use simple English and step-by-step explanations.
"""
                    },

                    {
                        "role": "user",
                        "content": user_input
                    }
                ],

                temperature=0.5
            )

            return response.choices[0].message.content


    except Exception as e:

        return f"""
Sorry, I encountered an error.

Error:
{str(e)}

Please try your request again.
"""


# =====================================================
# Terminal chatbot (optional - the web UI is in app.py)
# =====================================================
def chatbot():

    print("=" * 60)
    print("       AI PERSONALIZED LEARNING AGENT")
    print("=" * 60)

    print("\nI can:")
    print("• Explain topics")
    print("• Generate quizzes")
    print("• Create study plans")
    print("• Remember your learning progress")
    print("• Track your current topic")
    print("\nType 'exit' to stop.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:

            print("\nAgent: Goodbye! Keep learning 🚀")
            break

        response = learning_agent(user_input)

        print("\nAgent:")
        print(response)

        print("\n" + "-" * 60)


# =====================================================
# Testing
# =====================================================
def run_tests():

    test_cases = [
        "Explain Python loops",
        "Give me a quiz",
        "Create a study plan for SQL",
        "Show my progress",
        "Hello, how are you?"
    ]

    print("=" * 60)
    print("AGENT TESTING")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):

        print(f"\nTest {i}")
        print("Input:", test)

        action = planner(test)

        print("Selected Action:", action)

        assert action in [
            "EXPLAIN",
            "QUIZ",
            "PLAN",
            "MEMORY",
            "CHAT"
        ]

        print("Status: PASS")

    print("\nAll tests completed.")


# Run tests with:  python agent.py
if __name__ == "__main__":
    run_tests()
