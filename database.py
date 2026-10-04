import sqlite3
from pathlib import Path


# Database will be stored inside the project
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "learnpiolet.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Stores different conversations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Stores messages inside conversations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    connection.commit()
    connection.close()


def create_conversation(title="New Conversation"):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )

    conversation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return conversation_id


def save_message(conversation_id, role, content):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (conversation_id, role, content)
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, content)
    )

    connection.commit()
    connection.close()


def get_conversations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, created_at
        FROM conversations
        ORDER BY created_at DESC
    """)

    conversations = cursor.fetchall()

    connection.close()

    return conversations


def get_messages(conversation_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
    """, (conversation_id,))

    messages = cursor.fetchall()

    connection.close()

    return messages
def update_conversation_title(conversation_id, title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title = ?
        WHERE id = ?
        """,
        (title, conversation_id)
    )

    connection.commit()
    connection.close()
def delete_empty_conversations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM conversations
        WHERE id NOT IN (
            SELECT DISTINCT conversation_id
            FROM messages
        )
    """)

    deleted_count = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted_count