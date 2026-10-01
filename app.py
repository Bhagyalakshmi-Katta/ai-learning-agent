
import time
import gradio as gr

import agent
from memory import StudentMemory
from agent import learning_agent, planner

# Database functions
from database import (
    create_database,
    create_conversation,
    save_message,
    get_conversations,
    get_messages,
    update_conversation_title
)


# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

create_database()

# Create a conversation for this app session
current_conversation_id = create_conversation(
    "New Conversation"
)


# --------------------------------------------------
# THINKING MESSAGES
# --------------------------------------------------

THINKING_TEXT = {
    "EXPLAIN": "Preparing a simple explanation",
    "QUIZ": "Generating your quiz",
    "PLAN": "Building your study plan",
    "MEMORY": "Checking your learning progress",
    "CHAT": "Thinking about your question",
}


# --------------------------------------------------
# MEMORY
# --------------------------------------------------

def new_memory():

    agent.memory = StudentMemory()

    agent.memory.update_profile(
        name="Student",
        level="beginner",
        learning_style="simple step-by-step explanations"
    )


# Initialize memory
new_memory()


# --------------------------------------------------
# CONVERSATION FUNCTIONS
# --------------------------------------------------

def load_conversation(conversation_id):
    """
    Load all messages from a conversation.
    """

    messages = get_messages(conversation_id)

    history = []

    for role, content in messages:

        history.append({
            "role": role,
            "content": content
        })

    return history


def get_conversation_choices():
    """
    Get all conversations from SQLite
    and convert them into Gradio Radio choices.
    """

    conversations = get_conversations()

    choices = []

    for conversation_id, title, created_at in conversations:

        choices.append(
            (title, conversation_id)
        )

    return choices


def select_conversation(conversation_id):
    """
    Load the selected conversation.
    """

    if conversation_id is None:
        return [], None

    history = load_conversation(
        conversation_id
    )

    return history, conversation_id


# --------------------------------------------------
# NEW CONVERSATION
# --------------------------------------------------

def reset_chat():

    global current_conversation_id

    # Reset student memory
    new_memory()

    # Create a new conversation
    current_conversation_id = create_conversation(
        "New Conversation"
    )

    # Refresh sidebar
    choices = get_conversation_choices()

    return (
        [],
        choices,
        current_conversation_id
    )


# --------------------------------------------------
# CHAT FUNCTION
# --------------------------------------------------

def chat_with_agent(
    message,
    history,
    conversation_id
):

    # --------------------------------------------------
    # EMPTY MESSAGE CHECK
    # --------------------------------------------------

    if not message or not message.strip():

        yield (
            "",
            history or [],
            gr.update()
        )

        return


    history = history or []


    # --------------------------------------------------
    # CHECK FIRST MESSAGE
    # --------------------------------------------------

    existing_messages = get_messages(
        conversation_id
    )

    is_first_message = (
        len(existing_messages) == 0
    )


    # --------------------------------------------------
    # AUTOMATIC CONVERSATION TITLE
    # --------------------------------------------------

    if is_first_message:

        title = message.strip()

        # Remove unnecessary spaces/newlines
        title = " ".join(
            title.split()
        )

        # Keep title short
        if len(title) > 40:

            title = title[:40].rstrip() + "..."

        update_conversation_title(
            conversation_id,
            title
        )


    # --------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------

    save_message(
        conversation_id,
        "user",
        message
    )


    # --------------------------------------------------
    # SHOW USER MESSAGE
    # --------------------------------------------------

    history.append({
        "role": "user",
        "content": message
    })


    # --------------------------------------------------
    # SHOW THINKING MESSAGE
    # --------------------------------------------------

    history.append({
        "role": "assistant",
        "content": "🧠 *Analyzing your request...*"
    })

    yield (
        "",
        history,
        gr.update()
    )

    time.sleep(0.5)


    # --------------------------------------------------
    # PLANNER
    # --------------------------------------------------

    action = planner(message)

    # Safety check
    thinking_message = THINKING_TEXT.get(
        action,
        "Thinking about your question"
    )

    history[-1]["content"] = (
        f"⚙️ *Planner selected* **{action}** — "
        f"*{thinking_message}...*"
    )

    yield (
        "",
        history,
        gr.update()
    )


    # --------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------

    response = learning_agent(
        message
    )


    # --------------------------------------------------
    # SAVE AI RESPONSE
    # --------------------------------------------------

    save_message(
        conversation_id,
        "assistant",
        response
    )


    # --------------------------------------------------
    # TYPE RESPONSE
    # --------------------------------------------------

    step = 6

    for i in range(
        0,
        len(response),
        step
    ):

        shown = response[
            :i + step
        ]

        history[-1]["content"] = (
            shown + " ▌"
        )

        yield (
            "",
            history,
            gr.update()
        )

        time.sleep(0.01)


    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    history[-1]["content"] = response


    # --------------------------------------------------
    # REFRESH SIDEBAR
    # --------------------------------------------------

    updated_choices = (
        get_conversation_choices()
    )

    yield (
        "",
        history,
        gr.update(
            choices=updated_choices,
            value=conversation_id
        )
    )


# --------------------------------------------------
# CSS
# --------------------------------------------------

CSS = """
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}

footer {
    display: none !important;
}

#title {
    text-align: center;
    margin-bottom: 0;
}

#send-btn {
    min-height: 52px;
}

#sidebar {
    min-width: 230px !important;
    max-width: 260px !important;
}
"""


# --------------------------------------------------
# LEARNPIOLET UI
# --------------------------------------------------

with gr.Blocks(
    title="LearnPiolet",
    css=CSS,
    theme=gr.themes.Soft(
        primary_hue="emerald"
    )
) as demo:


    # --------------------------------------------------
    # CURRENT CONVERSATION STATE
    # --------------------------------------------------

    conversation_state = gr.State(
        current_conversation_id
    )


    with gr.Row():


        # ==================================================
        # SIDEBAR
        # ==================================================

        with gr.Column(
            scale=2,
            elem_id="sidebar"
        ):

            gr.Markdown(
                "## 💬 Conversations"
            )


            # New conversation button
            new_chat_button = gr.Button(
                "➕ New Conversation",
                variant="primary"
            )


            # Conversation list
            conversation_list = gr.Radio(
                choices=get_conversation_choices(),
                label="Previous Chats",
                show_label=True
            )


        # ==================================================
        # MAIN CHAT AREA
        # ==================================================

        with gr.Column(
            scale=7
        ):


            # --------------------------------------------------
            # TITLE
            # --------------------------------------------------

            gr.Markdown(
                """
                #  LearnPiolet
                ### Your Personalized AI Learning Agent

                Learn smarter with an AI tutor that can **explain topics,
                create quizzes, build study plans, and remember your progress.**
                """,
                elem_id="title"
            )


            # --------------------------------------------------
            # CHATBOT
            # --------------------------------------------------

            chatbot_ui = gr.Chatbot(
                label="LearnPiolet",
                show_label=False,
                type="messages",
                height=550,
                placeholder=(
                    "Start learning with LearnPiolet..."
                ),
                show_copy_button=True,
                autoscroll=True
            )


            # --------------------------------------------------
            # MESSAGE INPUT
            # --------------------------------------------------

            with gr.Row():

                message_box = gr.Textbox(
                    placeholder=(
                        "Ask LearnPiolet anything..."
                    ),
                    show_label=False,
                    scale=9,
                    autofocus=True
                )


                send_button = gr.Button(
                    "Send 🚀",
                    scale=1,
                    variant="primary",
                    elem_id="send-btn"
                )


    # ==================================================
    # SEND BUTTON
    # ==================================================

    send_button.click(
        chat_with_agent,

        inputs=[
            message_box,
            chatbot_ui,
            conversation_state
        ],

        outputs=[
            message_box,
            chatbot_ui,
            conversation_list
        ]
    )


    # ==================================================
    # ENTER KEY
    # ==================================================

    message_box.submit(
        chat_with_agent,

        inputs=[
            message_box,
            chatbot_ui,
            conversation_state
        ],

        outputs=[
            message_box,
            chatbot_ui,
            conversation_list
        ]
    )


    # ==================================================
    # NEW CONVERSATION
    # ==================================================

    new_chat_button.click(
        reset_chat,

        inputs=[],

        outputs=[
            chatbot_ui,
            conversation_list,
            conversation_state
        ]
    )


    # ==================================================
    # LOAD PREVIOUS CONVERSATION
    # ==================================================

    conversation_list.change(
        select_conversation,

        inputs=[
            conversation_list
        ],

        outputs=[
            chatbot_ui,
            conversation_state
        ]
    )


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    demo.launch(
        share=False
    )

