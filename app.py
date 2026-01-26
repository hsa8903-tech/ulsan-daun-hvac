import streamlit as st
import math
import requests
from datetime import datetime
import pytz
import base64
import os
from PIL import Image

# --- 1. 앱 기본 설정 ---
icon_file = "Lynn BI.png"
page_icon = "🏗️" # 기본값

if os.path.exists(icon_file):
    try:
        page_icon = Image.open(icon_file)
    except:
        pass

st.set_page_config(
    page_title="울산다운1차 결로관리",
    page_icon=page_icon,
    layout="centered"
)

# --- 2. 초기값(Session State) 설정 ---
if 'u_temp' not in st.session_state: st.session_state['u_temp'] = 18.5
if 'u_hum' not in st.session_state: st.session_state['u_hum'] = 60.0
if 'e_temp' not in st.session_state: st.session_state['e_temp'] = 25.0
if 'e_hum' not in st.session_state: st.session_state['e_hum'] = 70.0

# --- 3. 유틸리티 함수 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def fetch_weather_data():
    lat = 35.5617
    lon = 129.2676
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&daily=weather_code,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,precipitation_probability_max&timezone=Asia%2FTokyo"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return None

def get_weather_icon(code):
    if code == 0: return "☀️"
    elif code in [1, 2, 3]: return "⛅"
    elif code in [45, 48]: return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65]: return "🌧️"
    elif code in [71, 73, 75]: return "❄️"
    elif code >= 80: return "⛈️"
    else: return "☁️"

# --- 4. CSS 스타일 ---
bg_file = "bg.png"
logo_file = "Lynn BI.png"
bg_css = ""

if os.path.exists(bg_file):
    bin_str = get_base64_of_bin_file(bg_file)
    bg_css = f"""
    [data-testid="stAppViewContainer"] > .main::before {{
         content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
         background-image: url("data:image/png;base64,{bin_str}");
         background-repeat: no-repeat;
         background-position: bottom right;
         background-size: 40%;
         opacity: 0.4;
         z-index: -1;
         pointer-events: none;
    }}
    """

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{ position: relative; }}
    {bg_css}
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
    .weather-row {{ font-size: 14px; margin-bottom: 5px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
    
    /* [수정] 버튼 스타일 최적화 (높이 맞춤용) */
    div.stButton > button {{
        width: 100%;
        margin-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)


# --- 5. 데이터 로딩 ---
if 'weather_data'
