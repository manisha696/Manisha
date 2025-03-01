from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Load API Key
load_dotenv()
GEMINI_API_KEY = "AIzaSyCgcazA5TaXPTLTGOoQGvtC4x6w9DSeQNs"

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found! Check your .env file.")

# ✅ Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialize Flask App
app = Flask(__name__)  # 🔹 Fixed: Correct `__name__`
app.secret_key = os.urandom(24)  # 🔹 Secure random secret key

# ✅ Store chat history in memory
chat_history_store = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_with_dharitri():
    """Handles user queries with chat history."""
    data = request.json
    query = data.get("query")
    user_id = request.remote_addr  # 🔹 Use IP as a temporary session identifier

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # ✅ Retrieve chat history (store per user)
    chat_history = chat_history_store.get(user_id, [])
    chat_history.append(f"User: {query}")

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # ✅ Fixed model name
        response = model.generate_content("\n".join(chat_history))

        # ✅ Ensure response is valid
        bot_reply = getattr(response, "text", "No response from Gemini")

        # ✅ Improve structured reply handling
        structured_reply = "\n".join(
            [f"{i+1}. {point.strip()}" for i, point in enumerate(bot_reply.split("\n")) if point]
        )

        # ✅ Update chat history
        chat_history.append(f"धरित्री: {structured_reply}")
        chat_history_store[user_id] = chat_history[-10:]  # 🔹 Keep only last 10 messages

        return jsonify({"bot_name": "धरित्री", "response": structured_reply, "chat_history": chat_history})
    
    except Exception as e:
        return jsonify({"bot_name": "धरित्री", "error": f"API Error: {str(e)}"})

@app.route("/clear", methods=["POST"])
def clear_chat():
    user_id = request.remote_addr
    chat_history_store.pop(user_id, None)
    return jsonify({"message": "Chat history cleared!"})

# ✅ Fixed main execution block
if __name__ == "__main__":
    app.run(debug=True)
