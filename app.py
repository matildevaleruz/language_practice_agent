import uuid
import json
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from langchain_setup import conversation_chain, feedback_chain

from database import save_conversation

load_dotenv()

app = Flask(__name__)

# current session variables
session_settings = {}
conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-session', methods=['POST'])
def start_session():
    global session_settings
    global conversation_history
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        session_id = str(uuid.uuid4())  # random id

        session_settings = {
            'language': data.get('language'),
            'level': data.get('level'),
            'focus': data.get('focus'),
            'context': data.get('context'),
        }

        # Initial assistant message
        initial_prompt = "Start the conversation."
        assistant_message = conversation_chain.invoke({
            'language': session_settings['language'],
            'level': session_settings['level'],
            'focus': session_settings['focus'],
            'context': session_settings['context'],
            'history': "",
            'text': initial_prompt
        })

        # save to history list
        conversation_history = [{'user': initial_prompt, 'assistant': assistant_message}]

        return jsonify({
            'session_id': session_id,
            'assistant_message': assistant_message
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start session: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_text = data.get('text')
        if not user_text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not session_settings:
            return jsonify({'error': 'Session not started'}), 400
        
        # convert history into a text string to pass it in the prompt
        history_str = "\n".join([f"User: {turn['user']}\nAssistant: {turn['assistant']}" for turn in conversation_history])

        assistant_message = conversation_chain.invoke({
            'language': session_settings['language'],
            'level': session_settings['level'],
            'focus': session_settings['focus'],
            'context': session_settings['context'],
            'history': history_str,
            'text': user_text
        })
        
        # add to the history list
        conversation_history.append({'user': user_text, 'assistant': assistant_message})

        return jsonify({
            'assistant_message': assistant_message,
            'turn_index': len(conversation_history)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to process chat: {str(e)}'}), 500

@app.route('/finish-session', methods=['POST'])
def finish_session():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if not conversation_history:
            return jsonify({'error': 'No conversation history to save'}), 400
        
        # get all history as string to pass in the prompt
        conversation_json_str = json.dumps(conversation_history, ensure_ascii=False)

        feedback_str = feedback_chain.invoke({
            'language': session_settings['language'],
            'level': session_settings['level'],
            'focus': session_settings['focus'],
            'context': session_settings['context'],
            'conversation_json': conversation_json_str
        })
        
        # Try to parse the feedback, handle potential JSON parsing errors
        try:
            feedback = json.loads(feedback_str[7:-3])  # removes markdown ```json (...)``` to return the json object itself
        except (json.JSONDecodeError, IndexError) as e:
            # If parsing fails, return the raw feedback string
            feedback = {"raw_feedback": feedback_str, "parse_error": str(e)}
       
        save_conversation(session_id, session_settings, conversation_history, feedback)

        return jsonify({
            'feedback': feedback,
            'saved': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to finish session: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)