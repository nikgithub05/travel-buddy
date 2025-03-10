from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import sqlite3

# Create Blueprint
userdb_bp = Blueprint('userdb', __name__)
CORS(userdb_bp, supports_credentials=True)

bcrypt = Bcrypt()

# Enable CORS for specific origin (React app)
CORS(userdb_bp, supports_credentials=True)

# Initialize database
def init_db():
    with sqlite3.connect('user.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    print("Database initialized.")

init_db()

# Helper function to interact with database
def query_db(query, args=(), one=False):
    with sqlite3.connect('user.db') as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

# Signup Route
@userdb_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    print("Received data:", data)  # Debugging print

    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not (username and email and phone and password):
        return jsonify({"error": "All fields are required!"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        query_db("INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                 (username, email, phone, hashed_pw))
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists!"}), 409

# Login Route
@userdb_bp.route('/login', methods=['POST', 'OPTIONS'])
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
        return jsonify({"message": "Login successful!", "username": user[1]}), 200
    return jsonify({"error": "Invalid credentials!"}), 401
