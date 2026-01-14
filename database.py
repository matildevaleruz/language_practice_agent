import os
import psycopg2
import json
from datetime import datetime, timezone

DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            created TIMESTAMP,
            language TEXT,
            level TEXT,
            focus TEXT,
            context TEXT,
            conversation TEXT,
            feedback TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def save_conversation(session_id, session_settings, conversation_history, feedback):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    conversation_json_str = json.dumps(conversation_history, ensure_ascii=False)
    feedback_json_str = json.dumps(feedback, ensure_ascii=False)

    sql = """
        INSERT INTO conversations (id, created, language, level, focus, context, conversation, feedback)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        session_id,
        datetime.now(timezone.utc),
        session_settings['language'],
        session_settings['level'],
        session_settings['focus'],
        session_settings['context'],
        conversation_json_str,
        feedback_json_str
    )

    cursor.execute(sql, params)

    conn.commit()
    cursor.close()
    conn.close()
