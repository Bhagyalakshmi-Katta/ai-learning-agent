import os
import base64
import time
import gradio as gr

import agent

from memory import StudentMemory
from agent import learning_agent, planner

from database import (
    create_database,
    create_conversation,
    save_message,
    get_conversations,
    get_messages,
    update_conversation_title,
    delete_empty_conversations,
)


# ============================================================
# DATABASE SETUP
# ============================================================

create_database()

# Remove old empty conversations
delete_empty_conversations()

# Conversation is created only after first message
current_conversation_id = None


# ============================================================
# AI AVATAR
# ============================================================

AI_AVATAR_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMU"
    "FRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU"
    "FBQUFBQUFBT/wAARCADIAMgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUF"
    "BAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVW"
    "V1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi"
    "4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAEC"
    "AxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVm"
    "Z2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq"
    "8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD4aNByaXpSc9qyOiwmeBTSD3oYc0AUD2Gk0nfFOYYPSmYzQJvUQnFHXqaOlJ6VLaRVrini"
    "it/w34C17xa4/szTpZo+T574jiGOuXbCj867bS/gYQ4GseILS0fH+psUa6fPocYUfma5KmMo0tJSO6ll+IrfBE8qI7UY9jX034U/"
    "Z08NalIokh1q9GOZZWWBCfoFJ/WvTtP/AGZvBsCgHw5BOeOZp5HJ+vNcyzKlL4U38jpllVWn8bS+Z8L7T6Gj8Oa+92/Zz8IMu0eF"
    "NPHHZHrkNf8A2cfDkEjpB4NlmQ5/eWd/IhX8GNP6/FauLEsulLaa+8+NWGKQqQK+o1/ZR0zxLcSQaZ/buhXSLuKXsaTxtz26GuJ8"
    "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"
)

AI_AVATAR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ai_avatar.jpg",
)

# Avatar is embedded in this file, so no extra image file is needed
with open(AI_AVATAR, "wb") as _avatar_file:
    _avatar_file.write(base64.b64decode(AI_AVATAR_B64))


# ============================================================
# THINKING MESSAGES
# ============================================================

THINKING_TEXT = {
    "EXPLAIN": "Preparing a simple explanation",
    "QUIZ": "Creating a fun quiz for you",
    "PLAN": "Building your study plan",
    "MEMORY": "Checking your learning progress",
    "CHAT": "Thinking about your question",
}


# ============================================================
# MEMORY
# ============================================================

def new_memory():
    agent.memory = StudentMemory()

    agent.memory.update_profile(
        name="Student",
        level="beginner",
        learning_style="simple step-by-step explanations",
    )


new_memory()


# ============================================================
# STUDENT EMOTION / ENCOURAGEMENT
# ============================================================

def get_student_reaction(message):
    text = message.lower().strip()

    # Student understood
    if any(
        phrase in text
        for phrase in [
            "i get it",
            "got it",
            "i got it",
            "understood",
            "i understand",
            "now i understand",
            "i understood",
            "makes sense",
            "it makes sense",
            "clear now",
        ]
    ):
        return "🔥 **Well done! You got it!** ✨"

    # Student solved something
    if any(
        phrase in text
        for phrase in [
            "i solved",
            "i solved it",
            "i did it",
            "i got the answer",
            "my answer is correct",
            "i figured it out",
        ]
    ):
        return "🏆 **Amazing! You figured it out!** 🎉"

    # Student is confused
    if any(
        phrase in text
        for phrase in [
            "i don't understand",
            "i dont understand",
            "confused",
            "i am confused",
            "i'm confused",
            "not understand",
            "still don't get it",
            "still dont get it",
        ]
    ):
        return "🤗 **No worries! Let's break it down step by step.** 💛"

    # Student is struggling
    if any(
        phrase in text
        for phrase in [
            "i can't do this",
            "i cant do this",
            "too difficult",
            "this is difficult",
            "i am stuck",
            "i'm stuck",
            "stuck",
            "hard",
            "difficult",
        ]
    ):
        return "💪 **Don't give up! One small step at a time. You've got this!** 🔥"

    # Thanks
    if any(
        phrase in text
        for phrase in [
            "thank you",
            "thanks",
            "thx",
        ]
    ):
        return "😊 **You're welcome! Keep learning!** ✨"

    # Positive
    if any(
        phrase in text
        for phrase in [
            "awesome",
            "great",
            "nice",
            "cool",
            "perfect",
        ]
    ):
        return "✨ **Love that energy! Let's keep going!** 🔥"

    return "✨ **LearnPiolet is ready to help you learn!**"


# ============================================================
# CONVERSATION FUNCTIONS
# ============================================================

def load_conversation(conversation_id):
    messages = get_messages(conversation_id)

    history = []

    for role, content in messages:
        history.append(
            {
                "role": role,
                "content": content,
            }
        )

    return history


def get_conversation_choices():
    conversations = get_conversations()

    choices = []

    for conversation_id, title, created_at in conversations:
        choices.append(
            (title, conversation_id)
        )

    return choices


def select_conversation(conversation_id):
    global current_conversation_id

    if conversation_id is None:
        return (
            [],
            None,
            "✨ **Welcome champ! Ready to learn something awesome?**",
        )

    current_conversation_id = conversation_id

    history = load_conversation(conversation_id)

    return (
        history,
        conversation_id,
        "✦ **Conversation loaded. Let's continue, champ!**",
    )


# ============================================================
# NEW CONVERSATION
# ============================================================

def reset_chat():
    global current_conversation_id

    # Reset memory
    new_memory()

    # Do not create empty database conversation
    current_conversation_id = None

    choices = get_conversation_choices()

    return (
        [],
        gr.update(
            choices=choices,
            value=None,
        ),
        None,
        "✨ **Welcome champ! What are we learning today?**",
    )


# ============================================================
# CHAT FUNCTION
# ============================================================

def chat_with_agent(
    message,
    history,
    conversation_id,
):
    global current_conversation_id

    # --------------------------------------------------------
    # EMPTY MESSAGE CHECK
    # --------------------------------------------------------

    if not message or not message.strip():
        yield (
            "",
            history or [],
            gr.update(),
            conversation_id,
            "✨ **I'm listening, champ... Ask me anything!**",
        )
        return

    history = history or []

    # --------------------------------------------------------
    # STUDENT REACTION
    # --------------------------------------------------------

    reaction = get_student_reaction(message)

    # --------------------------------------------------------
    # CREATE CONVERSATION ONLY WHEN NEEDED
    # --------------------------------------------------------

    is_first_message = conversation_id is None

    if is_first_message:
        conversation_id = create_conversation(
            "New Conversation"
        )

        current_conversation_id = conversation_id

    else:
        current_conversation_id = conversation_id

    # --------------------------------------------------------
    # AUTOMATIC CONVERSATION TITLE
    # --------------------------------------------------------

    if is_first_message:
        title = message.strip()
        title = " ".join(title.split())

        if len(title) > 40:
            title = title[:40].rstrip() + "..."

        update_conversation_title(
            conversation_id,
            title,
        )

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    save_message(
        conversation_id,
        "user",
        message,
    )

    # --------------------------------------------------------
    # SHOW USER MESSAGE
    # --------------------------------------------------------

    history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    # --------------------------------------------------------
    # SHOW THINKING MESSAGE
    # --------------------------------------------------------

    history.append(
        {
            "role": "assistant",
            "content": (
                "✦ **LearnPiolet is thinking...**\n\n"
                "✨ *Preparing something helpful for you...*"
            ),
        }
    )

    yield (
        "",
        history,
        gr.update(),
        conversation_id,
        reaction,
    )

    time.sleep(0.5)

    # --------------------------------------------------------
    # PLANNER
    # --------------------------------------------------------

    action = planner(message)

    thinking_message = THINKING_TEXT.get(
        action,
        "Thinking about your question",
    )

    history[-1]["content"] = (
        "✦ **LearnPiolet is thinking...**\n\n"
        f"✨ *{thinking_message}...*"
    )

    yield (
        "",
        history,
        gr.update(),
        conversation_id,
        reaction,
    )

    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    response = learning_agent(message)

    # --------------------------------------------------------
    # SAVE AI RESPONSE
    # --------------------------------------------------------

    save_message(
        conversation_id,
        "assistant",
        response,
    )

    # --------------------------------------------------------
    # TYPE RESPONSE
    # --------------------------------------------------------

    step = 6

    for i in range(0, len(response), step):
        shown = response[: i + step]

        history[-1]["content"] = shown + " ▌"

        yield (
            "",
            history,
            gr.update(),
            conversation_id,
            reaction,
        )

        time.sleep(0.01)

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    history[-1]["content"] = response

    # --------------------------------------------------------
    # REFRESH SIDEBAR
    # --------------------------------------------------------

    updated_choices = get_conversation_choices()

    yield (
        "",
        history,
        gr.update(
            choices=updated_choices,
            value=conversation_id,
        ),
        conversation_id,
        reaction,
    )


# ============================================================
# CSS
# ============================================================

CSS = """
/* ============================================================
   COLOR PALETTE
   ============================================================ */

:root {
    --orange: #ff7048;
    --orange-light: #ff9870;
    --blue: #5b8def;
    --blue-light: #8fb1ff;

    --peach: #fff0e7;
    --lavender: #f1edff;
    --cream: #fffaf7;
    --white: #ffffff;

    --navy: #292746;
    --text: #56566f;
    --muted: #9695a8;
    --border: #eee5df;
}


/* ============================================================
   PAGE
   ============================================================ */

body {
    background:
        radial-gradient(
            circle at 5% 5%,
            #ffe7d8 0%,
            transparent 25%
        ),
        radial-gradient(
            circle at 95% 5%,
            #eee9ff 0%,
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #fffaf7,
            #fff8f4,
            #fbf9ff
        ) !important;
}


/* ============================================================
   GRADIO CONTAINER
   ============================================================ */

.gradio-container {
    max-width: 1450px !important;
    margin: auto !important;
    padding: 15px 20px !important;
}


/* Remove footer */

footer {
    display: none !important;
}


/* ============================================================
   APP SHELL
   ============================================================ */

#app-shell {
    background: rgba(255, 255, 255, 0.82) !important;

    border: 1px solid rgba(255, 255, 255, 0.95) !important;

    border-radius: 30px !important;

    overflow: hidden !important;

    min-height: 92vh;

    box-shadow:
        0 25px 70px rgba(55, 45, 70, 0.10),
        0 5px 18px rgba(55, 45, 70, 0.05);
}


/* ============================================================
   SIDEBAR
   ============================================================ */

#sidebar {
    min-width: 280px !important;
    max-width: 280px !important;

    padding: 27px 20px !important;

    background:
        linear-gradient(
            180deg,
            #fff1e8 0%,
            #fff9f5 58%,
            #f5f1ff 100%
        );

    border-right: 1px solid #f2e5df;
}


/* ============================================================
   BRAND
   ============================================================ */

#brand {
    margin-bottom: 24px;
}

#brand h1 {
    color: var(--navy);
    font-size: 28px !important;
    font-weight: 800 !important;
}

#brand p {
    color: var(--muted);
    font-size: 13px;
    margin-top: 5px;
}


/* ============================================================
   GEMINI STYLE BRAND SPARKLE
   ============================================================ */

#brand-sparkle {
    position: relative;

    display: inline-flex;

    width: 32px;
    height: 32px;

    margin-right: 7px;

    align-items: center;
    justify-content: center;

    font-size: 28px;

    color: #ff7048;

    filter:
        drop-shadow(
            0 4px 8px rgba(255, 112, 72, 0.22)
        );

    animation:
        brandSparkle 3s ease-in-out infinite;
}


/* small blue sparkle */

#brand-sparkle::after {
    content: "✦";

    position: absolute;

    right: -4px;
    bottom: -4px;

    font-size: 13px;

    color: #5b8def;

    animation:
        miniSparkle 2s ease-in-out infinite;
}


@keyframes brandSparkle {

    0%,
    100% {
        transform: rotate(0deg) scale(1);
    }

    50% {
        transform: rotate(8deg) scale(1.08);
    }
}


@keyframes miniSparkle {

    0%,
    100% {
        transform: scale(0.8);
        opacity: 0.6;
    }

    50% {
        transform: scale(1.25);
        opacity: 1;
    }
}


/* ============================================================
   NEW CHAT BUTTON
   ============================================================ */

#new-chat {
    width: 100% !important;

    min-height: 48px !important;

    border-radius: 999px !important;

    border: none !important;

    background:
        linear-gradient(
            135deg,
            #ff7048,
            #ff9a72
        ) !important;

    color: white !important;

    font-weight: 700 !important;

    box-shadow:
        0 10px 24px rgba(255, 112, 72, 0.22);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease !important;
}

#new-chat:hover {
    transform: translateY(-2px);

    box-shadow:
        0 14px 30px rgba(255, 112, 72, 0.30);
}


/* ============================================================
   PREVIOUS CHAT HEADING
   ============================================================ */

#chat-heading {
    color: var(--navy);

    font-weight: 800;

    margin-top: 27px;

    margin-bottom: 10px;
}


/* ============================================================
   CONVERSATION LIST
   ============================================================ */

#conversation-list {
    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    padding: 0 !important;
}


/* ============================================================
   PREVIOUS CHAT PILL
   ============================================================ */

#conversation-list label {
    position: relative !important;

    display: flex !important;

    align-items: center !important;

    width: 100% !important;

    min-height: 42px !important;

    margin: 7px 0 !important;

    padding: 8px 12px !important;

    border-radius: 999px !important;

    border: 1px solid rgba(255, 255, 255, 0.75) !important;

    background:
        rgba(255, 255, 255, 0.60) !important;

    color: #464762 !important;

    box-shadow:
        0 4px 12px rgba(60, 45, 50, 0.035);

    transition:
        transform 0.2s ease,
        background 0.2s ease,
        box-shadow 0.2s ease !important;

    overflow: hidden !important;
}


/* ============================================================
   GEMINI-STYLE SPARKLE ICON
   ============================================================ */

#conversation-list label::before {
    content: "✦";

    display: flex;

    align-items: center;

    justify-content: center;

    width: 27px;

    height: 27px;

    min-width: 27px;

    margin-right: 9px;

    border-radius: 50%;

    background:
        linear-gradient(
            135deg,
            #fff0df,
            #eaf0ff
        );

    color: #ff7048;

    font-size: 14px;

    font-weight: 800;

    box-shadow:
        inset 0 0 0 1px rgba(255, 255, 255, 0.9),
        0 3px 8px rgba(90, 100, 160, 0.08);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}


/* ============================================================
   DIFFERENT GEMINI-STYLE SPARKLES
   NO HEART SHAPES
   ============================================================ */

#conversation-list label:nth-child(2)::before {
    content: "✧";

    color: #5b8def;

    background:
        linear-gradient(
            135deg,
            #e9f0ff,
            #fff1e5
        );
}


#conversation-list label:nth-child(3)::before {
    content: "✦";

    color: #ff7048;

    background:
        linear-gradient(
            135deg,
            #fff0df,
            #e9f0ff
        );
}


#conversation-list label:nth-child(4)::before {
    content: "✧";

    color: #6d86e8;

    background:
        linear-gradient(
            135deg,
            #edf1ff,
            #fff0e6
        );
}


#conversation-list label:nth-child(5)::before {
    content: "✦";

    color: #f47b55;

    background:
        linear-gradient(
            135deg,
            #fff0e6,
            #e8f0ff
        );
}


#conversation-list label:nth-child(6)::before {
    content: "✧";

    color: #5689e8;

    background:
        linear-gradient(
            135deg,
            #e9f1ff,
            #fff1e7
        );
}


#conversation-list label:nth-child(7)::before {
    content: "✦";

    color: #ff7850;

    background:
        linear-gradient(
            135deg,
            #fff0e6,
            #e9f0ff
        );
}


#conversation-list label:nth-child(8)::before {
    content: "✧";

    color: #6885e8;

    background:
        linear-gradient(
            135deg,
            #edf1ff,
            #fff0e6
        );
}


/* ============================================================
   CHAT HOVER
   ============================================================ */

#conversation-list label:hover {
    background:
        linear-gradient(
            135deg,
            #fff2e9,
            #f0f4ff
        ) !important;

    border-color: #ffd9c8 !important;

    transform: translateX(4px) !important;

    box-shadow:
        0 7px 18px rgba(255, 112, 72, 0.10);
}


#conversation-list label:hover::before {
    transform: rotate(12deg) scale(1.08);

    box-shadow:
        0 5px 13px rgba(90, 110, 180, 0.13);
}


/* ============================================================
   SELECTED CHAT
   ============================================================ */

#conversation-list label:has(input:checked) {
    background:
        linear-gradient(
            135deg,
            #ffe6d8,
            #edf1ff
        ) !important;

    border-color: #f3d5c5 !important;

    color: #343452 !important;

    font-weight: 700 !important;

    box-shadow:
        0 7px 20px rgba(100, 75, 80, 0.08);
}


#conversation-list label:has(input:checked)::before {
    color: #ff7048;

    transform: scale(1.08) rotate(8deg);

    box-shadow:
        0 5px 14px rgba(255, 112, 72, 0.15);
}


/* ============================================================
   MAIN CONTENT
   ============================================================ */

#main-content {
    padding: 28px 40px 22px 40px !important;

    background:
        radial-gradient(
            circle at 90% 0%,
            #f0ebff 0%,
            transparent 27%
        ),
        #fffdfb !important;
}


/* ============================================================
   HEADER
   ============================================================ */

#main-header {
    margin-bottom: 12px;
}

#main-header h1 {
    color: var(--navy);

    font-size: 31px !important;

    font-weight: 850 !important;

    letter-spacing: -1.2px;

    margin: 0 0 3px 0 !important;
}

#main-header p {
    color: #85869a;

    font-size: 14px;
}

#sparkle {
    display: inline-block;

    color: #ff7048;

    animation:
        headerSparkle 2.5s ease-in-out infinite;
}


#sparkle::after {
    content: "✦";

    color: #5b8def;

    font-size: 12px;

    margin-left: 2px;
}


@keyframes headerSparkle {

    0%,
    100% {
        transform: scale(1) rotate(0deg);
    }

    50% {
        transform: scale(1.15) rotate(8deg);
    }
}


/* ============================================================
   REACTION
   ============================================================ */

#reaction {
    background:
        linear-gradient(
            90deg,
            #fff0e7,
            #f3efff
        );

    border: 1px solid #f3ddd1;

    border-radius: 999px;

    padding: 9px 15px !important;

    margin: 5px 0 10px 0;

    color: #565772;

    font-size: 13px;

    box-shadow:
        0 5px 18px rgba(70, 55, 50, 0.04);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;
}


/* ============================================================
   CHATBOT
   ============================================================ */

#chatbot {
    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    border-radius: 0 !important;

    padding: 5px 2px !important;
}

#chatbot > .wrap {
    background: transparent !important;

    border: none !important;

    box-shadow: none !important;
}


/* ============================================================
   AI AVATAR (small, round)
   ============================================================ */

#chatbot .avatar-container {
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
    flex-shrink: 0 !important;
    align-self: flex-end !important;
}

#chatbot .avatar-container img,
#chatbot .avatar-image {
    width: 34px !important;
    height: 34px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 2px solid #ffe3d3 !important;
    box-shadow: 0 3px 10px rgba(255, 112, 72, 0.18) !important;
}


/* Cute floating mascot in sidebar */

@keyframes mascot-float {
    0%, 100% { transform: translateY(0px) rotate(-2deg); }
    50% { transform: translateY(-6px) rotate(2deg); }
}

.mascot-float {
    animation: mascot-float 3s ease-in-out infinite;
}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

#chatbot .message {
    border-radius: 20px !important;

    padding: 13px 17px !important;

    font-size: 15px !important;

    line-height: 1.65 !important;

    max-width: 78% !important;

    border: none !important;

    box-shadow:
        0 6px 20px rgba(55, 45, 50, 0.045);
}


/* User message */

#chatbot .message.user {
    background:
        linear-gradient(
            135deg,
            #ffdfcc,
            #ffe9dc
        ) !important;

    color: #40364c !important;

    border: 1px solid #f5d4c0 !important;

    border-bottom-right-radius: 6px !important;
}


/* AI message */

#chatbot .message.bot {
    background:
        rgba(255, 255, 255, 0.94) !important;

    color: var(--navy) !important;

    border: 1px solid #eee8e4 !important;

    border-bottom-left-radius: 6px !important;

    box-shadow:
        0 7px 25px rgba(55, 45, 50, 0.055);
}


/* ============================================================
   MARKDOWN
   ============================================================ */

#chatbot p {
    margin: 4px 0 !important;
}

#chatbot strong {
    font-weight: 800 !important;
}


/* ============================================================
   CODE BLOCKS
   ============================================================ */

#chatbot pre {
    background: #24243d !important;

    border: none !important;

    border-radius: 14px !important;

    padding: 15px !important;
}


/* ============================================================
   INPUT AREA
   ============================================================ */

#input-area {
    display: flex !important;

    align-items: center !important;

    width: 88% !important;

    margin: 10px auto 0 auto !important;

    background:
        rgba(255, 255, 255, 0.98) !important;

    border: 1px solid #eee5df !important;

    border-radius: 999px !important;

    padding: 5px 6px 5px 17px !important;

    box-shadow:
        0 12px 35px rgba(65, 45, 35, 0.10),
        0 2px 8px rgba(65, 45, 35, 0.04);

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease !important;
}


/* Input focus */

#input-area:focus-within {
    border-color: #ffc1a8 !important;

    box-shadow:
        0 12px 38px rgba(255, 112, 72, 0.14),
        0 0 0 3px rgba(255, 112, 72, 0.06);
}


/* ============================================================
   TEXTBOX
   ============================================================ */

#message-box {
    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    border-radius: 999px !important;

    min-height: 38px !important;
}

#message-box > div {
    background: transparent !important;

    border: none !important;

    box-shadow: none !important;
}

#message-box textarea {
    background: transparent !important;

    border: none !important;

    outline: none !important;

    box-shadow: none !important;

    border-radius: 999px !important;

    color: var(--navy) !important;

    font-size: 14px !important;

    font-weight: 600 !important;

    padding: 10px 8px !important;

    resize: none !important;
}


/* Placeholder */

#message-box textarea::placeholder {
    color: #aaa8b8 !important;

    opacity: 1 !important;
}


/* Focus */

#message-box textarea:focus {
    outline: none !important;

    border: none !important;

    box-shadow: none !important;
}


/* ============================================================
   SEND BUTTON
   ============================================================ */

#send-btn {
    width: 40px !important;

    min-width: 40px !important;

    max-width: 40px !important;

    height: 40px !important;

    min-height: 40px !important;

    max-height: 40px !important;

    padding: 0 !important;

    margin: 0 !important;

    border: none !important;

    border-radius: 50% !important;

    background:
        linear-gradient(
            135deg,
            #ff7048,
            #ff9870
        ) !important;

    color: white !important;

    font-size: 17px !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    flex-shrink: 0 !important;

    box-shadow:
        0 6px 16px rgba(255, 112, 72, 0.27);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease !important;
}


/* Send hover */

#send-btn:hover {
    transform: scale(1.08) !important;

    box-shadow:
        0 9px 21px rgba(255, 112, 72, 0.35);
}


/* Send click */

#send-btn:active {
    transform: scale(0.94) !important;
}


/* ============================================================
   STATUS
   ============================================================ */

#ai-status {
    text-align: center;

    color: #9695a8;

    font-size: 11px;

    font-weight: 600;

    margin-top: 7px;
}


/* ============================================================
   NEW CONVERSATION SPARKLE ANIMATION
   ============================================================ */

#new-chat:active {
    transform: scale(0.96) !important;
}


/* ============================================================
   SCROLLBAR
   ============================================================ */

::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #eadfd9;

    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: #d8c8c0;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 850px) {

    #sidebar {
        min-width: 210px !important;
        max-width: 210px !important;
    }

    #main-content {
        padding: 20px !important;
    }

    #main-header h1 {
        font-size: 25px !important;
    }

    #chatbot .message {
        max-width: 90% !important;
    }

    #input-area {
        width: 96% !important;
    }

    #send-btn {
        width: 38px !important;

        height: 38px !important;

        min-width: 38px !important;

        max-width: 38px !important;

        min-height: 38px !important;

        max-height: 38px !important;
    }
}
"""


# ============================================================
# LEARNPIOLET UI
# ============================================================

with gr.Blocks(
    title="LearnPiolet",
    css=CSS,
    theme=gr.themes.Base(
        font=[
            "Inter",
            "Arial",
            "sans-serif",
        ]
    ),
) as demo:

    # ========================================================
    # STATE
    # ========================================================

    conversation_state = gr.State(
        current_conversation_id
    )

    # ========================================================
    # APP SHELL
    # ========================================================

    with gr.Row(elem_id="app-shell"):

        # ====================================================
        # SIDEBAR
        # ====================================================

        with gr.Column(
            scale=2,
            elem_id="sidebar",
        ):

            # ------------------------------------------------
            # BRAND
            # ------------------------------------------------

            gr.HTML(
                """
                <div id="brand">

                    <div style="
                        display:flex;
                        align-items:center;
                    ">

                        <span id="brand-sparkle">
                            ✦
                        </span>

                        <span style="
                            font-size: 28px;
                            font-weight: 800;
                            color: #20244a;
                        ">
                            LearnPiolet
                        </span>

                    </div>

                    <p>
                        Your cute AI learning companion ✨
                    </p>

                </div>
                """
            )

            # ------------------------------------------------
            # NEW CHAT
            # ------------------------------------------------

            new_chat_button = gr.Button(
                "＋  New Conversation",
                variant="primary",
                elem_id="new-chat",
            )

            # ------------------------------------------------
            # PREVIOUS CHATS
            # ------------------------------------------------

            gr.Markdown(
                "✦ **Previous Chats**",
                elem_id="chat-heading",
            )

            conversation_list = gr.Radio(
                choices=get_conversation_choices(),
                label=None,
                show_label=False,
                elem_id="conversation-list",
            )

            # ------------------------------------------------
            # SIDEBAR FOOTER
            # ------------------------------------------------

            gr.HTML(
                """
                <div style="
                    margin-top: 35px;
                    padding: 18px;
                    border-radius: 20px;
                    background:
                        linear-gradient(
                            135deg,
                            #fff0e5,
                            #f0ebff
                        );
                    text-align: center;
                    box-shadow:
                        0 8px 22px
                        rgba(80,60,70,0.04);
                ">

                    <img
                        class="mascot-float"
                        src="data:image/jpeg;base64,__AVATAR__"
                        alt="LearnPiolet"
                        style="
                            width: 110px;
                            height: 110px;
                            border-radius: 50%;
                            object-fit: cover;
                            margin-bottom: 10px;
                            border: 4px solid #ffffff;
                            box-shadow:
                                0 0 0 4px #ffe3d3,
                                0 10px 24px rgba(255,112,72,0.28);
                        "
                    >

                    <div style="
                        color: #3d4167;
                        font-weight: 700;
                        font-size: 13px;
                    ">
                        Small steps.
                        Big dreams. ✨
                    </div>

                    <div style="
                        color: #85869b;
                        font-size: 11px;
                        margin-top: 5px;
                    ">
                        Keep learning every day.
                    </div>

                </div>
                """.replace("__AVATAR__", AI_AVATAR_B64)
            )

        # ====================================================
        # MAIN AREA
        # ====================================================

        with gr.Column(
            scale=7,
            elem_id="main-content",
        ):

            # ------------------------------------------------
            # HEADER
            # ------------------------------------------------

            gr.HTML(
                """
                <div id="main-header">

                    <h1>
                        LearnPiolet
                        <span id="sparkle">✦</span>
                    </h1>

                    <p>
                        Your Personalized AI Learning Agent
                        ·&nbsp;
                        Learn at your own pace 💛
                    </p>

                </div>
                """
            )

            # ------------------------------------------------
            # REACTION
            # ------------------------------------------------

            reaction_box = gr.Markdown(
                "✨ **Welcome champ! What would you like to learn today?**",
                elem_id="reaction",
            )

            # ------------------------------------------------
            # CHATBOT
            # ------------------------------------------------

            chatbot_ui = gr.Chatbot(
                label=None,
                show_label=False,
                type="messages",
                height=560,
                placeholder="✦ Start learning with LearnPiolet...",
                show_copy_button=True,
                autoscroll=True,
                avatar_images=(None, AI_AVATAR),
                elem_id="chatbot",
            )

            # ------------------------------------------------
            # INPUT AREA
            # ------------------------------------------------

            with gr.Row(elem_id="input-area"):

                message_box = gr.Textbox(
                    placeholder="Ask LearnPiolet anything...",
                    show_label=False,
                    scale=9,
                    autofocus=True,
                    lines=1,
                    max_lines=5,
                    elem_id="message-box",
                )

                send_button = gr.Button(
                    "➤",
                    scale=1,
                    variant="primary",
                    elem_id="send-btn",
                )

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            gr.Markdown(
                "✦ Learn · Practice · Understand · Grow",
                elem_id="ai-status",
            )

    # ========================================================
    # SEND BUTTON
    # ========================================================

    send_button.click(
        chat_with_agent,
        inputs=[
            message_box,
            chatbot_ui,
            conversation_state,
        ],
        outputs=[
            message_box,
            chatbot_ui,
            conversation_list,
            conversation_state,
            reaction_box,
        ],
    )

    # ========================================================
    # ENTER KEY
    # ========================================================

    message_box.submit(
        chat_with_agent,
        inputs=[
            message_box,
            chatbot_ui,
            conversation_state,
        ],
        outputs=[
            message_box,
            chatbot_ui,
            conversation_list,
            conversation_state,
            reaction_box,
        ],
    )

    # ========================================================
    # NEW CONVERSATION
    # ========================================================

    new_chat_button.click(
        reset_chat,
        inputs=[],
        outputs=[
            chatbot_ui,
            conversation_list,
            conversation_state,
            reaction_box,
        ],
    )

    # ========================================================
    # LOAD PREVIOUS CONVERSATION
    # ========================================================

    conversation_list.change(
        select_conversation,
        inputs=[
            conversation_list,
        ],
        outputs=[
            chatbot_ui,
            conversation_state,
            reaction_box,
        ],
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    demo.launch(
        share=False
    )