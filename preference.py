from flask import Blueprint, request, jsonify
import sqlite3
from flask_cors import CORS

preference_bp = Blueprint('preference', __name__)

# Enable CORS with credentials for React app
CORS(preference_bp, resources={r"/api/generate-itinerary": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Initialize database for travel preferences
def init_db():
    with sqlite3.connect('user.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS preferences (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        destination TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        budget REAL NOT NULL,
                        activities TEXT NOT NULL,
                        group_size INTEGER NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    print("Preferences table initialized.")

init_db()

# Helper function to interact with database
def query_db(query, args=(), one=False):
    with sqlite3.connect('user.db') as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

# Route to handle travel preferences submission
@preference_bp.route('/generate-itinerary', methods=['POST', 'OPTIONS'])
def generate_itinerary():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    data = request.json
    print("Received data:", data)  # Debug the received data

    user_id = data.get('user_id')
    destination = data.get('destination')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    activities = ','.join(data.get('activities', []))
    
    # Handle the group_size field properly - store as string
    group_size = data.get('group_size')
    
    # Validate fields
    if not all([user_id, destination, start_date, end_date, budget, activities, group_size]):
        missing_fields = []
        if not user_id: missing_fields.append('user_id')
        if not destination: missing_fields.append('destination')
        if not start_date: missing_fields.append('start_date')
        if not end_date: missing_fields.append('end_date')
        if not budget: missing_fields.append('budget')
        if not activities: missing_fields.append('activities')
        if not group_size: missing_fields.append('group_size')
        
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        # Insert as string values where appropriate
        query_db('''INSERT INTO preferences (user_id, destination, start_date, end_date, budget, activities, group_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (user_id, destination, start_date, end_date, float(budget), activities, group_size))

        return jsonify({"message": "Preferences saved successfully!"}), 201

    except Exception as e:
        print("Error saving preferences:", str(e))
        return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500
