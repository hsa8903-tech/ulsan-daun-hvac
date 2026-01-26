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
    # 좌표: 울산다운2지구 우미린더시그니처
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

# [수정] 새로고침 버튼 전용 콜백 함수 (오류 방지)
def refresh_data_callback():
    new_data = fetch_weather_data()
    if new_data:
        st.session_state['weather_data'] = new_data
        if 'current' in new_data:
            st.session_state['e_temp'] = float(new_data['current']['temperature_2m'])
            st.session_state['e_hum'] = float(new_data['current']['relative_humidity_2m'])
    else:
        st.toast("데이터를 불러오지 못했습니다.", icon="⚠️")

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
    
    /* 버튼 스타일 최적화 (높이 맞춤용) */
    div.stButton > button {{
        width: 100%;
        margin-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)


# --- 5. 데이터 로딩 ---
if 'weather_data' not in st.session_state:
    st.session_state['weather_data'] = fetch_weather_data()
weather_data = st.session_state['weather_data']


# --- 6. 사이드바 ---
with st.sidebar:
    st.header("🏗️ 현장 개요")
    st.info("""
    **[PROJECT]**
    **울산다운1차 아파트 건설공사**
    * **위치:** 울산 중구 다운동
    * **시공:** 우미건설(주)
    """)
    st.divider()
    st.subheader("📅 주간 현장 날씨")
    
    if weather_data and 'daily' in weather_data:
        daily = weather_data['daily']
        c1, c2, c3 = st.columns([1.2, 1.5, 1.5])
        c1.markdown("**날짜**")
        c2.markdown("**기온**")
        c3.markdown("**습도/강수**")
        
        for i in range(5):
            d_date = datetime.strptime(daily['time'][i], "%Y-%m-%d").strftime("%m/%d")
            d_icon = get_weather_icon(daily['weather_code'][i])
            d_min = daily['temperature_2m_min'][i]
            d_max = daily['temperature_2m_max'][i]
            d_hum = daily['relative_humidity_2m_mean'][i]
            d_prob = daily['precipitation_probability_max'][i]
            
            cols = st.columns([1.2, 1.5, 1.5])
            cols[0].write(f"{d_date} {d_icon}")
            cols[1].write(f"{d_min:.1f}~{d_max:.1f}°")
            
            if d_prob >= 50:
                cols[2].markdown(f"{d_hum:.0f}% <span style='color:blue'>☔{d_prob:.0f}%</span>", unsafe_allow_html=True)
            else:
                cols[2].write(f"{d_hum:.0f}%")
            
            st.markdown("<div style='margin-bottom: 5px; border-bottom: 1px solid #eee;'></div>", unsafe_allow_html=True)
    else:
        st.error("데이터 수신 대기 중")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # [수정] 기상청 링크 버튼 (깨짐 방지 및 안정성 확보)
    # st.link_button은 스트림릿 정식 기능이라 CSS 충돌 없이 깔끔하게 나옵니다.
    st.link_button("☁️ 기상청 날씨누리 접속", "https://www.weather.go.kr/w/index.do", use_container_width=True)
    
    st.divider()
    
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    st.caption(f"Update: {now.strftime('%Y-%m-%d %H:%M')}")


# --- 7. 메인 헤더 ---
if os.path.exists(logo_file):
    logo_bin = get_base64_of_bin_file(logo_file)
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: rgba(255,255,255,0.85); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="data:image/png;base64,{logo_bin}" style="height: 50px; margin-right: 15px;">
        <h2 style="margin: 0; padding-top: 5px; color: #e06000; font-family: sans-serif; letter-spacing: -1px;">Woomi Construction</h2>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("Woomi Construction")

st.markdown("""
<div style="background-color: rgba(255,255,255,0.85); padding: 15px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <h1 style='margin:0; font-size: 2rem;'>울산다운1차 결로 관리 시스템</h1>
    <p style='margin:10px 0 0 0; color: #666;'>📡 현장 실시간 기상 데이터를 분석 중입니다.</p>
</div>
""", unsafe_allow_html=True)
st.divider()


# --- 8. 데이터 입력 (높이 정렬 유지) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌡️ 지하 내부")
    # key를 통한 자동 세션 업데이트
    st.number_input("표면온도 (℃)", step=0.1, format="%.1f", key='u_temp')
    st.number_input("내부습도 (%)", step=1.0, format="%.0f", key='u_hum')
    st.info("※ 습도계 미설치 시 70% 가정")

with col2:
    st.markdown("### ☁️ 외부 날씨")
    st.number_input("현재 기온 (℃)", step=0.1, format="%.1f", key='e_temp')
    st.number_input("현재 습도 (%)", step=0.5, format="%.1f", key='e_hum')
    
    # [수정] on_click을 사용하여 새로고침 오류 원천 차단
    st.button("🔄 데이터 새로고침", on_click=refresh_data_callback, use_container_width=True)

# 변수 할당
underground_temp = st.session_state['u_temp']
underground_hum = st.session_state['u_hum']
ext_temp = st.session_state['e_temp']
ext_hum = st.session_state['e_hum']


# --- 9. 판정 로직 ---
def calculate_dew_point(temp, hum):
    b, c = 17.62, 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    return round((c * gamma) / (b - gamma), 1)

ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0
target_humidity = 70.0 

st.write("")
st.subheader("📋 실시간 제어 가이드")

# 결과창 박스 스타일
box_safe = "background-color:#e6fffa;padding:15px;border-radius:10px;"
box_warn = "background-color:#fff3cd;padding:15px;border-radius:10px;"
box_danger = "background-color:#ffe6e6;padding:15px;border-radius:10px;"

# 1. 환기 가능 여부
is_vent_safe = False
if ext_dew_point < (underground_temp - safety_margin):
    is_vent_safe = True

if is_vent_safe:
    # 안전
    st.success(f"✅ 환기: ON  |  🌀 유인휀: ON  |  ⚡ 제습기: OFF")
    st.markdown(f"""
    <div style="{box_safe}">
        <b>[안전] 적극 환기 (에너지 절약)</b><br>
        <ul style="margin-bottom:5px;">
            <li><b>메인 환기</b>: <span style="color:green; font-weight:bold;">ON (가동)</span> - 외기로 건조</li>
            <li><b>유인휀</b>: <span style="color:green; font-weight:bold;">ON (가동)</span> - 공기 순환</li>
            <li><b>제습기</b>: <span style="color:gray; font-weight:bold;">OFF (정지)</span> - ⚡전력 절약</li>
        </ul>
        <hr style="margin:10px 0; border: 0; border-top: 1px solid #b3e6c9;">
        - 외기 이슬점({ext_dew_point}℃)이 낮아 환기만으로 충분합니다.
    </div>
    """, unsafe_allow_html=True)
else:
    # 환기 불가
    if underground_hum > target_humidity:
        # 위험
        st.error(f"⛔ 환기: OFF  |  🌀 유인휀: ON  |  💧 제습기: ON")
        st.markdown(f"""
        <div style="{box_danger}">
            <b>[위험] 밀폐 및 강제 제습</b><br>
            <ul style="margin-bottom:5px;">
                <li><b>메인 환기</b>: <span style="color:red; font-weight:bold;">OFF (밀폐)</span> - 습한 외기 차단</li>
                <li><b>유인휀</b>: <span style="color:blue; font-weight:bold;">ON (가동)</span> - 제습 효율 증대</li>
                <li><b>제습기</b>: <span style="color:blue; font-weight:bold;">ON (가동)</span> - 내부습도 {underground_hum:.0f}% (높음)</li>
            </ul>
            <hr style="margin:10px 0; border: 0; border-top: 1px solid #ffcccc;">
            - 외기 유입 시 결로가 발생하며, 내부도 습하므로 기계 제습이 필요합니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        # 주의 (절전)
        st.warning(f"⛔ 환기: OFF  |  🌀 유인휀: OFF  |  ⚡ 제습기: OFF")
        st.markdown(f"""
        <div style="{box_warn}">
            <b>[주의] 밀폐 유지 (전력 절감 모드)</b><br>
            <ul style="margin-bottom:5px;">
                <li><b>메인 환기</b>: <span style="color:red; font-weight:bold;">OFF (밀폐)</span> - 습한 외기 차단</li>
                <li><b>유인휀</b>: <span style="color:gray; font-weight:bold;">OFF (정지)</span> - ⚡전력 절약</li>
                <li><b>제습기</b>: <span style="color:gray; font-weight:bold;">OFF (정지)</span> - ⚡내부습도 {underground_hum:.0f}% (양호)</li>
            </ul>
            <hr style="margin:10px 0; border: 0; border-top: 1px solid #ffeeba;">
            - 외기는 습하지만 내부는 양호합니다. 모든 장비를 멈추고 현상을 유지하십시오.
        </div>
        """, unsafe_allow_html=True)


# --- 10. 내일 예보 ---
st.divider()
st.subheader("🔮 내일(익일) 환기 예보")
if weather_data and 'daily' in weather_data:
    t_max = weather_data['daily']['temperature_2m_max'][1]
    t_hum = weather_data['daily']['relative_humidity_2m_mean'][1]
    t_prob = weather_data['daily']['precipitation_probability_max'][1]
    t_dew = calculate_dew_point(t_max, t_hum)
    
    # 예보 박스 스타일
    box_forecast = "background-color: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: 100%;"
    
    c1, c2 = st.columns([1,2])
    with c1:
        st.markdown(f"""
        <div style="{box_forecast}">
            <strong style="color:#0056b3;">내일 예상</strong><br><br>
            최고: <b>{t_max:.1f}℃</b><br>습도: <b>{t_hum:.1f}%</b><br>강수: <b>{t_prob:.0f}%</b><br>이슬점: <b>{t_dew:.1f}℃</b>
        </div>""", unsafe_allow_html=True)
    with c2:
        if t_dew >= (underground_temp - safety_margin):
            st.markdown(f"<div style='{box_forecast} border-left: 5px solid #ffc107;'><strong style='color:#d39e00;'>⚠️ 내일도 '환기 주의' 예상</strong><br><br>내일도 습하거나 비 소식이 있을 수 있습니다.<br>지하 온도를 확인하며 밀폐 관리를 유지하세요.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='{box_forecast} border-left: 5px solid #17a2b8;'><strong style='color:#138496;'>🆗 내일은 '적극 환기' 가능</strong><br><br>내일은 비교적 건조할 것으로 예상됩니다.<br>오전부터 적극적으로 환기하여 지하를 말리십시오.</div>", unsafe_allow_html=True)

st.divider()
st.caption("우미건설(주) 울산다운1차 현장 설비팀")
