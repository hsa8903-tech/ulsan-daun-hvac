import streamlit as st
import math
import requests
from datetime import datetime
import pytz
import base64
import os

# --- 1. 앱 기본 설정 ---
st.set_page_config(
    page_title="울산다운2지구 우미린 결로관리",
    page_icon="🏗️",
    layout="centered"
)

# --- 2. 이미지 로딩 및 배경 설정 (핵심) ---
def get_base64_of_bin_file(bin_file):
    """이미지 파일을 읽어서 Base64 문자열로 변환"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 업로드하신 파일명 그대로 사용
img_file = "Lynn BI.png"

if os.path.exists(img_file):
    # 1) 배경 워터마크 적용 (CSS)
    bin_str = get_base64_of_bin_file(img_file)
    st.markdown(
        f"""
        <style>
        /* 메인 화면 컨테이너 */
        [data-testid="stAppViewContainer"] > .main {{
             position: relative;
        }}
        /* 가상요소(::before)를 사용하여 배경 이미지만 투명도 조절 */
        [data-testid="stAppViewContainer"] > .main::before {{
             content: "";
             position: absolute;
             top: 0;
             left: 0;
             width: 100%;
             height: 100%;
             
             /* 배경 이미지 설정 */
             background-image: url("data:image/png;base64,{bin_str}");
             background-repeat: no-repeat;
             background-position: bottom right; /* 우측 하단 배치 */
             background-size: 40%; /* 크기 조절 (화면의 40% 크기) */
             
             /* 투명도 및 레이어 설정 */
             opacity: 0.4; /* 선명도 40% */
             z-index: -1; /* 글자 뒤로 보내기 */
             pointer-events: none;
        }}
        
        /* 숫자 입력창 화살표 제거 (디자인 깔끔하게) */
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button {{ 
          -webkit-appearance: none; 
          margin: 0; 
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # 파일이 아직 안 올라갔을 때 안내
    st.toast("⚠️ 'Lynn BI.png' 파일을 GitHub에 올려주세요.", icon="FILE")


# --- 3. 날씨 데이터 (Open-Meteo API / 다운2지구) ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat = 35.561 
    lon = 129.269
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&daily=weather_code,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean&timezone=Asia%2FTokyo"
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

weather_data = get_weather_data()


# --- 4. 사이드바 설정 ---
with st.sidebar:
    st.header("🏗️ 현장 개요")
    st.info("""
    **[PROJECT]**
    **울산다운2지구 우미린**
    **더시그니처 아파트 건설공사**
    * **위치:** 울산 중구 다운동
    * **시공:** 우미건설(주)
    """)
    st.divider()
    st.subheader("📅 주간 현장 날씨")
    
    if weather_data and 'daily' in weather_data:
        daily = weather_data['daily']
        for i in range(5):
            d_date = datetime.strptime(daily['time'][i], "%Y-%m-%d").strftime("%m/%d(%a)")
            d_icon = get_weather_icon(daily['weather_code'][i])
            d_min = daily['temperature_2m_min'][i]
            d_max = daily['temperature_2m_max'][i]
            st.markdown(f"<div style='font-size:14px; margin-bottom:5px;'>{d_date} {d_icon} <b>{d_min:.1f}° / {d_max:.1f}°</b></div>", unsafe_allow_html=True)
    else:
        st.error("날씨 정보 수신 대기 중")

    st.markdown("<br><a href='https://www.weather.go.kr/w/index.do' target='_blank'><div style='background:#0056b3;color:white;padding:10px;border-radius:5px;text-align:center;'>☁️ 기상청 바로가기</div></a>", unsafe_allow_html=True)
    
    st.divider()
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    st.caption(f"Update: {now.strftime('%Y-%m-%d %H:%M')}")


# --- 5. 메인 헤더 (로고 + 타이틀) ---
col_h1, col_h2 = st.columns([1, 5])

with col_h1:
    # 2) 상단 로고 이미지 (파일이 있으면 표시)
    if os.path.exists(img_file):
        st.image(img_file, width=100) # 로고 크기 조절
    else:
        st.write("Logo")

with col_h2:
    st.markdown("<h2 style='margin-top:10px; color:#e06000;'>Woomi Construction</h2>", unsafe_allow_html=True) # 린 로고색(주황) 반영

st.title("울산다운2지구 결로 방지 대시보드")
st.warning("📡 현장 실시간 기상 데이터를 분석 중입니다.")
st.divider()


# --- 6. 데이터 입력 (소수점 1자리) ---
if weather_data and 'current' in weather_data:
    init_temp = float(weather_data['current']['temperature_2m'])
    init_hum = float(weather_data['current']['relative_humidity_2m'])
else:
    init_temp, init_hum = 25.0, 70.0

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🌡️ 지하 내부")
    underground_temp = st.slider("표면온도 (℃)", 0.0, 35.0, 18.5, step=0.1, format="%.1f")
with col2:
    st.markdown("### ☁️ 외부 날씨")
    ext_temp = st.number_input("현재 기온 (℃)", value=init_temp, step=0.1, format="%.1f")
    ext_hum = st.number_input("현재 습도 (%)", value=init_hum, step=0.5, format="%.1f")


# --- 7. 판정 로직 (Magnus Formula) ---
def calculate_dew_point(temp, hum):
    b, c = 17.62, 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    return round((c * gamma) / (b - gamma), 1)

ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0

st.write("")
st.subheader("📋 실시간 판정 결과")

if ext_dew_point >= (underground_temp - safety_margin):
    st.error(f"⛔ 환기 가동 중지 (OFF)")
    st.markdown(f"<div style='background-color:#ffe6e6;padding:15px;border-radius:10px;'><b>[위험] 결로 발생 주의</b><br>외기 이슬점: <b>{ext_dew_point}℃</b> (지하 {underground_temp}℃와 근접)<br>조치: 밀폐 후 제습기 가동</div>", unsafe_allow_html=True)
else:
    st.success(f"✅ 환기 가동 (ON)")
    st.markdown(f"<div style='background-color:#e6fffa;padding:15px;border-radius:10px;'><b>[안전] 환기 가능</b><br>외기 이슬점: <b>{ext_dew_point}℃</b> (지하 {underground_temp}℃보다 낮음)<br>조치: 적극 환기 실시</div>", unsafe_allow_html=True)


# --- 8. 내일 예보 ---
st.divider()
st.subheader("🔮 내일(익일) 환기 예보")
if weather_data and 'daily' in weather_data:
    t_max = weather_data['daily']['temperature_2m_max'][1]
    t_hum = weather_data['daily']['relative_humidity_2m_mean'][1]
    t_dew = calculate_dew_point(t_max, t_hum)
    
    c1, c2 = st.columns([1,2])
    with c1:
        st.info("내일 예상")
        st.write(f"최고: {t_max:.1f}℃")
        st.write(f"습도: {t_hum:.1f}%")
        st.write(f"이슬점: {t_dew:.1f}℃")
    with c2:
        if t_dew >= (underground_temp - safety_margin):
            st.warning("⚠️ 내일도 '환기 주의' 예상")
            st.write("내일도 습한 공기가 유입될 것으로 보입니다.")
        else:
            st.success("🆗 내일은 '적극 환기' 가능")
            st.write("내일은 공기가 건조하여 환기하기 좋습니다.")

st.divider()
st.caption("우미건설(주) 울산다운2지구 우미린더시그니처 현장 설비팀")
