from dotenv import load_dotenv
from database import init_db

if __name__ == '__main__':
    load_dotenv() # Load environment variables from .env file
    print("Attempting to initialize database...")
    if init_db():
        print("Database initialization script finished.")
    else:
        print("Database initialization script failed.")
