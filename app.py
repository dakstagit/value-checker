from flask import Flask, request, render_template, Response, jsonify
import openai
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# Initialize the OpenAI client once
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except openai.AuthenticationError:
    print("Authentication failed. Please check your OPENAI_API_KEY.")
    client = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product = request.form.get('product')
        price = request.form.get('price')
        category = request.form.get('category')
        country = request.form.get('country')
        user_score = request.form.get('user_score')

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

            prompt = f"""
            You are a Value-for-Money AI Analyst. Your task is to evaluate a product and provide a comprehensive, independent analysis.

            Product Name: {product}
            Listed Price: {price} {currency}
            Category: {category}
            Market: {country}
            User's Perceived Rating: {user_score}/5

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
                    model="gpt-4o-mini", # Using gpt-4o-mini for better performance and cost-effectiveness
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    temperature=0.3
                )
                full_response = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    full_response += content
                    yield content
                
            except openai.APIError as e:
                print(f"OpenAI API Error: {e}")
                yield json.dumps({"error": f"API Error: {e}"})
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                yield json.dumps({"error": f"An unexpected error occurred: {e}"})

        return Response(generate_stream(), mimetype='application/json')
    
    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
