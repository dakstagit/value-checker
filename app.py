from flask import Flask, request, render_template
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        product = request.form['product']
        price = request.form['price']
        prompt = f"""
Evaluate if the following product is value for money in India.
Product: {product}
Listed Price: ₹{price}
Please consider:
1. Global average price (converted to INR)
2. Estimated production cost
3. Comparable alternatives in Indian market
4. Final verdict with a rating (e.g., Excellent / Good / Average / Poor Value)
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        result = response['choices'][0]['message']['content']
    return render_template('index.html', result=result)
    
# REQUIRED for Render to work
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
