import json
import pytest
from unittest.mock import patch
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200

@patch('app.conversation_chain.invoke')
def test_start_session(mock_invoke, client):
    """Test the start-session endpoint."""
    mock_invoke.return_value = "Hello! This is a test."
    
    response = client.post('/start-session',
                           data=json.dumps({
                               'language': 'English',
                               'level': 'B1',
                               'focus': 'Travel',
                               'context': 'At a hotel'
                           }),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'session_id' in data
    assert 'assistant_message' in data
    assert data['assistant_message'] == "Hello! This is a test."

@patch('app.conversation_chain.invoke')
def test_chat(mock_invoke, client):
    """Test the chat endpoint."""
    # First, start a session to populate global session_settings
    client.post('/start-session',
                data=json.dumps({
                    'language': 'English',
                    'level': 'B1',
                    'focus': 'Travel',
                    'context': 'At a hotel'
                }),
                content_type='application/json')

    mock_invoke.return_value = "That's a good question."
    
    response = client.post('/chat',
                           data=json.dumps({'text': 'What is your name?'}),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'assistant_message' in data
    assert 'turn_index' in data
    assert data['assistant_message'] == "That's a good question."

@patch('app.feedback_chain.invoke')
@patch('app.save_conversation')
def test_finish_session(mock_save_conversation, mock_invoke_feedback, client):
    """Test the finish-session endpoint."""
    # Start a session to ensure there's a history
    client.post('/start-session',
                data=json.dumps({
                    'language': 'English',
                    'level': 'B1',
                    'focus': 'Travel',
                    'context': 'At a hotel'
                }),
                content_type='application/json')
    
    feedback_data = {
        "corrections": [],
        "strengths": ["Good use of vocabulary."],
        "weaknesses": ["Some minor grammar mistakes."],
        "recommendations": ["Practice verb tenses."]
    }
    mock_invoke_feedback.return_value = f"```json\n{json.dumps(feedback_data)}\n```"

    response = client.post('/finish-session',
                           data=json.dumps({'session_id': 'some-test-id'}),
                           content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert 'feedback' in data
    assert 'saved' in data
    assert data['saved'] is True
    assert data['feedback'] == feedback_data
    mock_save_conversation.assert_called_once()