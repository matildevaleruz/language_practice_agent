# Language Conversation Partner API

This project is a Flask-based web application that acts as a conversational partner for language learners. It uses AI to simulate conversations and provide feedback, helping users practice a new language.

## Features

- **Interactive Conversation:** Engage in a text-based conversation with an AI in your target language.
- **Customizable Sessions:** Choose the language, your proficiency level (CEFR), the learning focus and the topic of conversation.
- **AI-Powered Feedback:** Receive detailed feedback on your conversation, including corrections, strengths, weaknesses, and recommendations.
- **Session History:** All conversations are saved to a database for review.
- **Flexible AI Model:** Easily switch AI models via OpenRouter integration.

## How It Works

The system orchestrates a single AI model through three distinct phases, using two specialized prompts to simulate a complete practice session.

1. Conversation Initiation: The AI adopts the "Practice Partner" role. Using the Conversation Prompt, it processes the user's settings (language, level, scenario) and generates a contextually appropriate opening line in the target language.

2. Sustained Dialogue: The AI maintains the "Practice Partner" role. The same Conversation Prompt now receives the full message history with each exchange, allowing it to respond coherently and naturally, adapting the conversation's complexity to the user's stated level.

3. Feedback Generation: The AI switches to the "Tutor" role. A separate Feedback Prompt analyzes the complete conversation against the user's original learning objectives. It then generates structured feedback, highlighting corrections, strengths, and personalized recommendations.

Core Design Principle: Separating the conversational and analytical functions into distinct prompts ensures the AI excels at both natural dialogue and objective, targeted evaluation without task confusion.

## Project Structure

```
/api_project
|-- app.py                  # Main Flask application
|-- database.py             # Database connection and functions
|-- langchain_setup.py      # LLM, prompts, and chain configurations
|-- init_db.py              # Script to initialize the database
|-- requirements.txt        # Python dependencies
|-- .env.example            # Example environment variables
|-- static/                 # CSS and JavaScript files
|-- templates/              # HTML templates
|-- tests/                  # Pytest test files
`-- README.md
```

## Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

- Python 3.8+
- `pip` for package management

### 2. Clone the Repository

```bash
git clone <repository-url>
cd api_project
```

### 3. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Install all required packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the root of the project by copying the `.env.example` file.

```bash
cp .env.example .env
```

Now, edit the `.env` file with your specific configuration:

```
# .env

# --- Database ---
# URL for your PostgreSQL database
DATABASE_URL="postgresql://user:password@host:port/dbname"

# --- AI Model (OpenRouter) ---
# Your OpenRouter API Key
OPENROUTER_API_KEY="your_openrouter_api_key"

# The base URL for the OpenRouter API
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"

# The specific model you want to use (e.g., mistralai/mistral-7b-instruct:free)
OPENROUTER_MODEL="mistralai/mistral-7b-instruct:free"
```

### 6. Initialize the Database

Run the `init_db.py` script once to create the necessary tables in your database.

```bash
python init_db.py
```

## Running the Application

Once the setup is complete, you can start the Flask web server.

```bash
python app.py
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

The application exposes the following REST API endpoints:

- **`GET /`**
  - **Description:** Renders the main web interface.

- **`POST /start-session`**
  - **Description:** Starts a new conversation session.
  - **Request Body:**
    ```json
    {
      "language": "French",
      "level": "A2",
      "focus": "Vocabulary",
      "context": "At a restaurant"
    }
    ```
  - **Response:**
    ```json
    {
      "session_id": "[unique-session-id]",
      "assistant_message": "Bonjour! Que voulez-vous commander?"
    }
    ```

- **`POST /chat`**
  - **Description:** Sends a user message and gets the AI's response.
  - **Request Body:**
    ```json
    {
      "text": "Je voudrais un croissant."
    }
    ```
  - **Response:**
    ```json
    {
      "assistant_message": "Très bien. Et à boire?",
      "turn_index": 2
    }
    ```

- **`POST /finish-session`**
  - **Description:** Ends the current session, saves it to the database, and gets feedback.
  - **Request Body:**
    ```json
    {
      "session_id": "the-session-id-from-start-session"
    }
    ```
  - **Response:**
    ```json
    {
      "feedback": {
        "corrections": [...],
        "strengths": [...],
        "weaknesses": [...],
        "recommendations": [...]
      },
      "saved": true
    }
    ```

## Running Tests

This project uses `pytest` for testing.

### 1. Install Testing Dependencies

If you haven't already, install pytest:
```bash
pip install pytest
```

### 2. Run the Test Suite

To run all tests, execute the following command from the root directory:

```bash
pytest
```

## A Note from the Developer

Language learning isn't just about vocabulary or grammar—it's about connection, confidence, and accessing new worlds. This project was born from a belief that everyone should have access to a patient, judgment-free space to practice speaking, anytime. It's a small step toward making language practice more human, even when it's powered by a machine.
