import os
from flask import Flask, render_template, request, jsonify
from astrapy.db import AstraDB  # Corrected import for the correct class
from collections import defaultdict
import requests

app = Flask(__name__)

# ------------------------
# Constants & Config
# ------------------------

class Config:
    ASTRA_DB_ID = "d6b8bd5b-3e9c-4084-8bb3-8f40f687310d"
    ASTRA_DB_REGION = "us-east1"
    ASTRA_DB_KEYSPACE = "default"
    APPLICATION_TOKEN = "AstraCS:NYGBBviIaFDSNlMYyddZvrzf:287fd88aa028ecdb6b90c91234277e5fcae4ba1cc4fb4e3e5ad8a50e3787bb99"
    GROQ_API_KEY = "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"
    GROQ_API_BASE = "https://api.groq.com"
    MODEL_NAME = "llama-3.1-8b-instant"
    API_ENDPOINT = f"https://{ASTRA_DB_ID}-{ASTRA_DB_REGION}.apps.astra.datastax.com"

# ------------------------
# Database Connection
# ------------------------

class DatabaseManager:
    def __init__(self):
        self.client = AstraDB(
            token=Config.APPLICATION_TOKEN,
            api_endpoint=Config.API_ENDPOINT
        )

    def query(self, collection, query):
     try:
        # Log the query being executed
        print(f"Executing query on {collection}: {query}")
        
        # Get the collection
        astra_collection = self.client.collection(collection)
        
        # Execute the query
        result = astra_collection.find(query)
        
        # Log the results
        print(f"Query result: {list(result)}")
        
        return list(result)
     except Exception as e:
        print(f"Database Query Error: {e}")
        return []


# ------------------------
# Message Management
# ------------------------

class MessageSender:
    USER = "user"
    AI = "ai"

class Message:
    def __init__(self, text, sender, sender_name=""):
        self.text = text
        self.sender = sender
        self.sender_name = sender_name

    def to_dict(self):
        return {
            "text": self.text,
            "sender": self.sender,
            "sender_name": self.sender_name,
        }

class MessageProperties:
    def __init__(self, background_color="#FFFFFF", text_color="#000000"):
        self.background_color = background_color
        self.text_color = text_color

    def to_dict(self):
        return {
            "background_color": self.background_color,
            "text_color": self.text_color,
        }

# ------------------------
# Chat Handler
# ------------------------

class ChatHandler:
    def __init__(self):
        self.db = DatabaseManager()
        self.messages = []

    def fetch_context(self, query: str) -> str:
        results = self.db.query('sample_data', {})
        print("Raw Query Results:", results)


    def store_message(self, message: Message):
        self.messages.append(message)

    def get_ai_response(self, prompt_text: str) -> str:
        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": Config.MODEL_NAME,
            "messages": [{"role": "system", "content": prompt_text}],
        }
        
        try:
            response = requests.post(
                f"{Config.GROQ_API_BASE}/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI API Error: {e}")
            return "I apologize, but I encountered an error processing your request."

    def analyze_social_media(self, message: str) -> dict:
        """
        Analyzes social media content for metrics, sentiment, and engagement potential.
        """
        analysis_data = {
            'metrics': {},
            'sentiment': {},
            'recommendations': []
        }
        
        # Calculate basic metrics
        analysis_data['metrics'] = {
            'character_count': len(message),
            'word_count': len(message.split()),
            'hashtag_count': message.count('#'),
            'mention_count': message.count('@'),
            'url_count': message.lower().count('http'),
            'emoji_count': sum(1 for char in message if ord(char) >= 0x1F600)
        }
        
        # Perform sentiment analysis
        positive_words = {'great', 'awesome', 'excellent', 'happy', 'love', 'amazing', 'wonderful'}
        negative_words = {'bad', 'poor', 'terrible', 'hate', 'awful', 'horrible', 'disappointing'}
        neutral_words = {'okay', 'fine', 'normal', 'average', 'decent'}
        
        words = set(message.lower().split())
        positive_count = len(words.intersection(positive_words))
        negative_count = len(words.intersection(negative_words))
        neutral_count = len(words.intersection(neutral_words))
        
        analysis_data['sentiment'] = {
            'positive_words': positive_count,
            'negative_words': negative_count,
            'neutral_words': neutral_count,
            'overall_sentiment': self._determine_sentiment(positive_count, negative_count, neutral_count)
        }
        
        # Generate engagement recommendations
        analysis_data['recommendations'] = self._generate_recommendations(analysis_data['metrics'])
        
        # Add engagement potential score
        analysis_data['engagement_score'] = self._calculate_engagement_score(analysis_data)
        
        return analysis_data

    def _determine_sentiment(self, pos_count, neg_count, neu_count) -> str:
        if pos_count > neg_count and pos_count > neu_count:
            return 'positive'
        elif neg_count > pos_count and neg_count > neu_count:
            return 'negative'
        return 'neutral'

    def _generate_recommendations(self, metrics) -> list:
        recommendations = []
        
        if metrics['character_count'] > 280:
            recommendations.append("Consider shortening the message for better engagement on Twitter")
        
        if metrics['hashtag_count'] == 0:
            recommendations.append("Add relevant hashtags to increase visibility")
        elif metrics['hashtag_count'] > 3:
            recommendations.append("Consider reducing number of hashtags to avoid appearing spammy")
            
        if metrics['url_count'] == 0:
            recommendations.append("Consider adding a relevant link for more information")
            
        if metrics['mention_count'] == 0:
            recommendations.append("Tag relevant accounts to increase reach")
            
        if metrics['emoji_count'] == 0:
            recommendations.append("Consider adding emojis to make your message more engaging")
        elif metrics['emoji_count'] > 4:
            recommendations.append("Consider reducing the number of emojis used")
            
        return recommendations

    def _calculate_engagement_score(self, analysis_data) -> float:
        """Calculate an engagement potential score from 0-100"""
        score = 50  # Start at neutral
        
        # Adjust based on metrics
        metrics = analysis_data['metrics']
        if 100 <= metrics['character_count'] <= 200:
            score += 10
        if 1 <= metrics['hashtag_count'] <= 3:
            score += 10
        if metrics['url_count'] == 1:
            score += 5
        if 1 <= metrics['emoji_count'] <= 3:
            score += 5
            
        # Adjust based on sentiment
        sentiment = analysis_data['sentiment']
        if sentiment['overall_sentiment'] == 'positive':
            score += 10
        elif sentiment['overall_sentiment'] == 'negative':
            score -= 5
            
        return min(max(score, 0), 100)  # Ensure score stays between 0-100

# ------------------------
# Initialize Handlers
# ------------------------

chat_handler = ChatHandler()

# ------------------------
# Routes
# ------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data['message']

        # Store user message
        user_message_obj = Message(
            text=user_message,
            sender=MessageSender.USER,
            sender_name="User"
        )
        chat_handler.store_message(user_message_obj)

        # Get context and AI response
        context = chat_handler.fetch_context(user_message)
        prompt = f"{context}\nUser: {user_message}\nAI:"
        ai_response_text = chat_handler.get_ai_response(prompt)

        # Store and return AI response
        ai_message = Message(
            text=ai_response_text,
            sender=MessageSender.AI,
            sender_name="AI Assistant"
        )
        chat_handler.store_message(ai_message)

        return jsonify({"response": ai_message.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
            
        analysis_data = chat_handler.analyze_social_media(data['message'])
        return jsonify({"analysis_data": analysis_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Error Handlers
# ------------------------

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ------------------------
# Run the App
# ------------------------

if __name__ == '__main__':
    app.run(debug=True)
