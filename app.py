from flask import Flask, request, jsonify, render_template
from astrapy import DataAPIClient
import os
from dotenv import load_dotenv
from flask_cors import CORS


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for the app
CORS(app)

# Configuration for DataStax Astra DB from .env file
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
ASTRA_DB_URL = os.getenv("ASTRA_DB_URL")
ASTRA_KEYSPACE = os.getenv("ASTRA_KEYSPACE")

# Initialize Astra DB client
client = DataAPIClient(ASTRA_DB_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_DB_URL)

# Route for the home page
@app.route("/")
def index():
    return render_template("index.html")

# Route for analyzing social media performance
@app.route("/analyze", methods=["POST"])
def analyze():
    post_type = request.json.get("post_type")
    if not post_type:
        return jsonify({"error": "Post type is required"}), 400

    # Query Astra DB using collection
    collection = db[ASTRA_KEYSPACE]["engagement"]
    documents = collection.find({"post_type": post_type})

    # Calculate average metrics
    total_likes = total_shares = total_comments = count = 0
    for doc in documents:
        total_likes += doc.get("likes", 0)
        total_shares += doc.get("shares", 0)
        total_comments += doc.get("comments", 0)
        count += 1

    if count == 0:
        return jsonify({"error": "No data available for the specified post type"}), 404

    avg_likes = total_likes / count
    avg_shares = total_shares / count
    avg_comments = total_comments / count

    # Insights (mocking GPT integration here)
    insights = f"Post type '{post_type}' has an average of {avg_likes:.2f} likes, {avg_shares:.2f} shares, and {avg_comments:.2f} comments."

    return jsonify({
        "post_type": post_type,
        "average_likes": avg_likes,
        "average_shares": avg_shares,
        "average_comments": avg_comments,
        "insights": insights
    })

if __name__ == "__main__":
    app.run(debug=True)
