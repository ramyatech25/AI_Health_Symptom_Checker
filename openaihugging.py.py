import os

def create_project():
    # Create directories
    dirs = ['templates', 'static/css', 'static/js', 'static/images', 'utils']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        if d == 'utils':
            init_path = os.path.join(d, '__init__.py')
            if not os.path.exists(init_path):
                with open(init_path, 'w') as f:
                    f.write('')

    # Define all file contents
    files = {
        'app.py': '''from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from config import Config
from symptom_extractor import extract_symptoms
from disease_predictor import predict_disease
from ai_helpers import get_disease_info, generate_medical_report
from utils.helper import format_disease_info
import io

app = Flask(__name__)
app.config.from_object(Config)

@app.before_request
def before_request():
    if 'history' not in session:
        session['history'] = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_input = request.form.get('symptoms', '').strip()
    if not user_input:
        flash('Please enter your symptoms.', 'warning')
        return redirect(url_for('index'))
    
    symptoms = extract_symptoms(user_input)
    if not symptoms:
        flash('No known symptoms detected. Please try again with clear symptom descriptions.', 'danger')
        return redirect(url_for('index'))
    
    disease, confidence = predict_disease(user_input, symptoms)
    description, precautions = get_disease_info(disease)
    
    result = format_disease_info(disease, confidence, description, precautions)
    
    session['last_result'] = {
        'symptoms': symptoms,
        'disease': disease,
        'confidence': confidence,
        'description': description,
        'precautions': precautions
    }
    
    history_entry = {
        'symptoms': ', '.join(symptoms),
        'disease': disease,
        'confidence': result['confidence']
    }
    session['history'].append(history_entry)
    session.modified = True
    
    return render_template('result.html', result=result, symptoms=symptoms)

@app.route('/generate_report')
def generate_report():
    result = session.get('last_result')
    if not result:
        flash('No prediction found. Please check symptoms first.', 'warning')
        return redirect(url_for('index'))
    
    report_text = generate_medical_report(
        result['symptoms'],
        result['disease'],
        result['confidence'],
        result['description'],
        result['precautions']
    )
    
    file_data = io.BytesIO(report_text.encode('utf-8'))
    return send_file(
        file_data,
        mimetype='text/plain',
        as_attachment=True,
        download_name=f"Medical_Report_{result['disease']}.txt"
    )

@app.route('/history')
def history():
    return render_template('history.html', history=session['history'])

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['history'] = []
    session.modified = True
    flash('History cleared.', 'info')
    return redirect(url_for('history'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
''',

        'config.py': '''import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', None)
    USE_HUGGINGFACE_PREDICT = os.getenv('USE_HUGGINGFACE_PREDICT', 'False').lower() == 'true'
    MODEL_PATH = 'model.pkl'
    LABEL_ENCODER_PATH = 'label_encoder.pkl'
    SYMPTOMS_CSV = 'symptoms.csv'
    ALL_SYMPTOMS = [
        'fever', 'cough', 'headache', 'fatigue', 'sneezing',
        'runny_nose', 'sore_throat', 'body_ache', 'loss_of_taste',
        'shortness_of_breath', 'chest_pain', 'nausea', 'vomiting',
        'diarrhea', 'muscle_pain', 'chills', 'congestion'
    ]
''',

        '.env': '''SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=your_openai_api_key_optional
HUGGINGFACE_API_KEY=your_huggingface_api_key_optional
USE_HUGGINGFACE_PREDICT=True   # Set to True to use Hugging Face zero-shot for prediction
''',

        'requirements.txt': '''Flask==2.3.3
python-dotenv==1.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
requests==2.31.0
openai==1.3.0
''',

        'symptoms.csv': '''Disease,Fever,Cough,Headache,Fatigue,Sneezing,RunnyNose,SoreThroat,BodyAche,LossOfTaste,ShortnessOfBreath,ChestPain,Nausea,Vomiting,Diarrhea,MusclePain,Chills,Congestion
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,0,1,0,1,1,1,0,0,0,0,0,0,1,1,0
Flu,0,1,1,1,1,0,0,1,0,0,0,0,0,0,1,1,1
Flu,1,1,1,1,0,1,1,1,0,0,0,0,0,0,1,1,0
Flu,1,0,0,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,1,0,0,1,0,0,0,0,0,0,1,1,0
Flu,1,1,0,1,0,1,1,1,0,0,0,0,0,0,1,1,1
Flu,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,0
Flu,1,0,1,1,0,1,0,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,0,1,0,0,0,1,0,0,0,0,0,0,1,1,0
Flu,1,0,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,0,1,0,0,1,0,1,0,0,0,0,0,0,1,0,0
Flu,1,1,1,1,0,0,0,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,0,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Flu,1,1,1,1,0,0,1,1,0,0,0,0,0,0,1,1,0
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
Cold,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
COVID-19,1,1,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Allergy,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,1
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
Migraine,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0
''',

        'symptom_extractor.py': '''from utils.helper import extract_symptoms_from_text
from config import Config
import openai
import requests

def extract_symptoms_openai(text):
    if not Config.OPENAI_API_KEY:
        return None
    openai.api_key = Config.OPENAI_API_KEY
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant. Extract a list of symptoms from the user's description. Return only a comma-separated list of symptoms, using the exact symptom names from this list: " + ", ".join(Config.ALL_SYMPTOMS) + ". If no symptoms are found, return 'none'."},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=100
        )
        content = response.choices[0].message.content.strip().lower()
        if content == 'none':
            return []
        symptoms = [s.strip() for s in content.split(',') if s.strip()]
        symptoms = [s for s in symptoms if s in Config.ALL_SYMPTOMS]
        return symptoms
    except Exception as e:
        print(f"OpenAI extraction error: {e}")
        return None

def extract_symptoms_huggingface(text):
    """Use Hugging Face NER (or a custom extraction) - simplified fallback."""
    # For demonstration, we could use a NER model, but we'll keep it simple
    # and just use the regex fallback if OpenAI fails.
    return None

def extract_symptoms(input_text):
    # Try OpenAI first if available
    if Config.OPENAI_API_KEY:
        symptoms = extract_symptoms_openai(input_text)
        if symptoms is not None:
            return symptoms
    # Fallback to regex
    return extract_symptoms_from_text(input_text)
''',

        'ai_helpers.py': '''import openai
import requests
from config import Config
from datetime import datetime

def get_disease_info_openai(disease_name):
    if not Config.OPENAI_API_KEY:
        return None, None
    openai.api_key = Config.OPENAI_API_KEY
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical information assistant. Provide a short description and three practical precautions for the given disease. Format your answer as: DESCRIPTION: <description> PRECAUTIONS: <precaution1>, <precaution2>, <precaution3>"},
                {"role": "user", "content": disease_name}
            ],
            temperature=0.5,
            max_tokens=150
        )
        content = response.choices[0].message.content.strip()
        description = "No description available."
        precautions = "Please consult a doctor."
        if "DESCRIPTION:" in content and "PRECAUTIONS:" in content:
            parts = content.split("PRECAUTIONS:")
            desc_part = parts[0].replace("DESCRIPTION:", "").strip()
            prec_part = parts[1].strip() if len(parts) > 1 else ""
            description = desc_part if desc_part else description
            precautions = prec_part if prec_part else precautions
        else:
            description = content
        return description, precautions
    except Exception as e:
        print(f"OpenAI info error: {e}")
        return None, None

def get_disease_info_huggingface(disease_name):
    if not Config.HUGGINGFACE_API_KEY:
        return None, None
    try:
        model_name = "google/flan-t5-base"
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"}
        prompt = f"Provide a brief description and three precautions for {disease_name}."
        payload = {"inputs": prompt}
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        generated_text = result[0]['generated_text'] if isinstance(result, list) else result['generated_text']
        parts = generated_text.split('.')
        if len(parts) >= 2:
            description = parts[0].strip() + '.'
            precautions = '.'.join(parts[1:]).strip()
        else:
            description = generated_text
            precautions = "Consult a healthcare professional."
        return description, precautions
    except Exception as e:
        print(f"Hugging Face info error: {e}")
        return None, None

def fallback_info(disease):
    info = {
        'Flu': ("Influenza is a viral infection that attacks your respiratory system.",
                "1. Rest and drink fluids. 2. Take over-the-counter pain relievers. 3. See a doctor if symptoms worsen."),
        'Cold': ("The common cold is a viral infection of your nose and throat.",
                 "1. Get plenty of rest. 2. Stay hydrated. 3. Use saline nasal spray."),
        'COVID-19': ("COVID-19 is an infectious disease caused by the SARS-CoV-2 virus.",
                     "1. Isolate and monitor symptoms. 2. Seek medical help if breathing difficulty. 3. Follow local health guidelines."),
        'Allergy': ("Allergies occur when your immune system reacts to a foreign substance.",
                    "1. Avoid allergens. 2. Use antihistamines. 3. Consult an allergist."),
        'Migraine': ("Migraine is a neurological condition causing severe headaches.",
                     "1. Rest in a quiet, dark room. 2. Apply cold or warm compresses. 3. Take prescribed medications.")
    }
    return info.get(disease, ("No detailed information available.", "Please consult a doctor."))

def get_disease_info(disease_name):
    desc, prec = get_disease_info_openai(disease_name)
    if desc and prec:
        return desc, prec
    desc, prec = get_disease_info_huggingface(disease_name)
    if desc and prec:
        return desc, prec
    return fallback_info(disease_name)

def generate_medical_report(symptoms, disease, confidence, description, precautions):
    symptom_list = ", ".join(symptoms)
    confidence_str = f"{confidence:.2f}%"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    summary = ""
    if Config.OPENAI_API_KEY:
        try:
            openai.api_key = Config.OPENAI_API_KEY
            prompt = f"""
            Given the following medical information, write a short, clear, and empathetic medical report summary for a patient.
            Symptoms: {symptom_list}
            Possible Disease: {disease}
            Confidence: {confidence_str}
            Description: {description}
            Precautions: {precautions}
            Include recommendations for next steps (when to see a doctor, lifestyle advice).
            """
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant. Provide a concise and reassuring medical report summary."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI report generation error: {e}")
    
    report = f"""
============================================
        MEDICAL REPORT
============================================
Date: {date_str}
--------------------------------------------

SYMPTOMS REPORTED:
{symptom_list}

PREDICTED CONDITION:
{disease} (Confidence: {confidence_str})

DESCRIPTION:
{description}

PRECAUTIONS & SELF-CARE:
{precautions}

"""
    if summary:
        report += f"""
AI-GENERATED SUMMARY & RECOMMENDATIONS:
{summary}
"""
    else:
        report += """
ADDITIONAL NOTES:
This report is generated based on the symptoms you provided. It is not a substitute for professional medical advice. Please consult a healthcare provider for an accurate diagnosis.
"""

    report += """
============================================
Disclaimer: This report is for informational purposes only and does not constitute medical advice. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
"""
    return report
''',

        'disease_predictor.py': '''import numpy as np
import pandas as pd
import requests
from utils.preprocessing import load_model_and_encoder, encode_symptoms
from config import Config

# Load local model and encoder (will be used as fallback or primary)
model, label_encoder = load_model_and_encoder()

# Load disease labels from CSV for zero-shot classification
def get_disease_labels():
    df = pd.read_csv(Config.SYMPTOMS_CSV)
    return list(df['Disease'].unique())

def predict_disease_huggingface(user_text, symptom_list):
    """Use Hugging Face zero-shot classification to predict disease."""
    if not Config.HUGGINGFACE_API_KEY or not Config.USE_HUGGINGFACE_PREDICT:
        return None, None
    
    candidate_labels = get_disease_labels()
    # If we have symptoms, use them; otherwise use the full text
    sequence = user_text if user_text else ', '.join(symptom_list)
    
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": sequence,
        "parameters": {"candidate_labels": candidate_labels}
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        # Extract top label and confidence
        labels = result['labels']
        scores = result['scores']
        # Take the highest score
        best_idx = np.argmax(scores)
        disease = labels[best_idx]
        confidence = scores[best_idx] * 100
        return disease, confidence
    except Exception as e:
        print(f"Hugging Face prediction error: {e}")
        return None, None

def predict_disease_local(symptom_list):
    """Use the local Random Forest model."""
    feature_vector = encode_symptoms(symptom_list, Config.ALL_SYMPTOMS)
    X = np.array([feature_vector])
    proba = model.predict_proba(X)[0]
    pred_idx = np.argmax(proba)
    confidence = proba[pred_idx] * 100
    disease = label_encoder.inverse_transform([pred_idx])[0]
    return disease, confidence

def predict_disease(user_text, symptom_list):
    """
    Predict disease using Hugging Face zero-shot if enabled, else fallback to local model.
    """
    if Config.USE_HUGGINGFACE_PREDICT and Config.HUGGINGFACE_API_KEY:
        disease, confidence = predict_disease_huggingface(user_text, symptom_list)
        if disease is not None:
            return disease, confidence
        # If HF fails, fall through to local
    # Local model prediction
    return predict_disease_local(symptom_list)
''',

        'utils/preprocessing.py': '''import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
from config import Config

def load_and_prepare_data(csv_path):
    df = pd.read_csv(csv_path)
    X = df.drop('Disease', axis=1).values
    y = df['Disease'].values
    return X, y

def train_and_save_model():
    X, y = load_and_prepare_data(Config.SYMPTOMS_CSV)
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y_encoded)
    with open(Config.MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(Config.LABEL_ENCODER_PATH, 'wb') as f:
        pickle.dump(le, f)
    return model, le

def load_model_and_encoder():
    if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.LABEL_ENCODER_PATH):
        with open(Config.MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(Config.LABEL_ENCODER_PATH, 'rb') as f:
            le = pickle.load(f)
        return model, le
    else:
        return train_and_save_model()

def encode_symptoms(symptom_list, all_symptoms):
    vector = {symptom: 0 for symptom in all_symptoms}
    for symptom in symptom_list:
        if symptom in vector:
            vector[symptom] = 1
    return [vector[s] for s in all_symptoms]
''',

        'utils/helper.py': '''from config import Config
import re

def extract_symptoms_from_text(text):
    text_lower = text.lower()
    found = []
    for symptom in Config.ALL_SYMPTOMS:
        if re.search(r'\\b' + re.escape(symptom) + r'\\b', text_lower):
            found.append(symptom)
    return found

def format_disease_info(disease, confidence, description=None, precautions=None):
    return {
        'disease': disease,
        'confidence': f"{confidence:.2f}%",
        'description': description or "No additional information available.",
        'precautions': precautions or "Please consult a doctor."
    }
''',

        'templates/index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Health Symptom Checker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">AI Health Symptom Checker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('history') }}">History</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('about') }}">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">Check Your Symptoms</h4>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="{{ url_for('predict') }}">
                            <div class="mb-3">
                                <label for="symptoms" class="form-label">Describe your symptoms or list them separated by commas:</label>
                                <textarea class="form-control" id="symptoms" name="symptoms" rows="4" placeholder="e.g., fever, cough, headache, fatigue"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Check Symptoms</button>
                        </form>
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                <div class="mt-3">
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                            {{ message }}
                                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                        </div>
                                    {% endfor %}
                                </div>
                            {% endif %}
                        {% endwith %}
                    </div>
                </div>
                <div class="mt-3 text-muted text-center">
                    <small>Note: This is an AI-powered tool and not a substitute for professional medical advice.</small>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
''',

        'templates/result.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prediction Result</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">AI Health Symptom Checker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('history') }}">History</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('about') }}">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-success text-white">
                        <h4 class="mb-0">Prediction Result</h4>
                    </div>
                    <div class="card-body">
                        <h5>Detected Symptoms:</h5>
                        <p class="badge bg-secondary">{{ symptoms | join(', ') }}</p>
                        <hr>
                        <h3 class="text-primary">Predicted Disease: {{ result.disease }}</h3>
                        <p><strong>Confidence:</strong> {{ result.confidence }}</p>
                        <hr>
                        <h5>Description:</h5>
                        <p>{{ result.description }}</p>
                        <h5>Precautions:</h5>
                        <p>{{ result.precautions }}</p>
                        <div class="d-grid gap-2 d-md-flex justify-content-md-between mt-4">
                            <a href="{{ url_for('index') }}" class="btn btn-primary">Check Again</a>
                            <a href="{{ url_for('generate_report') }}" class="btn btn-success">Download Medical Report</a>
                            <a href="{{ url_for('history') }}" class="btn btn-outline-secondary">View History</a>
                        </div>
                    </div>
                </div>
                <div class="mt-3 text-muted text-center">
                    <small>This information is generated by an AI and should not replace professional medical advice.</small>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
''',

        'templates/history.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prediction History</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">AI Health Symptom Checker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link active" href="{{ url_for('history') }}">History</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('about') }}">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h4 class="mb-0">Prediction History</h4>
                        <form method="POST" action="{{ url_for('clear_history') }}" class="mb-0">
                            <button type="submit" class="btn btn-danger btn-sm">Clear History</button>
                        </form>
                    </div>
                    <div class="card-body">
                        {% if history %}
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Symptoms</th>
                                            <th>Disease</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for entry in history %}
                                        <tr>
                                            <td>{{ loop.index }}</td>
                                            <td>{{ entry.symptoms }}</td>
                                            <td>{{ entry.disease }}</td>
                                            <td>{{ entry.confidence }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted text-center">No predictions yet. Go to the <a href="{{ url_for('index') }}">home page</a> to check symptoms.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
''',

        'templates/about.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - AI Health Symptom Checker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">AI Health Symptom Checker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('history') }}">History</a></li>
                    <li class="nav-item"><a class="nav-link active" href="{{ url_for('about') }}">About</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">About This Project</h4>
                    </div>
                    <div class="card-body">
                        <h5>AI Health Symptom Checker</h5>
                        <p>
                            This application uses machine learning and state-of-the-art language models (OpenAI & Hugging Face)
                            to analyse symptoms, predict possible diseases, and generate a detailed medical report.
                        </p>
                        <h5>Key Features</h5>
                        <ul>
                            <li><strong>Intelligent Symptom Extraction</strong> – Uses OpenAI GPT (or regex fallback) to extract symptoms from free text.</li>
                            <li><strong>Hybrid Disease Prediction</strong> – Choose between a local Random Forest model or Hugging Face zero-shot classification (via <code>facebook/bart-large-mnli</code>).</li>
                            <li><strong>Comprehensive Disease Info</strong> – Description and precautions generated by OpenAI, Hugging Face, or static fallback.</li>
                            <li><strong>Medical Report Generation</strong> – Download a detailed .txt report with AI-generated summary and recommendations.</li>
                            <li><strong>History Tracking</strong> – All predictions are stored in your session.</li>
                        </ul>
                        <h5>Technology Stack</h5>
                        <ul>
                            <li>Flask (Backend)</li>
                            <li>scikit-learn (Local ML)</li>
                            <li>OpenAI API (Symptom extraction, report summarization)</li>
                            <li>Hugging Face Inference API (Zero-shot prediction, disease info)</li>
                            <li>Bootstrap (Frontend)</li>
                        </ul>
                        <h5>Configuration</h5>
                        <p>
                            Set <code>USE_HUGGINGFACE_PREDICT=True</code> in your <code>.env</code> to enable Hugging Face zero-shot prediction.
                            Provide either <code>OPENAI_API_KEY</code> or <code>HUGGINGFACE_API_KEY</code> for enhanced features.
                        </p>
                        <p class="text-muted mt-3">
                            <small>Disclaimer: This tool is for educational purposes only and does not constitute medical advice.</small>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
''',

        'static/css/style.css': '''body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.card {
    border-radius: 10px;
    border: none;
}
.card-header {
    border-radius: 10px 10px 0 0 !important;
}
.navbar-brand {
    font-weight: 600;
}
.btn-primary {
    background-color: #0d6efd;
    border-color: #0d6efd;
}
.btn-primary:hover {
    background-color: #0b5ed7;
    border-color: #0a58ca;
}
.alert {
    border-radius: 8px;
}
.table th {
    background-color: #e9ecef;
}
.badge {
    font-size: 1rem;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
}
''',

        'static/js/script.js': '''document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 5000);
    });
});
'''
    }

    for path, content in files.items():
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Project created successfully with Hugging Face Integration!")
    print("Features:")
    print("  - OpenAI symptom extraction (fallback to regex)")
    print("  - Hugging Face zero-shot disease prediction (optional)")
    print("  - Hugging Face disease information generation (fallback to static)")
    print("  - Downloadable medical report with AI summary")
    print("\nTo run:")
    print("  1. pip install -r requirements.txt")
    print("  2. Set your API keys in .env")
    print("  3. python app.py")
    print("  4. Open http://127.0.0.1:5000")

if __name__ == '__main__':
    create_project()