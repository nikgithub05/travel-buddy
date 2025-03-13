from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Enable CORS for specific origin (React app) and allow credentials
CORS(app, resources={r"/*": {
    "origins": "http://localhost:3000",
    "supports_credentials": True,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'D:/PRATHMESH NIKAM/Downloads/VS/trip-planner/database/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize local database
def init_db():
    with sqlite3.connect('user.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at DATETIME NOT NULL)''')
        
        # Add trip_preferences table
        conn.execute('''CREATE TABLE IF NOT EXISTS trip_preferences (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        destination TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        budget TEXT NOT NULL,
                        activities TEXT NOT NULL,
                        group_size TEXT NOT NULL,
                        created_at DATETIME NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')
    print("Database initialized.")

# Call init_db when the app starts
init_db()

# Helper function to interact with local database
def query_db(query, args=(), one=False):
    with sqlite3.connect('user.db') as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

# Function to insert user data into the local database
def insert_user_local(username, email, phone, password, created_at):
    try:
        query_db("INSERT INTO users (username, email, phone, password, created_at) VALUES (?, ?, ?, ?, ?)",
                 (username, email, phone, password, created_at))
        print(f"User {username} registered successfully in local DB!")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity Error: {e}")
        return False
    except Exception as e:
        print(f"General Error: {e}")
        return False

# Function to save trip preferences to local database
def save_trip_preferences_local(user_id, destination, start_date, end_date, budget, activities, group_size):
    try:
        # Convert activities list to a comma-separated string
        activities_str = ",".join(activities)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query_db("""
            INSERT INTO trip_preferences 
            (user_id, destination, start_date, end_date, budget, activities, group_size, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            (user_id, destination, start_date, end_date, budget, activities_str, group_size, created_at))
        
        print(f"Trip preferences for user {user_id} saved successfully in local DB!")
        return True
    except Exception as e:
        print(f"Error saving trip preferences in local DB: {e}")
        return False

# Function to get trip preferences for a user from local database
def get_trip_preferences_local(user_id):
    try:
        result = query_db("SELECT * FROM trip_preferences WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", 
                        (user_id,), one=True)
        
        if result:
            # Unpack the result
            id, user_id, destination, start_date, end_date, budget, activities_str, group_size, created_at = result
            
            # Convert activities string back to list
            activities = activities_str.split(",")
            
            return {
                "user_id": user_id,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "activities": activities,
                "group_size": group_size
            }
        return None
    except Exception as e:
        print(f"Error getting trip preferences from local DB: {e}")
        return None

# Function to insert user data into Firebase
def insert_user_firebase(username, email, phone, password, created_at):
    try:
        user_ref = db.collection('users').document(email)
        user_ref.set({
            'username': username,
            'email': email,
            'phone': phone,
            'password': password,
            'created_at': created_at
        })
        print(f"User {username} registered successfully in Firebase!")
        return True
    except Exception as e:
        print(f"Error registering user in Firebase: {e}")
        return False

# Function to save trip preferences to Firebase
def save_trip_preferences_firebase(user_id, destination, start_date, end_date, budget, activities, group_size):
    try:
        # Convert activities list to a comma-separated string
        activities_str = ",".join(activities)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        trip_prefs_ref = db.collection('trip_preferences').document(f'{user_id}_{created_at}')
        trip_prefs_ref.set({
            'user_id': user_id,
            'destination': destination,
            'start_date': start_date,
            'end_date': end_date,
            'budget': budget,
            'activities': activities_str,
            'group_size': group_size,
            'created_at': created_at
        })
        
        print(f"Trip preferences for user {user_id} saved successfully in Firebase!")
        return True
    except Exception as e:
        print(f"Error saving trip preferences in Firebase: {e}")
        return False

# Function to get trip preferences for a user from Firebase
def get_trip_preferences_firebase(user_id):
    try:
        trip_prefs_ref = db.collection('trip_preferences').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(1).stream()
        
        for doc in trip_prefs_ref:
            data = doc.to_dict()
            # Convert activities string back to list
            activities = data['activities'].split(",")
            
            return {
                "user_id": data['user_id'],
                "destination": data['destination'],
                "start_date": data['start_date'],
                "end_date": data['end_date'],
                "budget": data['budget'],
                "activities": activities,
                "group_size": data['group_size']
            }
        return None
    except Exception as e:
        print(f"Error getting trip preferences from Firebase: {e}")
        return None

# Signup Route
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    print("Received data:", data)

    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not (username and email and phone and password):
        print("Missing required fields")
        return jsonify({"error": "All fields are required!"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    hashed_phone = bcrypt.generate_password_hash(phone.encode('utf-8')).decode('utf-8')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert user data into both local and Firebase databases
    user_inserted_local = insert_user_local(username, email, hashed_phone, hashed_pw, created_at)
    user_inserted_firebase = insert_user_firebase(username, email, hashed_phone, hashed_pw, created_at)

    if user_inserted_local and user_inserted_firebase:
        return jsonify({"message": "User registered successfully!", "user_registered": True}), 201
    else:
        return jsonify({"error": "An error occurred during registration.", "user_registered": False}), 500

# Login Route
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200  # Handle preflight request

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not (email and password):
        return jsonify({"error": "Email and password are required!"}), 400

    user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
    if user and bcrypt.check_password_hash(user[4], password):
        return jsonify({"message": "Login successful!", "username": user[1], "user_id": user[0]}), 200
    return jsonify({"error": "Invalid credentials!"}), 401

# Save Trip Preferences Route
@app.route('/api/save-trip-preferences', methods=['POST'])
def save_preferences():
    data = request.json
    print("Received trip preference data:", data)

    user_id = data.get('user_id')
    destination = data.get('destination')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    activities = data.get('activities')
    group_size = data.get('group_size')

    if not all([user_id, destination, start_date, end_date, budget, activities, group_size]):
        return jsonify({"error": "All fields are required!"}), 400

    # Save trip preferences to both local and Firebase databases
    saved_local = save_trip_preferences_local(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )
    saved_firebase = save_trip_preferences_firebase(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )

    if saved_local and saved_firebase:
        # Return the saved preferences
        preferences = get_trip_preferences_firebase(user_id)
        return jsonify({"message": "Preferences saved successfully!", "preferences": preferences}), 201
    else:
        return jsonify({"error": "Failed to save preferences"}), 500

# Get Trip Preferences Route
@app.route('/api/trip-preferences/<int:user_id>', methods=['GET'])
def get_preferences(user_id):
    preferences = get_trip_preferences_firebase(user_id)
    
    if preferences:
        return jsonify(preferences), 200
    else:
        return jsonify({"error": "No preferences found for this user"}), 404

# Placeholder for Generate Itinerary Route
@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    data = request.json
    print("Received itinerary data:", data)
    
    # First, save the preferences to both local and Firebase databases
    user_id = data.get('user_id')
    destination = data.get('destination')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    activities = data.get('activities')
    group_size = data.get('group_size')

    if not all([user_id, destination, start_date, end_date, budget, activities, group_size]):
        return jsonify({"error": "All fields are required!"}), 400

    # Save trip preferences to both local and Firebase databases
    saved_local = save_trip_preferences_local(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )
    saved_firebase = save_trip_preferences_firebase(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )

    if not saved_local or not saved_firebase:
        return jsonify({"error": "Failed to save preferences"}), 500

    # Placeholder for itinerary generation logic
    try:
        # Integrate with another API here
        # Example: itinerary = call_another_api(data)
        itinerary = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "group_size": group_size,
            "activities": activities,
            "itinerary": [
                {"day": 1, "morning": "Visit Museum", "afternoon": "Lunch at Café", "evening": "Dinner at Restaurant"},
                {"day": 2, "morning": "Hike in Park", "afternoon": "Shopping", "evening": "Relax at Beach"}
            ]
        }
        return jsonify(itinerary), 200
    except Exception as e:
        print(f"API Error: {e}")
        # Even though the API generation failed, we still return the saved preferences
        # with a partial success status
        preferences = get_trip_preferences_firebase(user_id)
        return jsonify({
            "error": str(e),
            "message": "Preferences saved, but itinerary generation failed.",
            "preferences": preferences
        }), 207  # 207 Multi-Status

if __name__ == '__main__':
    app.run(port=5000, debug=True)
