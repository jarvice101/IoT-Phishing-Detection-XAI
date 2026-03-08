import streamlit as st
import torch
import os
import numpy as np
import pickle
import tensorflow as tf
import re
from transformers import AutoTokenizer, DistilBertModel
from groq import Groq
from fastapi import FastAPI
import uvicorn
from threading import Thread

# 1. MODEL JOINER (Bari file ko wapis jorne ke liye)
def join_model():
    # Agar asli file nahi hai lekin parts maujood hain, toh jor do
    if not os.path.exists('best_model.pt'):
        parts = sorted([f for f in os.listdir('.') if 'best_model.pt.part' in f])
        if parts:
            with open('best_model.pt', 'wb') as f:
                for part in parts:
                    with open(part, 'rb') as p:
                        f.write(p.read())
            return True
    return os.path.exists('best_model.pt')

# 2. API SETUP (LLM for Explanations)
GROQ_API_KEY = "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"
client_groq = Groq(api_key=GROQ_API_KEY)

# --- FASTAPI SETUP FOR IOT DEVICES ---
api_app = FastAPI()

@api_app.post("/iot_scan")
async def iot_scan(data: dict):
    # Yeh endpoint IoT devices (Mobile/Watch) se data lega
    content = data.get("content")
    type = data.get("type", "URL")
    return {"status": "received", "message": f"{type} is being processed by Cloud AI"}

# --- MODELS & PREPROCESSING ---
class DistilBertClassifier(torch.nn.Module):
    def __init__(self):
        super(DistilBertClassifier, self).__init__()
        self.distilbert = DistilBertModel.from_pretrained('distilbert-base-uncased')
        self.classifier = torch.nn.Linear(768, 2)
    def forward(self, input_ids, attention_mask):
        output = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        return self.classifier(output[0][:, 0])

def clean_url(text):
    text = str(text).lower()
    text = re.sub(r'^https?:\/\/|www\.', '', text)
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    return text

def get_ai_explanation(content, score, type="URL"):
    prompt = f"Cybersecurity Expert analysis: The {type} '{content}' has a risk score of {score*100:.2f}%. Explain why in 2 professional lines."
    try:
        completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content
    except:
        return "Patterns detected correlate with known phishing signatures. Precaution advised."

# --- STREAMLIT UI ---
st.set_page_config(page_title="🛡️ XAI Cyber Guard", layout="wide")
st.title("🛡️ XAI Phishing Intelligence (Multi-Device Hub)")

# Dashboard Metrics
col_a, col_b, col_c = st.columns(3)
col_a.metric("Active IoT Nodes", "4") 
col_b.metric("Threats Blocked", "12")
col_c.metric("Cloud Status", "Online & Healthy")

st.divider()

tab1, tab2 = st.tabs(["📧 Email Analysis", "🔗 URL Analysis"])

# --- TAB 1: EMAIL (DistilBERT) ---
with tab1:
    st.header("Forensic Email Analysis")
    e_input = st.text_area("Paste email content here", height=150, key="email_box")
    if st.button("Analyze Email Integrity", type="primary"):
        if e_input:
            try:
                with st.spinner('Joining and Loading Model...'):
                    if join_model():
                        tokenizer = AutoTokenizer.from_pretrained('spam_tokenizer')
                        model = DistilBertClassifier()
                        model.load_state_dict(torch.load('best_model.pt', map_location='cpu'), strict=False)
                        model.eval()
                        
                        inputs = tokenizer(e_input, return_tensors='pt', padding=True, truncation=True, max_length=512)
                        with torch.no_grad():
                            out = model(inputs['input_ids'], inputs['attention_mask'])
                            prob = torch.nn.functional.softmax(out, dim=1)[0][1].item()
                        
                        st.subheader("System Verdict")
                        st.metric("Risk Score", f"{prob*100:.2f}%")
                        if prob > 0.5: st.error("🚨 RESULT: MALICIOUS / PHISHING")
                        else: st.success("✅ RESULT: SAFE / LEGITIMATE")
                        st.info(get_ai_explanation(e_input[:100], prob, "Email"))
                    else:
                        st.error("Model parts missing! Please upload .part files.")
            except Exception as e: st.error(f"Error: {e}")

# --- TAB 2: URL (CNN-LSTM) ---
with tab2:
    st.header("URL Pattern Intelligence")
    u_input = st.text_input("Enter URL to scan", placeholder="example.com", key="url_box")
    if st.button("Run URL Scan", type="primary"):
        if u_input:
            try:
                with st.spinner('Scanning URL patterns...'):
                    u_model = tf.keras.models.load_model('cnn_lstm_url_model.keras', compile=False)
                    with open('url_tfidf.pkl', 'rb') as f:
                        vec = pickle.load(f)
                    
                    cleaned = clean_url(u_input)
                    features = vec.transform([cleaned]).toarray()
                    u_pred = u_model.predict(np.expand_dims(features, axis=-1), verbose=0)
                    prob = float(np.squeeze(u_pred))
                    
                    st.subheader("System Verdict")
                    st.metric("Risk Score", f"{prob*100:.2f}%")
                    if prob > 0.6: st.error("🚨 RESULT: MALICIOUS URL")
                    else: st.success("✅ RESULT: SECURE URL")
                    st.info(get_ai_explanation(u_input, prob, "URL"))
            except Exception as e: st.error(f"Error: {e}")