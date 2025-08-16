from flask import Flask, request, render_template, Response, jsonify
import openai
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except openai.AuthenticationError:
    print("Authentication failed. Please check your OPENAI_API_KEY.")
    client = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data received"}), 400

            product = data.get('product')
            price = data.get('price')
            category = data.get('category')
            country = data.get('country')
            user_score = data.get('user_score')
        except Exception as e:
            return jsonify({"error": f"Invalid JSON format: {e}"}), 400

        if not all([product, price, category, country, user_score]):
            return jsonify({"error": "Missing form data"}), 400

        currency = {
            "India": "INR",
            "United States": "USD",
            "United Kingdom": "GBP"
        }.get(country, "local currency")

        def generate_stream():
            if not client:
                yield json.dumps({"error": "API Key is not configured correctly."})
                return

            # Crucial prompt update: Tell the AI to ignore the user's rating
            prompt = f"""
            You are a Value-for-Money AI Analyst. Your task is to evaluate a product and provide a comprehensive, independent analysis.

            Product Name: {product}
            Listed Price: {price} {currency}
            Category: {category}
            Market: {country}

            The user's rating is {user_score}/5, but you must completely ignore this score. Base your evaluation *solely* on your independent analysis of market data.

            Your response must be a single JSON object. Do not include any text before or after the JSON.
            The JSON object must contain the following keys:
            "global_avg_price": A string with the global average price for this category, converted to {currency}.
            "production_cost": A string with the estimated production cost, in {currency}.
            "alternatives": A string with similar alternatives available in the selected market.
            "summary": A short, one-paragraph summary of your value-for-money reasoning and recommendation.
            "final_recommendation": A string formatted exactly like: 'BUY (Score: 4/5 – Good Value)'.
            "confidence_score": An integer representing your confidence in this analysis (1-100).
            """
            
            try:
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    temperature=0.3
                )
                
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    yield content
                
            except openai.APIError as e:
                yield json.dumps({"error": f"API Error: {e}"})
            except Exception as e:
                yield json.dumps({"error": f"An unexpected error occurred: {e}"})

        return Response(generate_stream(), mimetype='application/json')
    
    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
