 # 🚀 LearnPiolet — Personalized AI Learning Agent

An agentic AI learning assistant built with the Groq LLM and Gradio. LearnPiolet helps students learn technical topics through personalized explanations, quizzes, study plans, memory, and conversational learning.

## ✨ Features

* 🤖 Agent-based learning workflow
* 🧭 Planner decides the action: `EXPLAIN` / `QUIZ` / `PLAN` / `MEMORY` / `CHAT`
* 📚 Topic explanation tool
* 📝 Quiz generation tool
* 📅 Personalized study-plan generator
* 🧠 Student memory and state management
* 💬 Context-aware conversations
* 🗄️ SQLite database for conversation data
* ⚠️ Error handling and test cases
* 💻 ChatGPT-style Gradio web interface
* ⌨️ Analyzing indicator and live typing experience

## 🛠️ Technologies Used

* Python
* Groq LLM
* Gradio
* SQLite
* python-dotenv

## 📁 Project Structure

```text
LearnPiolet/
│
├── app.py              # Main chatbot and Gradio UI
├── agent.py            # Agent, planner, context, and test logic
├── tools.py            # Groq client and learning tools
├── memory.py           # Student memory and state management
├── database.py         # SQLite database operations
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── .gitignore          # Files excluded from Git
└── README.md           # Project documentation
```

## 🚀 Setup

### 1. Create a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The `.env` file should **never be uploaded to GitHub**.

### 4. Run LearnPiolet

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:7860
```

### 5. Run the test cases

```bash
python agent.py
```

## 💡 Demo Prompts

Try prompts such as:

1. `Explain Python decorators`
2. `Give me a quiz on Python functions`
3. `Show my progress`
4. `Create a study plan for Python decorators`
5. `Hello, how are you?`

## 🎯 Project Goal

LearnPiolet is designed to provide students with a personalized AI learning experience by combining agentic planning, learning tools, student memory, and conversational interaction in a single application.

## 🔮 Future Improvements

* Learning progress analytics
* More educational tools
* Improved personalization
* More subject-specific learning workflows
* Deployment for students to access the application online
