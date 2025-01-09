# Project Title: **Social Media Analytics Chatbot**

## Overview
The Social Media Analytics Chatbot is a Flask-based application designed to analyze social media content and provide insights through a conversational interface. It uses a combination of contextual data, a predefined dataset, and an AI-powered chatbot to offer concise and meaningful analytics about social media metrics and trends. The chatbot is optimized for Hinglish and English language responses, tailored to user queries.

---

## Features

- **AI-Powered Chatbot**: Offers insights based on user queries using advanced AI models.
- **Social Media Analytics**: Provides detailed metrics like engagement rate, sentiment analysis, likes, shares, comments, and more.
- **Contextual Analysis**: Uses a predefined dataset for enhanced context in responses.
- **Dynamic Query Handling**: Analyzes keywords in user inputs (e.g., "analytics", "metrics") and adapts responses accordingly.
- **Customizable Context**: Users can modify the context variable to include their own social media data.
- **Interactive Frontend**: Includes templates for home and analyzer pages.

---

## Practical Applications

1. **Social Media Managers**:
   - Get quick insights into performance metrics.
   - Evaluate sentiment trends for campaigns.

2. **Content Creators**:
   - Understand audience engagement for specific posts.
   - Optimize content based on analytical feedback.

3. **Market Researchers**:
   - Analyze trends across multiple data points.
   - Perform competitor analysis.

4. **General Users**:
   - Gain a better understanding of social media analytics.

---

## Problem It Solves

### Traditional Challenges:
- Analyzing social media performance manually is time-consuming.
- Lack of quick, conversational tools to process large datasets.
- Dependency on multiple platforms for metrics and insights.

### Solution:
This chatbot centralizes data analysis and presents actionable insights in a user-friendly conversational format. By integrating AI and preloaded contextual data, the tool saves time and enhances efficiency for users.

---

## Installation and Setup

### Prerequisites
Ensure you have the following installed:

- Python 3.8+
- Flask
- Requests
- Pydantic

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/username/social-media-analytics-chatbot.git
   cd social-media-analytics-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. Access the application in your browser:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

1. **Home Page**:
   - Navigate to the home page to understand the project’s purpose.

2. **Analyzer Page**:
   - Use the analyzer interface to interact with the chatbot.

3. **API Endpoints**:
   - `/api/chat`: Submit a user query for analysis.
   - `/api/parse`: Parse data using predefined templates.

4. **Customizing Context**:
   - Update the `context` variable in `app.py` to include your own data.

---

## Limitations

- **API Key Issue**: Due to issues with OpenAI’s API key limitations, we switched to Groq’s API for chat responses.
- **Hardcoded Context**: Currently, context data is hardcoded and must be updated manually for personalized analytics.

---

## Contributing

We welcome contributions to improve this project. Follow these steps to contribute:

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## Troubleshooting

1. **Flask App Not Running**:
   - Ensure all dependencies are installed using `requirements.txt`.
   - Check if port 5000 is in use.

2. **API Errors**:
   - Verify Groq API key validity in `app.py`.

3. **Dataset Issues**:
   - Ensure the `context` variable contains correctly formatted data.

---

## Live Demo
- **[Try the App Here](https://yourprojectwebsite.com)**

---

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

---

## Acknowledgments

- **OpenAI**: For initial API integration.
- **Groq**: For API support.
- **Contributors**: Thank you to everyone who helped develop and test this project.

---

## Links

- **GitHub Repository**: [Social Media Analytics Chatbot](https://github.com/username/social-media-analytics-chatbot)
- **Live Demo**: [Demo](https://yourprojectwebsite.com)

