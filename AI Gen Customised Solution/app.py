from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# ✅ Load API Keys
load_dotenv()
GEMINI_API_KEY = "AIzaSyCgcazA5TaXPTLTGOoQGvtC4x6w9DSeQNs"
WEATHER_API_KEY = "3c3bbc5bc2392cce9b9ad50cdcec67f2"

# ✅ Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Function to fetch weather data
def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": data.get("rain", {}).get("1h", 0)
        }
    else:
        return None

# ✅ Route: Home Page
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Route: Fetch Weather Data
@app.route("/get_weather", methods=["POST"])
def fetch_weather():
    city = request.json.get("city")
    weather_data = get_weather_data(city)
    if weather_data:
        return jsonify(weather_data)
    return jsonify({"error": "Invalid city or API error"}), 400

# ✅ Route: Get Fertilizer Recommendation
@app.route("/recommend", methods=["POST"])
def recommend_fertilizer():
    data = request.json
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    rainfall = data.get("rainfall")
    npk_values = data.get("npk_values")
    soil_moisture = data.get("soil_moisture")

    prompt = f"""
    Given the following agricultural conditions:
    - Temperature: {temperature}°C
    - Humidity: {humidity}%
    - Rainfall: {rainfall} mm
    - Soil Moisture: {soil_moisture}%
    - NPK Ratio: {npk_values}

    Recommend the best fertilizer, application method, and precautions.
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    return jsonify({"recommendation": response.text})

# ✅ Run Flask App

    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5001, debug=True)

