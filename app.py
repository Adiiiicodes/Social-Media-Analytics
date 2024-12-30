from flask import Flask, request, jsonify, render_template
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

app = Flask(__name__)

# Configuration for DataStax Astra DB
ASTRA_DB_CLIENT_ID = "your-client-id"
ASTRA_DB_CLIENT_SECRET = "your-client-secret"
ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH = "path/to/your/secure-connect-database-name.zip"
ASTRA_KEYSPACE = "your-keyspace"

# Set up authentication and secure connect bundle
auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
cluster = Cluster(cloud={'secure_connect_bundle': ASTRA_DB_SECURE_CONNECT_BUNDLE_PATH}, auth_provider=auth_provider)
session = cluster.connect()
session.set_keyspace(ASTRA_KEYSPACE)

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

    # Query Astra DB
    query = f"SELECT likes, shares, comments FROM engagement WHERE post_type = '{post_type}'"
    rows = session.execute(query)

    # Calculate average metrics
    total_likes = total_shares = total_comments = count = 0
    for row in rows:
        total_likes += row.likes
        total_shares += row.shares
        total_comments += row.comments
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
