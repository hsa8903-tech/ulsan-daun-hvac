import streamlit as st
import pandas as pd
import math
import requests
from datetime import datetime
import pytz

# --- 1. 앱 기본 설정 ---
st.set_page_config(
    page_title="울산다운1차 결로관리",
    page_icon="🏗️",
    layout="centered"
)

# --- 2. 날씨 데이터 가져오기 (Open-Meteo API / 무료, 키 불필요) ---
@st.cache_data(ttl=3600) # 1시간마다 데이터 갱신
def get_weather_data():
    # 울산 중구 다운동 인근 좌표
    lat = 35.55
    lon = 129.28
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo"
    
    try:
        response = requests.get(url)
        return response.json()
    except:
        return None

def get_weather_icon(code):
    # WMO 날씨 코드 변환
    if code == 0: return "☀️"
    elif code in [1, 2, 3]: return "⛅"
    elif code in [45, 48]: return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65]: return "🌧️"
    elif code in [71, 73, 75]: return "❄️"
    elif code >= 80: return "⛈️"
    else: return "☁️"

weather_data = get_weather_data()

# --- 3. 사이드바 (현장 정보 + 주간 예보) ---
with st.sidebar:
    st.header("🏗️ 현장 개요")
    st.info("""
    **[PROJECT]**
    **울산다운1차 아파트 건설공사**
    * **위치:** 울산 중구 다운동
    * **시공:** 우미건설(주)
    """)
    
    st.divider()
    
    # [NEW] 주간 날씨 예보 영역
    st.subheader("📅 주간 현장 날씨")
    
    if weather_data:
        daily = weather_data.get('daily', {})
        dates = daily.get('time', [])
        codes = daily.get('weather_code', [])
        max_temps = daily.get('temperature_2m_max', [])
        min_temps = daily.get('temperature_2m_min', [])
        
        # 5일치 예보만 표시
        for i in range(5):
            date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
            date_str = date_obj.strftime("%m/%d(%a)")
            icon = get_weather_icon(codes[i])
            
            # 보기 좋게 한 줄씩 표시
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:5px;">
                <span>{date_str}</span>
                <span>{icon} {min_temps[i]}°/{max_temps[i]}°</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption("Data: Open-Meteo")
    else:
        st.error("날씨 정보를 불러올 수 없습니다.")

    st.divider()
    
    # 현재 시간 표시
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    st.caption(f"Update: {now.strftime('%Y-%m-%d %H:%M')}")


# --- 4. 메인 화면 ---
st.markdown("## 🏢 Woomi Construction")
st.title("울산다운1차 결로 방지 대시보드")
st.warning("📡 인터넷 기상 데이터를 실시간으로 수신 중입니다.")

st.divider()

# --- 5. 로직 (이슬점 계산) ---
def calculate_dew_point(temp, hum):
    b = 17.62
    c = 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    dew_point = (c * gamma) / (b - gamma)
    return round(dew_point, 2)

# --- 6. 데이터 입력 (API 연동 + 수동 보정) ---
col1, col2 = st.columns(2)

# API에서 현재 날씨 가져오기 (기본값 설정)
if weather_data and 'current' in weather_data:
    current_temp = weather_data['current']['temperature_2m']
    current_hum = weather_data['current']['relative_humidity_2m']
else:
    current_temp = 25.0
    current_hum = 70.0

with col1:
    st.markdown("### 🌡️ 지하 내부")
    # 여름철 지하 온도는 보통 18~22도 사이
    underground_temp = st.slider("벽체/바닥 표면온도 (℃)", 0.0, 35.0, 18.0, step=0.5)

with col2:
    st.markdown("### ☁️ 외부 날씨")
    # API 값을 기본값(value)으로 넣어주되, 필요시 수정 가능하게 함
    ext_temp = st.number_input("현재 기온 (℃)", value=float(current_temp))
    ext_hum = st.number_input("현재 습도 (%)", value=float(current_hum))

# --- 7. 판단 및 결과 ---
ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0 

st.write("") 
st.subheader("📋 실시간 판정 결과")

if ext_dew_point >= (underground_temp - safety_margin):
    # 위험
    st.error(f"⛔ 환기 가동 중지 (OFF)")
    st.markdown(f"""
    <div style="background-color: #ffe6e6; padding: 15px; border-radius: 10px;">
        <b>[위험] 외기 유입 시 결로 발생 확정</b><br>
        - 외기 이슬점: <b>{ext_dew_point}℃</b> (지하온도 {underground_temp}℃ 보다 높음)<br>
        - 조치: 셔터/창호 밀폐 후 제습기 가동
    </div>
    """, unsafe_allow_html=True)
else:
    # 안전
    st.success(f"✅ 환기 가동 (ON)")
    st.markdown(f"""
    <div style="background-color: #e6fffa; padding: 15px; border-radius: 10px;">
        <b>[안전] 환기 시 제습 효과 있음</b><br>
        - 외기 이슬점: <b>{ext_dew_point}℃</b> (지하온도 {underground_temp}℃ 보다 낮음)<br>
        - 조치: 급/배기 팬 적극 가동
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("우미건설(주) 울산다운1차 설비팀 | v2.0")
