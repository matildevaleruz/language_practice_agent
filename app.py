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

    data = request.json
    session_id = str(uuid.uuid4()) #random id

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

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    
    data = request.json
    user_text = data.get('text')
    
    #convert history into a text string to pass it in the prompt
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

@app.route('/finish-session', methods=['POST'])
def finish_session():
    data = request.json
    session_id = data.get('session_id')
    
    # get all history as string to pass in the prompt
    conversation_json_str = json.dumps(conversation_history, ensure_ascii=False)

    feedback_str = feedback_chain.invoke({
        'language': session_settings['language'],
        'level': session_settings['level'],
        'focus': session_settings['focus'],
        'context': session_settings['context'],
        'conversation_json': conversation_json_str
    })
    
    feedback = json.loads(feedback_str[7:-3]) # removes markdown ```json (...)``` to return the json object itself"
   
    save_conversation(session_id, session_settings, conversation_history, feedback)

    return jsonify({
        'feedback': feedback,
        'saved': True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
