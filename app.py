from flask import Flask, request, jsonify
import openai
import sqlite3
from flask_cors import CORS


app = Flask(__name__)
CORS(app)



# Configure OpenAI API key
# openai.api_key = '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'

# Function to create a database connection
def create_db_connection():
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    return conn, c

@app.route('/')
def index():
    return 'Welcome to the Stress Support Chatbot'

def generate_response(user_input):
    prompt_template = f"You are a mental support assistant. A user is feeling stressed and says: '{user_input}'. Provide immediate support and advice to help them manage their stress symptoms."
    completion = openai.Completion.create(
        engine="text-embedding-3-small",
        prompt=prompt_template,
        max_tokens=150
    )
    return completion.choices[0].text.strip()

@app.route('/support', methods=['POST'])
def support():
    user_input = request.json.get('message')
    response = generate_response(user_input)
    
    # Create a database connection within this thread
    conn, c = create_db_connection()
    
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS interactions
                (id INTEGER PRIMARY KEY AUTOINCREMENT, user_input text, response text)''')
    
    # Log interaction
    c.execute("INSERT INTO interactions (user_input, response) VALUES (?, ?)",
              (user_input, response))
    conn.commit()
    
    # Close the database connection
    conn.close()
    
    return jsonify({'response': response})


@app.route('/support', methods=['OPTIONS'])
def handle_options():
    return '', 200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }
if __name__ == '__main__':
    app.run(debug=True, port=5000)
