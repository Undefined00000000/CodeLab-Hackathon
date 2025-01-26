from flask import Flask, request, jsonify
from flask_limiter import Limiter
from functools import wraps
import logging
import re
from datetime import datetime

app = Flask(__name__)

# Set up secure logging
logging.basicConfig(
    filename='logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Mock data for users and roles
USER_ROLES = {
    "student_token": "student",
    "teacher_token": "teacher",
    "staff_token": "staff",
    "admin_token": "admin"
}

# Middleware for authentication and role validation
def auth_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get headers or request body
        auth_token = request.json.get("auth_token", "") if request.is_json else ""
        prompt = request.json.get("prompt", "") if request.is_json else ""

        # Validate user authentication
        if not auth_token or auth_token not in USER_ROLES:
            logging.warning("Unauthorized access attempt")
            return jsonify({"error": "Unauthorized access"}), 401

        # Assign user role
        role = USER_ROLES[auth_token]

        # Input validation for the prompt
        if not validate_prompt(prompt):
            logging.warning(f"Invalid input detected: {prompt}")
            return jsonify({"error": "Invalid input detected"}), 400

        # Log the request
        logging.info(f"Request received: Role={role}, Prompt={prompt}")

        # Add role and isAuthenticated to request context
        request.context = {"role": role, "isAuthenticated": 1}
        return func(*args, **kwargs)

    return wrapper

# Function to validate prompt (input validation)
def validate_prompt(prompt):
    return bool(re.match(r"^[a-zA-Z0-9\s\?\.\,]+$", prompt))

# API endpoint
@app.route("/api/chatbot", methods=["POST"])
@auth_middleware
def chatbot():
    context = request.context
    role = context["role"]
    is_authenticated = context["isAuthenticated"]

    print(role)
    print(is_authenticated)

    # Mock response based on role
    if role == "admin":
        response = "Welcome, admin. How can I assist you?"
    elif role == "student":
        response = "Hello, student. What do you need help with?"
    else:
        response = "Hello, anonymous user. Please log in for full access."

    return jsonify({
        "response": response,
    }), 200

if __name__ == "__main__":
    # Ensure app runs securely (HTTPS recommended for production)
    app.run(debug=True, port=5000)
