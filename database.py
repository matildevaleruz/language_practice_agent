import os
import psycopg2
import json
from datetime import datetime, timezone

DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    try:
        if not DATABASE_URL:
            print("Warning: DATABASE_URL environment variable is not set")
            print("Database operations will fail. Please set DATABASE_URL in your .env file")
            return False
            
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
        print("Database initialized successfully")
        return True
        
    except psycopg2.Error as e:
        print(f"Database initialization error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during database initialization: {e}")
        return False

def save_conversation(session_id, session_settings, conversation_history, feedback):
    try:
        if not DATABASE_URL:
            print("Warning: Cannot save conversation - DATABASE_URL not set")
            return False
            
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Convert data to JSON strings
        conversation_json_str = json.dumps(conversation_history, ensure_ascii=False)
        feedback_json_str = json.dumps(feedback, ensure_ascii=False)

        sql = """
            INSERT INTO conversations (id, created, language, level, focus, context, conversation, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            session_id,
            datetime.now(timezone.utc),
            session_settings.get('language', ''),
            session_settings.get('level', ''),
            session_settings.get('focus', ''),
            session_settings.get('context', ''),
            conversation_json_str,
            feedback_json_str
        )

        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Conversation saved with ID: {session_id}")
        return True
        
    except psycopg2.Error as e:
        print(f"Database error saving conversation {session_id}: {e}")
        return False
    except json.JSONEncodeError as e:
        print(f"JSON encoding error for conversation {session_id}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving conversation {session_id}: {e}")
        return False