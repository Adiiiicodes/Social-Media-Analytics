from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
import uuid
import requests
from bs4 import BeautifulSoup
import PyPDF2
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time
from groq import Groq
import os
from flask import jsonify, request, render_template
from werkzeug.utils import secure_filename
import uuid
from typing import Dict, Any

app = Flask(__name__)
app.secret_key = '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'  # Use a secure secret key

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_EXTENSIONS = {'pdf'}
TEMP_EMAIL_STORAGE = {}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Initialize ChromaDB
chroma_persist_directory = "chroma_db"
os.makedirs(chroma_persist_directory, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_pdf(file_path):
    """Extract text from PDF."""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def split_text(text, chunk_size=1000, chunk_overlap=200):
    """Split text into chunks using the text splitter."""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)

def get_with_retry(url):
    """Make a GET request with retries and polite delay."""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    headers = {
        'User-Agent': 'Friendly Bot 1.0 (cookiebolte@gmail.com)',
    }

    response = session.get(url, headers=headers)
    time.sleep(2)  # Polite delay between requests
    return response

def scrape_job_posting(url):
    """Scrape job posting from a URL using retry logic."""
    try:
        response = get_with_retry(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'meta', 'iframe']):
            element.decompose()

        content = soup.get_text(separator="\n", strip=True)
        if len(content) < 50:
            return None
        return content

    except Exception as e:
        print(f"Error scraping job posting: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

def create_email_prompt(form_data: Dict[str, Any], job_posting_text: str) -> str:
    return f"""
    Generate a professional email using the following information:
    
    Sender's Name: {form_data['name']}
    Company: {form_data['company']}
    Services Offered: {form_data['services']}
    Recipient: {form_data['recipient']}
    Goal: {form_data['goal']}
    Problem to Solve: {form_data['problem']}
    Past Work Experience: {form_data['pastWork']}
    Desired Tone: {form_data['tone']}
    Call to Action: {form_data['cta']}
    Benefits: {form_data['benefits']}
    Deadline: {form_data['deadline']}
    
    Job Posting Details:
    {job_posting_text}
    
    Create a persuasive email that:
    1. Maintains a {form_data['tone']} tone
    2. Clearly addresses the recipient's needs from the job posting
    3. Highlights relevant experience and benefits
    4. Includes a clear call to action
    5. Uses the provided sign-off: {form_data['customSignoff'] if form_data['customSignoff'] else form_data['signoff']}
    """

@app.route('/generate', methods=['GET', 'POST'])
def generate_email():
    if request.method == 'GET':
        return render_template('generate.html')

    if request.method == 'POST':
        try:
            # File handling
            if 'portfolio' not in request.files:
                return jsonify({'success': False, 'message': 'No file uploaded'})

            file = request.files['portfolio']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'})

            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Invalid file type'})

            # Generate unique ID and save file
            email_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, f"{email_id}_{filename}")
            file.save(temp_path)

            # Process portfolio
            portfolio_text = process_pdf(temp_path)
            chunks = split_text(portfolio_text)

            # Store in vector database
            vectorstore = Chroma(
                collection_name=f"portfolio_{email_id}",
                embedding_function=embeddings,
                persist_directory=chroma_persist_directory
            )
            vectorstore.add_texts(chunks)

            # Get and validate job URL
            job_url = request.form.get('jobUrl')
            if not job_url:
                return jsonify({'success': False, 'message': 'Job posting URL is required'})

            job_posting_text = scrape_job_posting(job_url)
            if not job_posting_text:
                return jsonify({'success': False, 'message': 'Unable to scrape job posting. Please check the URL.'})

            # Collect form data
            form_data = {
                'name': request.form.get('name'),
                'company': request.form.get('company'),
                'services': request.form.get('services'),
                'recipient': request.form.get('recipient'),
                'goal': request.form.get('goal'),
                'problem': request.form.get('problem'),
                'pastWork': request.form.get('pastWork'),
                'tone': request.form.get('tone'),
                'cta': request.form.get('cta'),
                'benefits': request.form.get('benefits'),
                'deadline': request.form.get('deadline'),
                'signoff': request.form.get('signoff'),
                'customSignoff': request.form.get('customSignoff'),
                'portfolio_chunks': chunks,
                'job_posting': job_posting_text
            }

            # Initialize Groq client
            groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            
            # Create prompt and generate email
            prompt = create_email_prompt(form_data, job_posting_text)
            
            # Make API call to Groq
            completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer who crafts compelling, personalized business correspondence."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",  # Or your preferred Groq model
                temperature=0.7,
                max_tokens=1000
            )

            # Extract generated email
            email_content = completion.choices[0].message.content

            # Store email data
            TEMP_EMAIL_STORAGE[email_id] = {
                'form_data': form_data,
                'email_content': email_content
            }

            # Clean up
            os.remove(temp_path)

            return jsonify({'success': True, 'emailId': email_id})
            
        except Exception as e:
            print(f"Error generating email: {e}")
            return jsonify({'success': False, 'message': str(e)})

@app.route('/preview')
def preview_email():
    email_id = request.args.get('id')
    if not email_id or email_id not in TEMP_EMAIL_STORAGE:
        return "Email not found", 404

    email_data = TEMP_EMAIL_STORAGE[email_id]
    email_content = email_data.get('email_content', 'Email content is not available.')

    return render_template('preview.html', email_content=email_content, email_id=email_id)

@app.route('/modify_email', methods=['POST'])
def modify_email():
    email_id = request.json.get('emailId')
    modified_content = request.json.get('content')

    if not email_id or email_id not in TEMP_EMAIL_STORAGE:
        return jsonify({'success': False, 'message': 'Email not found'})

    TEMP_EMAIL_STORAGE[email_id]['email_content'] = modified_content
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
