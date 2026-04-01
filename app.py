# --- 3. UI LAYOUT ---
st.title("🛡️ XAI Phishing Intelligence Hub")
st.markdown("### Real-time IoT Threat Detection with Explainable AI")

# --- NEW: URL PARAMETERS READER ---
# Ye hissa MacroDroid se aane wale data ko read karega
query_params = st.query_params
default_email = query_params.get("email_content", "")
default_url = query_params.get("url_content", "")

# Metrics Sidebar
with st.sidebar:
    st.header("IoT Node Status")
    st.success("Cloud Engine: Active")
    st.info("AI Model: DistilBERT + CNN-LSTM")
    st.metric("Detected Threats", "12")
    st.write("---")
    st.write("**IoT Integration Mode:** Live Browser Scanning")

# Initialize Models
try:
    tokenizer, email_model, url_model, url_vec = load_all_models()
except Exception as e:
    st.error(f"Initialization Error: {e}")

tab1, tab2 = st.tabs(["📧 Email Analysis", "🔗 URL Analysis"])

# --- EMAIL TAB ---
with tab1:
    # 'value' mein 'default_email' daal diya taake auto-fill ho
    e_input = st.text_area("Paste email content (IoT Node Input)", value=default_email, height=150)
    
    # Agar data auto aaya hai, toh button dabaye baghair analysis chalao (Optional)
    if st.button("Analyze Email", type="primary") or default_email:
        if e_input:
            inputs = tokenizer(e_input, return_tensors='pt', padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                out = email_model(inputs['input_ids'], inputs['attention_mask'])
                prob = torch.nn.functional.softmax(out, dim=1).item()
            
            st.metric("Risk Level", f"{prob*100:.2f}%")
            if prob > 0.5: st.error("🚨 Verdict: MALICIOUS")
            else: st.success("✅ Verdict: SAFE")
            st.write("**AI Explanation:**", get_ai_explanation(e_input[:100], prob, "Email"))

# --- URL TAB ---
with tab2:
    # 'value' mein 'default_url' daal diya taake auto-fill ho
    u_input = st.text_input("Enter URL from Device", value=default_url, placeholder="example.com")
    
    if st.button("Scan URL", type="primary") or default_url:
        if u_input:
            cleaned = str(u_input).lower().replace('https://', '').replace('http://', '').replace('www.', '')
            features = url_vec.transform([cleaned]).toarray()
            u_pred = url_model.predict(np.expand_dims(features, axis=-1), verbose=0)
            prob = float(np.squeeze(u_pred))
            
            st.metric("Risk Level", f"{prob*100:.2f}%")
            if prob > 0.6: st.error("🚨 Verdict: MALICIOUS")
            else: st.success("✅ Verdict: SAFE")
            st.write("**AI Explanation:**", get_ai_explanation(u_input, prob, "URL"))
