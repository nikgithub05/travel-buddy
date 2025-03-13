from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)

userdb_bp = Blueprint('userdb', __name__)

# Enable CORS for specific origin (React app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Initialize database
def init_db():
    with sqlite3.connect('user.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at DATETIME NOT NULL)''')
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
@userdb_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    print("Received data:", data)  # <-- Debug here

    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not (username and email and phone and password):
        return jsonify({"error": "All fields are required!"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        query_db("INSERT INTO users (username, email, phone, password, created_at) VALUES (?, ?, ?, ?, ?)",
                 (username, email, phone, hashed_pw, created_at))
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists!"}), 409

# Login Route
@userdb_bp.route('/api/login', methods=['POST', 'OPTIONS'])
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

# Register the blueprint
app.register_blueprint(userdb_bp)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
