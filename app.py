from flask import Flask, request
from flask_cors import CORS
from userdb import userdb_bp
from preference import preference_bp
from flask_bcrypt import Bcrypt
from ai_service import ai_bp 

app = Flask(__name__)

# Flask secret key (for sessions, JWT, etc.)
app.config['SECRET_KEY'] = 'yoyomyboi'

# Enable CORS globally with credentials support
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Initialize bcrypt with app
bcrypt = Bcrypt(app)

# Registering blueprints
app.register_blueprint(userdb_bp, url_prefix='/api')
app.register_blueprint(preference_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api') 

# Ensure OPTIONS method is allowed for preflight requests
@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        return '', 200

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
