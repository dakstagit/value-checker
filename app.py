from flask import Flask, request, render_template
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        product = request.form['product']
        price = request.form['price']
        category = request.form['category']
        country = request.form['country']
        user_score = request.form['user_score']

        # Determine currency based on country
        currency = {
            "India": "INR",
            "United States": "USD",
            "United Kingdom": "GBP"
        }.get(country, "local currency")

        prompt = f"""
Evaluate whether the following product is value for money in the selected market.

Product Name: {product}
Listed Price: {price} {currency}
Category: {category}
Market: {country}

The user has rated this product {user_score}/5 based on their perception.

Please give your own independent rating based on data and your analysis only. Do NOT consider the user's rating while scoring.

Make sure:
- All price comparisons, cost estimates, and final recommendations are in the local currency of the selected market.
- Use INR for India, USD for United States, and GBP for United Kingdom.

Please include:
1. Global average price for this category (converted to {currency} if needed)
2. Estimated production cost
3. Similar alternatives available in the selected market
4. Provide a short paragraph summarizing your value-for-money reasoning and recommendation.
5. Give a confidence score (out of 100) indicating how confident you are in this evaluation.
6. End with a final recommendation formatted exactly like:
Final Recommendation: BUY (Score: 4/5 – Good Value)
Confidence Score: 86/100
"""


        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        result = response.choices[0].message.content

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
