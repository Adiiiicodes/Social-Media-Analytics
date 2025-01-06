from flask import Flask, render_template, request, jsonify
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import requests
from dataclasses import dataclass
from enum import Enum

app = Flask(__name__)

class MessageSender(str, Enum):
    AI = "ai"
    USER = "user"

class Source(BaseModel):
    id: Optional[str] = None
    display_name: Optional[str] = None
    source: Optional[str] = None

class MessageProperties(BaseModel):
    source: Optional[Source] = None
    icon: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None

class Message(BaseModel):
    text: str
    sender: str = "user"
    sender_name: str = "User"
    session_id: Optional[str] = None
    flow_id: Optional[str] = None
    files: Optional[List[str]] = None
    properties: Optional[MessageProperties] = None

    @classmethod
    def from_template(cls, **kwargs):
        return cls(**kwargs)

class DataParser:
    @staticmethod
    def data_to_text(template: str, data: Union[List, Dict], sep: str = "\n") -> str:
        if isinstance(data, dict):
            return template.format(**data)
        elif isinstance(data, list):
            return sep.join(template.format(**item) if isinstance(item, dict) else str(item) for item in data)
        return str(data)

class ChatHandler:
    def __init__(self):
        self.messages = []
        self.groq_api_key = "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"
        self.groq_api_base = "https://api.groq.com"
        self.model_name = "llama-3.1-8b-instant"
        self.data_parser = DataParser()

    def store_message(self, message: Message) -> Message:
        self.messages.append(message.dict())
        return message

    def parse_data(self, data: Union[List, Dict], template: str = "{text}", sep: str = "\n") -> str:
        return self.data_parser.data_to_text(template, data, sep)

    def build_prompt(self, template: str, **kwargs) -> Message:
        text = template.format(**kwargs)
        return Message(text=text)

    def get_ai_response(self, user_message: str) -> str:
        url = f"{self.groq_api_base}/openai/v1/chat/completions"  # Fixed endpoint
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.1,
            "max_tokens": 1000
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")  # Debug logging
            return f"Error communicating with AI service: {str(e)}"
        except Exception as e:
            print(f"General Error: {str(e)}")  # Debug logging
            return f"An unexpected error occurred: {str(e)}"

    def analyze_social_media(self, message: str) -> Dict:
        # Placeholder for social media analysis logic
        # This would be replaced with actual analysis code
        return {
            "engagement_rate": 4.5,
            "likes": 1200,
            "comments": 45,
            "shares": 30,
            "sentiment": "positive"
        }

chat_handler = ChatHandler()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = Message(
        text=data['message'],
        sender=MessageSender.USER,
        sender_name="User",
        properties=MessageProperties(
            background_color="#FFE147",
            text_color="#000000"
        )
    )
    chat_handler.store_message(user_message)

    # Check if analysis is requested
    analysis_data = None
    if any(keyword in data['message'].lower() for keyword in ['analytics', 'stats', 'metrics']):
        analysis_data = chat_handler.analyze_social_media(data['message'])

    # Get AI response
    prompt = chat_handler.build_prompt(
        "{user_query}\n{context}",
        user_query=data['message'],
        context="Analyze this social media data: " + str(analysis_data) if analysis_data else ""
    )
    
    ai_response_text = chat_handler.get_ai_response(prompt.text)
    ai_message = Message(
        text=ai_response_text,
        sender=MessageSender.AI,
        sender_name="AI Assistant",
        properties=MessageProperties(
            background_color="#FF4D4D",
            text_color="#000000"
        )
    )
    chat_handler.store_message(ai_message)

    return jsonify({
        "response": ai_message.dict(),
        "should_show_viz": bool(analysis_data),
        "analysis_data": analysis_data
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(chat_handler.messages)

if __name__ == '__main__':
    app.run(debug=True)
