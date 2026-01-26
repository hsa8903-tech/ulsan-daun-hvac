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

img_file = "Lynn BI.png"

# --- 3. CSS 스타일 ---
if os.path.exists(img_file):
    bin_str = get_base64_of_bin_file(img_file)
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{ position: relative; }}
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
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- 4. 날씨 데이터 가져오기 (API) ---
# 좌표: 울산다운2지구 우미린더시그니처 (데이터 정확도 위해)
def fetch_weather_data():
    lat = 35.5617
    lon = 129.2676
    # [수정] precipitation_probability_max (강수확률) 추가 요청
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

# 데이터 초기 로딩 또는 새로고침
if 'weather_data' not in st.session_state:
    st.session_state['weather_data'] = fetch_weather_data()

weather_data = st.session_state['weather_data']


# --- 5. 사이드바 ---
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
    
    # [수정] 주간 날씨에 '강수확률(☔)' 추가 표시
    if weather_data and 'daily' in weather_data:
        daily = weather_data['daily']
        for i in range(5):
            d_date = datetime.strptime(daily['time'][i], "%Y-%m-%d").strftime("%m/%d(%a)")
            d_icon = get_weather_icon(daily['weather_code'][i])
            d_min = daily['temperature_2m_min'][i]
            d_max = daily['temperature_2m_max'][i]
            d_hum = daily['relative_humidity_2m_mean'][i]       # 습도
            d_prob = daily['precipitation_probability_max'][i]  # 강수확률
            
            # 날짜 | 아이콘 | 최저/최고 | 습도/강수확률
            # 모바일 화면 고려하여 줄바꿈 배치
            st.markdown(f"""
            <div style='font-size:13px; margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:2px;'>
                    <span style='font-weight:bold;'>{d_date} {d_icon}</span>
                    <span>🌡️ {d_min:.0f}° ~ {d_max:.0f}°</span>
                </div>
                <div style='display:flex; justify-content:flex-end; color:#555; font-size:12px;'>
                    <span style='margin-right:8px;'>💧습도 {d_hum:.0f}%</span>
                    <span style='color:{'#0066cc' if d_prob >= 50 else '#555'};'>☔강수 {d_prob:.0f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("데이터 수신 대기 중")

    st.markdown("""
    <br>
    <a href="https://www.weather.go.kr/w/index.do" target="_blank" style="text-decoration:none;">
        <div style="background-color:#0056b3; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold; font-family:'Malgun Gothic', sans-serif;">
            ☁️ 기상청 날씨누리 접속
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    st.divider()
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    st.caption(f"Update: {now.strftime('%Y-%m-%d %H:%M')}")


# --- 6. 메인 헤더 ---
if os.path.exists(img_file):
    logo_bin = get_base64_of_bin_file(img_file)
    header_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{logo_bin}" style="height: 50px; margin-right: 15px;">
        <h2 style="margin: 0; padding-top: 5px; color: #e06000; font-family: sans-serif; letter-spacing: -1px;">
            Woomi Construction
        </h2>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.title("Woomi Construction")

st.title("울산다운1차 결로 방지 대시보드")
st.warning("📡 현장 실시간 기상 데이터를 분석 중입니다.")
st.divider()


# --- 7. 데이터 입력 및 새로고침 ---
if weather_data and 'current' in weather_data:
    api_temp = float(weather_data['current']['temperature_2m'])
    api_hum = float(weather_data['current']['relative_humidity_2m'])
else:
    api_temp, api_hum = 25.0, 70.0

if 'u_temp' not in st.session_state: st.session_state['u_temp'] = 18.5
if 'e_temp' not in st.session_state: st.session_state['e_temp'] = api_temp
if 'e_hum' not in st.session_state: st.session_state['e_hum'] = api_hum

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌡️ 지하 내부")
    underground_temp = st.slider("표면온도 (℃)", 0.0, 35.0, key='u_temp', step=0.1, format="%.1f")

with col2:
    st.markdown("### ☁️ 외부 날씨")
    if st.button("🔄 데이터 새로고침", help="기상청 최신 데이터로 초기화합니다"):
        new_data = fetch_weather_data()
        st.session_state['weather_data'] = new_data
        if new_data and 'current' in new_data:
            st.session_state['e_temp'] = float(new_data['current']['temperature_2m'])
            st.session_state['e_hum'] = float(new_data['current']['relative_humidity_2m'])
        st.rerun()
        
    ext_temp = st.number_input("현재 기온 (℃)", key='e_temp', step=0.1, format="%.1f")
    ext_hum = st.number_input("현재 습도 (%)", key='e_hum', step=0.5, format="%.1f")


# --- 8. 판정 로직 (유인휀 포함) ---
def calculate_dew_point(temp, hum):
    b, c = 17.62, 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    return round((c * gamma) / (b - gamma), 1)

ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0

st.write("")
st.subheader("📋 실시간 판정 결과")

if ext_dew_point >= (underground_temp - safety_margin):
    # 위험
    st.error(f"⛔ 환기 시스템: 정지 (OFF)  |  🌀 유인휀: 가동 (ON)")
    st.markdown(f"""
    <div style="background-color:#ffe6e6;padding:15px;border-radius:10px;">
        <b>[위험] 결로 발생 주의</b><br>
        <ul style="margin-bottom:5px;">
            <li><b>메인 환기(급/배기)</b>: <span style="color:red; font-weight:bold;">가동 중지 (OFF)</span> - 습한 외기 차단</li>
            <li><b>유인휀(Jet Fan)</b>: <span style="color:blue; font-weight:bold;">가동 (ON)</span> - 내부 공기 순환</li>
        </ul>
        <hr style="margin:10px 0; border: 0; border-top: 1px solid #ffcccc;">
        - 외기 이슬점: <b>{ext_dew_point}℃</b> (지하 {underground_temp}℃와 근접)<br>
        - 조치: 셔터/창호 밀폐 후 제습기 가동
    </div>
    """, unsafe_allow_html=True)
else:
    # 안전
    st.success(f"✅ 환기 시스템: 가동 (ON)  |  🌀 유인휀: 가동 (ON)")
    st.markdown(f"""
    <div style="background-color:#e6fffa;padding:15px;border-radius:10px;">
        <b>[안전] 적극 환기 권장</b><br>
        <ul style="margin-bottom:5px;">
            <li><b>메인 환기(급/배기)</b>: <span style="color:green; font-weight:bold;">가동 (ON)</span></li>
            <li><b>유인휀(Jet Fan)</b>: <span style="color:green; font-weight:bold;">가동 (ON)</span></li>
        </ul>
        <hr style="margin:10px 0; border: 0; border-top: 1px solid #b3e6c9;">
        - 외기 이슬점: <b>{ext_dew_point}℃</b> (지하 {underground_temp}℃보다 낮음)<br>
        - 조치: 급/배기 팬 적극 가동하여 습기 배출
    </div>
    """, unsafe_allow_html=True)


# --- 9. 내일 예보 (습도/강수확률 포함) ---
st.divider()
st.subheader("🔮 내일(익일) 환기 예보")
if weather_data and 'daily' in weather_data:
    t_max = weather_data['daily']['temperature_2m_max'][1]
    t_hum = weather_data['daily']['relative_humidity_2m_mean'][1]
    # [수정] 내일 강수확률 추가
    t_prob = weather_data['daily']['precipitation_probability_max'][1]
    
    t_dew = calculate_dew_point(t_max, t_hum)
    
    c1, c2 = st.columns([1,2])
    with c1:
        st.info("내일 예상")
        st.write(f"최고: {t_max:.1f}℃")
        st.write(f"습도: {t_hum:.1f}%")
        st.write(f"강수확률: {t_prob:.0f}%")
        st.write(f"이슬점: {t_dew:.1f}℃")
    with c2:
        if t_dew >= (underground_temp - safety_margin):
            st.warning("⚠️ 내일도 '환기 주의' 예상")
            st.write("내일도 습하거나 비 소식이 있을 수 있습니다.\n지하 온도를 확인하며 밀폐 관리를 유지하세요.")
        else:
            st.success("🆗 내일은 '적극 환기' 가능")
            st.write("내일은 비교적 건조할 것으로 예상됩니다.\n오전부터 적극적으로 환기하여 지하를 말리십시오.")

st.divider()
st.caption("우미건설(주) 울산다운1차 현장 설비팀")
