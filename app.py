import streamlit as st
import math
import requests
from datetime import datetime
import pytz
import base64
import os

# --- 1. 앱 기본 설정 ---
st.set_page_config(
    page_title="울산다운1차 결로관리",
    page_icon="🏗️",
    layout="centered"
)

# --- 2. 이미지 처리 함수 ---
def get_base64_of_bin_file(bin_file):
    """이미지 파일을 읽어서 Base64 문자열로 변환"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 파일명 설정 (GitHub에 이 이름으로 파일을 올려주세요)
bg_file = "bg.png"       # 배경 사진
logo_file = "Lynn BI.png" # 로고

# --- 3. CSS 스타일 (배경 투명도 70% 적용) ---
css_code = """
<style>
/* 숫자 입력창 화살표 제거 */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
"""

if os.path.exists(bg_file):
    bin_str = get_base64_of_bin_file(bg_file)
    css_code += f"""
    /* 앱 메인 화면 설정 */
    [data-testid="stAppViewContainer"] > .main {{
        position: relative;
    }}
    
    /* 가상 요소(::before)로 배경 이미지 적용 (글자에는 영향 없음) */
    [data-testid="stAppViewContainer"] > .main::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        
        /* [핵심] 투명도 70% 적용 (불투명도 0.3) */
        /* 숫자가 낮을수록 배경이 연해지고 글씨가 잘 보입니다 */
        opacity: 0.3; 
        z-index: -1;
    }}
    """
else:
    # 배경 파일이 없을 때 (기존 워터마크 스타일)
    if os.path.exists(logo_file):
        logo_bin = get_base64_of_bin_file(logo_file)
        css_code += f"""
        [data-testid="stAppViewContainer"] > .main::before {{
             content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
             background-image: url("data:image/png;base64,{logo_bin}");
             background-repeat: no-repeat;
             background-position: bottom right;
             background-size: 40%;
             opacity: 0.1;
             z-index: -1;
             pointer-events: none;
        }}
        """

css_code += "</style>"
st.markdown(css_code, unsafe_allow_html=True)


# --- 4. 날씨 데이터 가져오기 (API) ---
# 좌표: 울산다운2지구 우미린더시그니처
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
