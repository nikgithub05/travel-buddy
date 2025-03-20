from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import requests
import schedule
import time
import threading
import logging
import re
import random

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable CORS for specific origin (React app) and allow credentials
CORS(app, resources={r"/*": {
    "origins": "http://localhost:3000",
    "supports_credentials": True,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH', r'D:\PRATHMESH NIKAM\Downloads\VS\trip-planner\database\travelbuddy\travel-buddy-e2cb5-firebase-adminsdk-fbsvc-10c48a13fd.json'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# LOCAL DATABASE I.E USER.DB FILE KA INSTERACTION START
# Initialize local database, this for storing the data locally 
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
        
        # Add logs table
        conn.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY,
                        message TEXT NOT NULL,
                        level TEXT NOT NULL,
                        timestamp DATETIME NOT NULL)''')
    logger.info("Database initialized.")

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
        logger.info(f"User {username} registered successfully in local DB!")
        return True
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity Error: {e}")
        return False
    except Exception as e:
        logger.error(f"General Error: {e}")
        return False

# Function to check if user exists in local database
def check_user_exists_local(email, phone):
    try:
        user = query_db("SELECT * FROM users WHERE email = ? OR phone = ?", (email, phone), one=True)
        return user is not None
    except Exception as e:
        logger.error(f"Error checking user existence in local DB: {e}")
        return False
    
# LOCAL DATABASE I.E USER.DB FILE KA INSTERACTION END

# FIREBASE INTERACTION START, INITIAL STAGE START

# Function to insert user data into Firebase Firestore
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
        logger.info(f"User {username} registered successfully in Firebase Firestore!")
        return True
    except Exception as e:
        logger.error(f"Error registering user in Firebase Firestore: {e}")
        return False

# Function to check if user exists in Firebase Authentication
def check_user_exists_firebase_auth(email):
    try:
        user_record = auth.get_user_by_email(email)
        return user_record is not None
    except auth.UserNotFoundError:
        return False
    except Exception as e:
        logger.error(f"Error checking user existence in Firebase Authentication: {e}")
        return False

# Function to check if user exists in Firebase Firestore
def check_user_exists_firebase(email, phone):
    try:
        users_ref = db.collection('users').where('email', '==', email).stream()
        for doc in users_ref:
            return True
        
        users_ref = db.collection('users').where('phone', '==', phone).stream()
        for doc in users_ref:
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking user existence in Firebase Firestore: {e}")
        return False

# FIREBASE INTERACTION START, INITIAL STAGE END

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
        
        logger.info(f"Trip preferences for user {user_id} saved successfully in local DB!")
        return True
    except Exception as e:
        logger.error(f"Error saving trip preferences in local DB: {e}")
        return False

# Function to save trip preferences to Firebase Firestore
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
        
        logger.info(f"Trip preferences for user {user_id} saved successfully in Firebase Firestore!")
        return True
    except Exception as e:
        logger.error(f"Error saving trip preferences in Firebase Firestore: {e}")
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
        logger.error(f"Error getting trip preferences from local DB: {e}")
        return None

# Function to get trip preferences for a user from Firebase Firestore
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
        logger.error(f"Error getting trip preferences from Firebase Firestore: {e}")
        return None

# Function to check internet connectivity
def is_connected():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Function to sync users from local to Firebase Firestore
def sync_users_to_firebase_firestore():
    users = query_db("SELECT * FROM users")
    for user in users:
        user_id, username, email, phone, password, created_at = user
        if not check_user_exists_firebase(email, phone):
            if insert_user_firebase(username, email, phone, password, created_at):
                logger.info(f"User {username} synced to Firebase Firestore!")
            else:
                logger.error(f"Failed to sync user {username} to Firebase Firestore")
        else:
            logger.info(f"User {username} already exists in Firebase Firestore.")

# Function to sync trip preferences from local to Firebase Firestore
def sync_trip_preferences_to_firebase_firestore():
    trip_prefs = query_db("SELECT * FROM trip_preferences")
    for pref in trip_prefs:
        id, user_id, destination, start_date, end_date, budget, activities_str, group_size, created_at = pref
        activities = activities_str.split(",")
        if not check_trip_preference_exists_firebase(user_id, created_at):
            if save_trip_preferences_firebase(user_id, destination, start_date, end_date, budget, activities, group_size):
                logger.info(f"Trip preferences for user {user_id} synced to Firebase Firestore!")
            else:
                logger.error(f"Failed to sync trip preferences for user {user_id} to Firebase Firestore")
        else:
            logger.info(f"Trip preferences for user {user_id} already exist in Firebase Firestore.")

# Function to check if trip preferences exist in Firebase Firestore
def check_trip_preference_exists_firebase(user_id, created_at):
    try:
        trip_prefs_ref = db.collection('trip_preferences').where('user_id', '==', user_id).where('created_at', '==', created_at).stream()
        for doc in trip_prefs_ref:
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking trip preference existence in Firebase Firestore: {e}")
        return False

# Function to sync users from Firebase Firestore to local
def sync_users_from_firebase_firestore():
    users_ref = db.collection('users').stream()
    for doc in users_ref:
        data = doc.to_dict()
        if not check_user_exists_local(data['email'], data['phone']):
            hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            hashed_phone = bcrypt.generate_password_hash(data['phone'].encode('utf-8')).decode('utf-8')
            if insert_user_local(data['username'], data['email'], hashed_phone, hashed_pw, data['created_at']):
                logger.info(f"User {data['username']} synced from Firebase Firestore to local DB!")
            else:
                logger.error(f"Failed to sync user {data['username']} from Firebase Firestore to local DB")
        else:
            logger.info(f"User {data['username']} already exists in local DB.")

# Function to sync trip preferences from Firebase Firestore to local
def sync_trip_preferences_from_firebase_firestore():
    trip_prefs_ref = db.collection('trip_preferences').stream()
    for doc in trip_prefs_ref:
        data = doc.to_dict()
        activities = data['activities'].split(",")
        if not check_trip_preference_exists_local(data['user_id'], data['created_at']):
            if save_trip_preferences_local(data['user_id'], data['destination'], data['start_date'], data['end_date'], data['budget'], activities, data['group_size']):
                logger.info(f"Trip preferences for user {data['user_id']} synced from Firebase Firestore to local DB!")
            else:
                logger.error(f"Failed to sync trip preferences for user {data['user_id']} from Firebase Firestore to local DB")
        else:
            logger.info(f"Trip preferences for user {data['user_id']} already exist in local DB.")

# Function to check if trip preferences exist in local database
def check_trip_preference_exists_local(user_id, created_at):
    try:
        result = query_db("SELECT * FROM trip_preferences WHERE user_id = ? AND created_at = ?", (user_id, created_at), one=True)
        return result is not None
    except Exception as e:
        logger.error(f"Error checking trip preference existence in local DB: {e}")
        return False

# Function to log messages to both local and Firebase Firestore
def log_message(message, level):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Log to local database
    try:
        query_db("INSERT INTO logs (message, level, timestamp) VALUES (?, ?, ?)", (message, level, timestamp))
        logger.info(f"Log '{message}' stored in local DB.")
    except Exception as e:
        logger.error(f"Error storing log in local DB: {e}")
    
    # Log to Firebase Firestore
    try:
        log_ref = db.collection('logs').document(timestamp)
        log_ref.set({
            'message': message,
            'level': level,
            'timestamp': timestamp
        })
        logger.info(f"Log '{message}' stored in Firebase Firestore.")
    except Exception as e:
        logger.error(f"Error storing log in Firebase Firestore: {e}")

# Function to perform full sync
def full_sync():
    if is_connected():
        logger.info("Internet connection detected. Starting sync...")
        sync_users_to_firebase_firestore()
        sync_trip_preferences_to_firebase_firestore()
        sync_users_from_firebase_firestore()
        sync_trip_preferences_from_firebase_firestore()
        logger.info("Sync completed.")
    else:
        logger.info("No internet connection. Skipping sync.")

# Schedule the sync function to run every 5 minutes
schedule.every(5).minutes.do(full_sync)

# Background thread to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Placeholder for API interaction
def fetch_external_itinerary(destination, start_date, end_date, budget, activities, group_size):
    # Replace with actual API call
    # Example:
    # response = requests.get('https://external-api.com/itinerary', params={
    #     'destination': destination,
    #     'start_date': start_date,
    #     'end_date': end_date,
    #     'budget': budget,
    #     'activities': ','.join(activities),
    #     'group_size': group_size
    # })
    # return response.json()
    
    # For now, return None to indicate no external API response
    return None

# Function to generate a dynamic itinerary based on user preferences
def generate_dynamic_itinerary(destination, start_date, end_date, budget, activities, group_size):
    # Parse dates
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate number of days
    num_days = (end_date - start_date).days + 1
    
    # Define possible activities
    possible_activities = {
        'Hiking': f"Hike in {destination}",
        'Beach': f"Relax at the beach in {destination}",
        'City Tour': f"Explore the city in {destination}",
        'Adventure': f"Try adventure activities in {destination}",
        'Relaxation': f"Relax and unwind in {destination}"
    }
    
    # Create a basic itinerary
    itinerary = []
    for day in range(1, num_days + 1):
        # Randomly select activities for the day
        day_activities = random.sample(list(possible_activities.values()), min(len(activities), 3))
        
        # Distribute activities throughout the day
        morning_activity = day_activities[0] if day_activities else "Free morning"
        afternoon_activity = day_activities[1] if len(day_activities) > 1 else "Free afternoon"
        evening_activity = day_activities[2] if len(day_activities) > 2 else "Free evening"
        
        itinerary.append({
            "day": day,
            "morning": morning_activity,
            "afternoon": afternoon_activity,
            "evening": evening_activity
        })
    
    return {
        "destination": destination,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "budget": budget,
        "group_size": group_size,
        "activities": activities,
        "itinerary": itinerary
    }

# Signup Route
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    logger.info("Received signup data: %s", data)

    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not (username and email and phone and password):
        logger.error("Missing required fields in signup data")
        return jsonify({"error": "All fields are required!"}), 400

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        logger.error("Invalid email format in signup data")
        return jsonify({"error": "Invalid email format!"}), 400

    # Validate phone number format (simple example)
    if not re.match(r"^\d{10}$", phone):
        logger.error("Invalid phone number format in signup data")
        return jsonify({"error": "Invalid phone number format!"}), 400

    # Check if user already exists in local DB or Firebase Authentication
    if check_user_exists_local(email, phone) or check_user_exists_firebase_auth(email):
        logger.error(f"User with email {email} or phone {phone} already exists")
        return jsonify({"error": "User already exists!"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    hashed_phone = bcrypt.generate_password_hash(phone.encode('utf-8')).decode('utf-8')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create user in Firebase Authentication
    try:
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        logger.info(f"User {username} registered successfully in Firebase Authentication!")
    except auth.EmailAlreadyExistsError:
        logger.error(f"User with email {email} already exists in Firebase Authentication")
        return jsonify({"error": "User already exists in Firebase Authentication!"}), 400
    except Exception as e:
        logger.error(f"Error registering user in Firebase Authentication: {e}")
        return jsonify({"error": f"Error registering user in Firebase Authentication: {str(e)}"}), 500

    # Insert user data into local database
    try:
        user_inserted_local = insert_user_local(username, email, hashed_phone, hashed_pw, created_at)
    except Exception as e:
        logger.error(f"Error inserting user into local DB: {e}")
        return jsonify({"error": f"Error inserting user into local DB: {str(e)}"}), 500

    # Insert user data into Firebase Firestore
    try:
        user_inserted_firebase = insert_user_firebase(username, email, hashed_phone, hashed_pw, created_at)
    except Exception as e:
        logger.error(f"Error inserting user into Firebase Firestore: {e}")
        return jsonify({"error": f"Error inserting user into Firebase Firestore: {str(e)}"}), 500

    if user_inserted_local and user_inserted_firebase:
        log_message(f"User {username} registered successfully", "INFO")
        return jsonify({"message": "User registered successfully!", "user_registered": True}), 201
    else:
        log_message(f"Failed to register user {username}", "ERROR")
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
        logger.error("Missing required fields in login data")
        return jsonify({"error": "Email and password are required!"}), 400

    user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)
    if user and bcrypt.check_password_hash(user[4], password):
        log_message(f"User {user[1]} logged in successfully", "INFO")
        return jsonify({"message": "Login successful!", "username": user[1], "user_id": user[0]}), 200
    else:
        log_message(f"Failed login attempt for email {email}", "WARNING")
        return jsonify({"error": "Invalid credentials!"}), 401

# Save Trip Preferences Route
@app.route('/api/save-trip-preferences', methods=['POST'])
def save_preferences():
    data = request.json
    logger.info("Received trip preference data: %s", data)

    user_id = data.get('user_id')
    destination = data.get('destination')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    activities = data.get('activities')
    group_size = data.get('group_size')

    if not all([user_id, destination, start_date, end_date, budget, activities, group_size]):
        logger.error("Missing required fields in trip preferences data")
        return jsonify({"error": "All fields are required!"}), 400

    # Save trip preferences to both local and Firebase Firestore databases
    saved_local = save_trip_preferences_local(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )
    saved_firebase = save_trip_preferences_firebase(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )

    if saved_local and saved_firebase:
        log_message(f"Trip preferences for user {user_id} saved successfully", "INFO")
        # Return the saved preferences
        preferences = get_trip_preferences_firebase(user_id)
        return jsonify({"message": "Preferences saved successfully!", "preferences": preferences}), 201
    else:
        log_message(f"Failed to save trip preferences for user {user_id}", "ERROR")
        return jsonify({"error": "Failed to save preferences"}), 500

# Get Trip Preferences Route
@app.route('/api/trip-preferences/<int:user_id>', methods=['GET'])
def get_preferences(user_id):
    preferences = get_trip_preferences_firebase(user_id)
    
    if preferences:
        log_message(f"Retrieved trip preferences for user {user_id}", "INFO")
        return jsonify(preferences), 200
    else:
        log_message(f"No trip preferences found for user {user_id}", "WARNING")
        return jsonify({"error": "No preferences found for this user"}), 404

# Generate Itinerary Route
@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    data = request.json
    logger.info("Received itinerary data: %s", data)
    
    # First, save the preferences to both local and Firebase Firestore databases
    user_id = data.get('user_id')
    destination = data.get('destination')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    activities = data.get('activities')
    group_size = data.get('group_size')

    if not all([user_id, destination, start_date, end_date, budget, activities, group_size]):
        logger.error("Missing required fields in itinerary data")
        return jsonify({"error": "All fields are required!"}), 400

    # Save trip preferences to both local and Firebase Firestore databases
    saved_local = save_trip_preferences_local(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )
    saved_firebase = save_trip_preferences_firebase(
        user_id, destination, start_date, end_date, budget, activities, group_size
    )

    if not saved_local or not saved_firebase:
        log_message(f"Failed to save trip preferences for user {user_id}", "ERROR")
        return jsonify({"error": "Failed to save preferences"}), 500

    # Try to fetch itinerary from external API
    external_itinerary = fetch_external_itinerary(destination, start_date, end_date, budget, activities, group_size)
    
    if external_itinerary:
        return jsonify(external_itinerary), 200

    # If external API fails, generate a dynamic itinerary
    itinerary = generate_dynamic_itinerary(destination, start_date, end_date, budget, activities, group_size)

    return jsonify(itinerary), 200

# Forgot Password Route
@app.route('/api/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return '', 200  # Handle preflight request

    data = request.json
    logger.info("Received forgot password data: %s", data)

    email = data.get('email')

    if not email:
        logger.error("Missing required fields in forgot password data")
        return jsonify({"error": "Email is required!"}), 400

    try:
        # Generate password reset link using Firebase Authentication
        logger.info(f"Attempting to send password reset email to {email}")

        action_code_settings = auth.ActionCodeSettings(
            url="http://localhost:3000/reset-password",
            handle_code_in_app=False
        )

        auth.send_password_reset_email(email, action_code_settings)
        logger.info(f"Password reset email sent to {email}")

        return jsonify({"message": "Password reset email sent successfully!"}), 200
    except auth.EmailNotFoundError:
        logger.error(f"Email {email} not found in Firebase Authentication")
        return jsonify({"error": "Email not found in Firebase Authentication!"}), 404
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        return jsonify({"error": "Failed to send password reset email."}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
