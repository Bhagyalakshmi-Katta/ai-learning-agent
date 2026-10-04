# memory.py
# Student memory + state management


class StudentMemory:

    def __init__(self):
        self.profile = {
            "name": None,
            "level": "beginner",
            "learning_style": "simple explanation"
        }

        self.progress = {
            "topics_studied": [],
            "topics_mastered": [],
            "quiz_scores": {}
        }

        self.current_state = {
            "current_topic": None,
            "difficulty": "beginner",
            "last_action": None
        }

    def update_profile(self, name=None, level=None, learning_style=None):

        if name:
            self.profile["name"] = name

        if level:
            self.profile["level"] = level

        if learning_style:
            self.profile["learning_style"] = learning_style

    def add_topic(self, topic):

        if topic not in self.progress["topics_studied"]:
            self.progress["topics_studied"].append(topic)

        self.current_state["current_topic"] = topic

    def add_score(self, topic, score):

        self.progress["quiz_scores"][topic] = score

        if score >= 80:
            if topic not in self.progress["topics_mastered"]:
                self.progress["topics_mastered"].append(topic)

    def set_action(self, action):

        self.current_state["last_action"] = action

    def show_memory(self):

        return {
            "profile": self.profile,
            "progress": self.progress,
            "current_state": self.current_state
        }
