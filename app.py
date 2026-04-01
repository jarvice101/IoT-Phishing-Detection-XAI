# --- NEW: URL PARAMETERS READER ---
query_params = st.query_params
default_email = query_params.get("email_content", "")
default_url = query_params.get("url_content", "")

# Agar koi data bahar se aaya hai, toh sahi Tab ko select karne ke liye index set karein
start_tab = 0
if default_url:
    start_tab = 1

tab1, tab2 = st.tabs(["📧 Email Analysis", "🔗 URL Analysis"])

# --- EMAIL TAB ---
with tab1 if start_tab == 0 else tab1:
    e_input = st.text_area("Paste email content (IoT Node Input)", value=default_email, height=150)
    # Baqi analysis code wahi rahega...

# --- URL TAB ---
with tab2:
    u_input = st.text_input("Enter URL from Device", value=default_url, placeholder="example.com")
    # Baqi analysis code wahi rahega...
