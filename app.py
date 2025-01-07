from flask import Flask, render_template, request, jsonify
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import requests

app = Flask(__name__)

# Enum for message sender
class MessageSender(str, Enum):
    AI = "ai"
    USER = "user"

# Source model for message properties
class Source(BaseModel):
    id: Optional[str] = None
    display_name: Optional[str] = None
    source: Optional[str] = None

# Message properties such as colors and icons
class MessageProperties(BaseModel):
    source: Optional[Source] = None
    icon: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None

# Message model for sending and receiving messages
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

# DataParser for formatting data into text
class DataParser:
    @staticmethod
    def data_to_text(template: str, data: Union[List, Dict], sep: str = "\n") -> str:
        if isinstance(data, dict):
            return template.format(**data)
        elif isinstance(data, list):
            return sep.join(template.format(**item) if isinstance(item, dict) else str(item) for item in data)
        return str(data)

# ChatHandler to manage conversation logic
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

    def build_prompt(self, template: str, context: str, **kwargs) -> Message:
        kwargs = defaultdict(lambda: "", kwargs)
        kwargs["context"] = context
        text = template.format_map(kwargs)
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
    
    # Build context and get AI response
    context = """Content_Type\tTheme_Colors\tLikes\tComments\tViews\tPlatform\tPersonality\tField\tDate\tPublic_Sentiment\tChannel\tDislikes\tTheme
    Podcast\tStudio Setup\t10K\t917\t367k\tYoutube\tCycle Baba\tCyclist\t02-Jan-25\tPositive\tBeerBiceps\t161\t
    Podcast\tStudio Setup\t51K\t2.6K\t2.2M\tYoutube\tKriti Sanon\tActress\t28-Dec-24\tNegative\tBeerBiceps\t693\t
    Podcast\tStudio Setup\t37K\t2.5K\t1.2M\tYoutube\tAP Dhillon\tSinger\t25-Dec-24\tNegative\tBeerBiceps\t1.1K\t
    Podcast\tStudio Setup\t33K\t1.3K\t1.3M\tYoutube\tSankalp Jain\tSex\t21-Dec-24\tPositive\tBeerBiceps\t545\t
    Podcast\tStudio Setup\t43K\t1.9K\t1.5M\tYoutube\tVarun Dhawan\tActor\t19-Dec-24\tNegative\tBeerBiceps\t514\t
    Podcast\tStudio Setup\t53K\t4.5K\t2.2M\tYoutube\tShishir Kumar\tGhost\t14-Dec-24\tVery Negative\tBeerBiceps\t1.1K\t
    Podcast\tStudio Setup\t19K\t1.9K\t695K\tYoutube\tSanjeev Goenka\tCricket\t11-Dec-24\tNegative\tBeerBiceps\t873\t
    Podcast\tStudio Setup\t11K\t515\t402K\tYoutube\tDr. Nayana Sivaraj\tAyurveda\t09-Dec-24\tPositive\tBeerBiceps\t228\t
    Podcast\tStudio Setup\t15K\t1K\t778K\tYoutube\tDr. Vivek Allahbadia\tBone Pain\t02-Dec-24\tPositive\tBeerBiceps\t131\t
    Podcast\tStudio Setup\t15K\t1.1K\t628K\tYoutube\tSumit Shah\tCrypto\t05-Dec-24\tPositive\tBeerBiceps\t197\t
    Podcast\tStudio Setup\t7.9K\t543\t282K\tYoutube\tMithali Raj\tCricket\t30-Nov-24\tPositive\tBeerBiceps\t105\t
    Podcast\tStudio Setup\t27K\t1.2K\t894K\tYoutube\tAnkur Warikoo\tFintuber\t27-Nov-24\tVery Positive\tBeerBiceps\t222\t
    Podcast\tStudio Setup\t31K\t4.2K\t2.2M\tYoutube\tPankit Goyal\tVaastu\t21-Nov-24\tVery Negative\tBeerBiceps\t22K\t
    Podcast\tStudio Setup\t77K\t6.8K\t2.1M\tYoutube\tNitish Rajput\tNews Youtube\t19-Nov-24\tPositive\tBeerBiceps\t740\t
    Podcast\tStudio Setup\t59K\t5.3K\t2.6M\tYoutube\tRupa Bhaty\tRigveda\t16-Nov-24\tPositive\tBeerBiceps\t1.5K\t
    Podcast\tStudio Setup\t53K\t2.5K\t1.8M\tYoutube\tDr. Alok Sharma\tSleep\t14-Nov-24\tPositive\tBeerBiceps\t499\t
    Podcast\tStudio Setup\t109K\t3.6K\t4.2M\tYoutube\tRohit Shetty and Ajay Devgan\tBollywood\t09-Nov-24\tNegative\tBeerBiceps\t2K\t
    Podcast\tStudio Setup\t28K\t1.3K\t845K\tYoutube\tFood Pharmer\tHealth Youtuber\t07-Nov-24\tVery Positive\tBeerBiceps\t134\t
    Podcast\tStudio Setup\t3.9K\t372\t136K\tYoutube\tAnkit Batra\tBhajanSpecial\t04-Nov-24\tPositive\tBeerBiceps\t74\t
    Podcast\tStudio Setup\t44K\t2.5K\t1.8M\tYoutube\tDevi Chitralekhaji\tKrishna\t30-Oct-24\tPositive\tBeerBiceps\t725\t
    Podcast\tStudio Setup\t48K\t2.1K\t2M\tYoutube\tDr. Anchal\tSkincare\t28-Oct-24\tPositive\tBeerBiceps\t451\t
    Podcast\tStudio Setup\t18K\t1.6K\t630K\tYoutube\tShaan\tSinger\t24-Oct-24\tPositive\tBeerBiceps\t265\t
    Podcast\tStudio Setup\t39K\t1.4K\t1.9M\tYoutube\tKeshav Inani\tBusiness and Spirituality\t21-Oct-24\tPositive\tBeerBiceps\t637\t
    Podcast\tStudio Setup\t26K\t1.2K\t1.1M\tYoutube\tGynaec\tPregnancy\t18-Oct-24\tPositive\tBeerBiceps\t926\t
    Podcast\tStudio Setup\t50K\t4.5K\t2.2M\tYoutube\tMallika Sherawat\tBollywood\t11-Oct-24\tNegative\tBeerBiceps\t853\t
    """

    myprompt = """act as a social media analyst and give me the analysis of the following data:{context} , and keep the answers within 50 words and more humanly and in conversational toneand in hinglish language"""
    
    prompt = chat_handler.build_prompt("{myprompt}\n{context}\n{user_query}", user_query=data['message'], context=context)
    ai_response_text = chat_handler.get_ai_response(prompt.text)

    # Prepare AI message
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

@app.route('/api/parse', methods=['POST'])
def parse():
    data = request.json
    parsed_data = chat_handler.parse_data(data['data'], template=data.get('template', "{text}"))
    return jsonify({"parsed_data": parsed_data})

if __name__ == "__main__":
    app.run(debug=True)
