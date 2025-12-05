"""
💪 FITZONE GYM FITNESS ASSISTANT
Professional Portfolio-Ready Bot
Save as: gym_fitness.py
"""

import streamlit as st
import requests
import time
from datetime import datetime
from collections import defaultdict

# ==================== CONFIGURATION ====================
import os
GOOGLE_API_KEY = st.secrets.get("AIzaSyCRoaWiiOGsslJ5VQwPXo-pfYRmOUMxu5Q", os.getenv("AIzaSyCRoaWiiOGsslJ5VQwPXo-pfYRmOUMxu5Q", ""))  #⚠️ REPLACE THIS

RATE_LIMIT = 10
RATE_LIMIT_WINDOW = 60
CACHE_TTL = 300

# ==================== SESSION STATE ====================
if 'rate_limit_tracker' not in st.session_state:
    st.session_state.rate_limit_tracker = defaultdict(list)
if 'response_cache' not in st.session_state:
    st.session_state.response_cache = {}

# ==================== KNOWLEDGE BASE ====================
GYM_INFO = """
FITZONE GYM

Location: 123 Fitness Avenue, City Center
Phone: (555) 123-4567
Hours: Mon-Fri 5AM-11PM, Weekends 6AM-10PM
Rating: 4.7/5 stars

MEMBERSHIPS:
Basic $29/mo - Gym access, locker room, WiFi
Premium $49/mo - Basic + group classes, sauna, 2 guest passes/month
Elite $79/mo - Premium + 2 PT sessions/month, nutrition consult
Day Pass: $15

CLASSES:
Yoga: Mon/Wed/Fri 7AM, 6PM
Spin: Tue/Thu/Sat 6:30AM, 5:30PM
HIIT: Mon/Wed/Fri 6PM
Pilates: Tue/Thu 7AM, 6PM
Zumba: Wed/Sat 5PM
Boxing: Tue/Thu 7PM

PERSONAL TRAINING:
Single: $60, 5-pack: $275, 10-pack: $500, Unlimited: $400/month

SPECIAL: First month 50% off for new members!
"""

# ==================== FUNCTIONS ====================
def check_rate_limit():
    current_time = time.time()
    requests_list = st.session_state.rate_limit_tracker["user"]
    requests_list = [t for t in requests_list if current_time - t < RATE_LIMIT_WINDOW]
    st.session_state.rate_limit_tracker["user"] = requests_list
    if len(requests_list) >= RATE_LIMIT:
        return False
    requests_list.append(current_time)
    return True

def get_cached_response(question):
    cache_key = f"gym:{question}"
    if cache_key in st.session_state.response_cache:
        cached = st.session_state.response_cache[cache_key]
        if time.time() - cached['timestamp'] < CACHE_TTL:
            return cached['response']
    return None

def cache_response(question, response):
    st.session_state.response_cache[f"gym:{question}"] = {
        'response': response, 'timestamp': time.time()
    }

def ask_trainer(question):
    try:
        if not check_rate_limit():
            return "⏱️ Please wait a moment before asking another question!"
        
        cached = get_cached_response(question)
        if cached:
            return cached
        
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
            return "❌ System not configured. Please contact administrator."
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
        
        prompt = f"""You are Max, an energetic fitness assistant at FitZone Gym.

Answer using ONLY this information:
{GYM_INFO}

Customer: {question}

Your response:"""
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 600}
        }
        
        response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                               json=payload, timeout=20)
        
        if response.status_code == 429:
            return """😅 Oops! Too many questions right now.

**What to do:**
• Wait 60 seconds and try again
• The system has rate limits to prevent overload

Sorry for the inconvenience! 💪"""
        
        if response.status_code != 200:
            return "❌ Sorry, something went wrong. Please try again in a moment."
        
        answer = response.json()['candidates'][0]['content']['parts'][0]['text']
        cache_response(question, answer)
        return answer
        
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again!"
    except Exception as e:
        return "❌ Sorry, I'm having trouble right now. Please try again!"

# ==================== PAGE SETUP ====================
st.set_page_config(
    page_title="FitZone Gym",
    page_icon="💪",
    layout="wide"
)

# ==================== STYLING ====================
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    /* Full gradient background - NO WHITE */
    .main, .stApp {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%) !important;
    }
    
    .main .block-container {
        max-width: 950px;
        padding: 2rem 1rem;
    }
    
    /* Title - CENTERED */
    .main h1 {
        color: white !important;
        text-align: center !important;
        font-size: 4.2rem !important;
        font-weight: 900 !important;
        text-shadow: 5px 5px 15px rgba(0,0,0,0.7);
        margin: 0 auto 0.3rem auto !important;
        padding: 0 !important;
        letter-spacing: 3px;
    }
    
    /* Subtitle - CENTERED */
    .subtitle {
        color: rgba(255, 255, 255, 0.98);
        text-align: center;
        font-size: 1.7rem;
        font-weight: 400;
        letter-spacing: 5px;
        margin-bottom: 2rem;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.6);
    }
    
    .status-box {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
        padding: 1.4rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        font-size: 1.3rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }
    
    .membership-card {
        background: rgba(255, 255, 255, 0.96);
        padding: 1.8rem;
        border-radius: 22px;
        margin: 1.2rem 0;
        box-shadow: 0 8px 28px rgba(0,0,0,0.3);
        border-left: 6px solid #FF6B6B;
        transition: transform 0.3s;
    }
    
    .membership-card:hover {
        transform: translateY(-5px);
    }
    
    .membership-card h3 {
        color: #FF6B6B !important;
        margin-bottom: 1rem !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }
    
    .price-tag {
        color: #00b894;
        font-weight: 900;
        font-size: 2.2rem;
    }
    
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .stChatMessage {
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 22px !important;
        padding: 1.4rem !important;
        margin: 1.2rem 0 !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3) !important;
    }
    
    .stChatInput > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 32px !important;
        border: 3px solid rgba(255, 107, 107, 0.6) !important;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    .footer {
        text-align: center;
        color: white;
        padding: 2.5rem 0 1rem 0;
        margin-top: 3.5rem;
        border-top: 3px solid rgba(255, 255, 255, 0.4);
    }
    
    .footer h3 {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== CONTENT ====================
st.title("💪 FITZONE GYM")
st.markdown('<p class="subtitle">GET FIT. STAY STRONG.</p>', unsafe_allow_html=True)

# Status
if GOOGLE_API_KEY and GOOGLE_API_KEY != "YOUR_API_KEY_HERE":
    st.markdown('<div class="status-box">✅ Your Fitness Assistant is Ready!</div>', unsafe_allow_html=True)
else:
    st.error("⚠️ System Offline")
    st.stop()

# Membership cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="membership-card">
        <h3>BASIC</h3>
        <p class="price-tag">$29<span style="font-size:0.5em">/mo</span></p>
        <p>✓ Gym access<br>✓ Locker room<br>✓ Free WiFi</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="membership-card">
        <h3>PREMIUM</h3>
        <p class="price-tag">$49<span style="font-size:0.5em">/mo</span></p>
        <p>✓ All Basic<br>✓ Group classes<br>✓ Sauna</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="membership-card">
        <h3>ELITE</h3>
        <p class="price-tag">$79<span style="font-size:0.5em">/mo</span></p>
        <p>✓ All Premium<br>✓ 2 PT sessions<br>✓ Nutrition</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <span class="badge">🏋️ Modern Equipment</span>
    <span class="badge">👥 Expert Trainers</span>
    <span class="badge">📅 Flexible Classes</span>
    <span class="badge">🎯 Results Driven</span>
</div>
""", unsafe_allow_html=True)

# Chat
if 'messages' not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": """Hey! 👋 I'm Max, your fitness assistant!

I can help with:
✅ Membership plans
✅ Class schedules
✅ Gym facilities
✅ Personal training
✅ Fitness advice

What can I help you achieve today? 💪"""
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask Max anything!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("💪 Max is preparing your answer..."):
            answer = ask_trainer(prompt)
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# Footer
st.markdown("""
<div class="footer">
    <h3>💪 FITZONE GYM</h3>
    <p>123 Fitness Avenue, City Center<br>
    📞 (555) 123-4567 | ✉️ info@fitzonegym.com<br>
    ⭐⭐⭐⭐⭐ 4.7/5 Rating<br>
    ⏰ Mon-Fri 5AM-11PM | Weekends 6AM-10PM<br><br>
    🤖 AI-Powered Assistant | Portfolio Project</p>
</div>

""", unsafe_allow_html=True)

