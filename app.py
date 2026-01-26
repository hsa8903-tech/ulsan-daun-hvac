import streamlit as st
import math
import requests
from datetime import datetime, timedelta
import pytz

# --- 1. 앱 기본 설정 ---
st.set_page_config(
    page_title="울산다운1차 결로관리",
    page_icon="🏗️",
    layout="centered"
)

# --- 2. 날씨 데이터 가져오기 (Open-Meteo API) ---
@st.cache_data(ttl=3600)
def get_weather_data():
    lat = 35.55 # 울산 다운동 좌표
    lon = 129.28
    # 내일 예측을 위해 daily 변수에 습도 평균(relative_humidity_2m_mean) 추가 요청
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

# 이슬점 계산 함수
def calculate_dew_point(temp, hum):
    b = 17.62
    c = 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    dew_point = (c * gamma) / (b - gamma)
    return round(dew_point) # 소수점 제거 (반올림)

weather_data = get_weather_data()

# --- 3. 사이드바 (현장 정보 + 주간 예보 + 기상청 배너) ---
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
    
    if weather_data:
        daily = weather_data.get('daily', {})
        dates = daily.get('time', [])
        codes = daily.get('weather_code', [])
        max_temps = daily.get('temperature_2m_max', [])
        min_temps = daily.get('temperature_2m_min', [])
        
        for i in range(5):
            date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
            date_str = date_obj.strftime("%m/%d(%a)")
            icon = get_weather_icon(codes[i])
            # 소수점 없이 정수로 표시
            t_min = int(round(min_temps[i]))
            t_max = int(round(max_temps[i]))
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:5px;">
                <span>{date_str}</span>
                <span>{icon} {t_min}° / {t_max}°</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption("Data: Open-Meteo")
    else:
        st.error("날씨 정보를 불러올 수 없습니다.")

    st.write("") # 여백
    
    # [NEW] 기상청 배너 링크
    st.markdown("""
    <a href="https://www.weather.go.kr/w/index.do" target="_blank" style="text-decoration:none;">
        <div style="background-color:#0056b3; color:white; padding:10px; border-radius:5px; text-align:center; font-weight:bold;">
            ☁️ 기상청 날씨누리 접속
        </div>
    </a>
    """, unsafe_allow_html=True)

    st.divider()
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    st.caption(f"Update: {now.strftime('%Y-%m-%d %H:%M')}")


# --- 4. 메인 화면 ---
st.markdown("## 🏢 Woomi Construction")
st.title("울산다운1차 결로 방지 대시보드")
st.warning("📡 인터넷 기상 데이터를 실시간으로 수신 중입니다.")

st.divider()

# --- 5. 데이터 입력 (소수점 제거) ---
col1, col2 = st.columns(2)

# API 초기값 로딩
if weather_data and 'current' in weather_data:
    init_temp = int(round(weather_data['current']['temperature_2m']))
    init_hum = int(round(weather_data['current']['relative_humidity_2m']))
else:
    init_temp = 25
    init_hum = 70

with col1:
    st.markdown("### 🌡️ 지하 내부")
    # step=1로 설정하여 소수점 제거
    underground_temp = st.slider("벽체/바닥 표면온도 (℃)", 0, 35, 18, step=1)

with col2:
    st.markdown("### ☁️ 외부 날씨")
    # 정수형(int) 입력 및 표시 (format="%d")
    ext_temp = st.number_input("현재 기온 (℃)", value=init_temp, step=1, format="%d")
    ext_hum = st.number_input("현재 습도 (%)", value=init_hum, step=1, format="%d")

# --- 6. 실시간 판정 결과 ---
ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2 # 정수형

st.write("") 
st.subheader("📋 실시간 판정 결과")

if ext_dew_point >= (underground_temp - safety_margin):
    # 위험
    st.error(f"⛔ 환기 가동 중지 (OFF)")
    st.markdown(f"""
    <div style="background-color: #ffe6e6; padding: 15px; border-radius: 10px;">
        <b>[위험] 외기 유입 시 결로 발생 확정</b><br>
        - 외기 이슬점: <b>{ext_dew_point}℃</b> (지하 {underground_temp}℃ 와 유사/높음)<br>
        - 조치: 셔터/창호 밀폐 후 제습기 가동
    </div>
    """, unsafe_allow_html=True)
else:
    # 안전
    st.success(f"✅ 환기 가동 (ON)")
    st.markdown(f"""
    <div style="background-color: #e6fffa; padding: 15px; border-radius: 10px;">
        <b>[안전] 환기 시 제습 효과 있음</b><br>
        - 외기 이슬점: <b>{ext_dew_point}℃</b> (지하 {underground_temp}℃ 보다 낮음)<br>
        - 조치: 급/배기 팬 적극 가동
    </div>
    """, unsafe_allow_html=True)

# --- 7. [NEW] 내일 예정 판정 ---
st.divider()
st.subheader("🔮 내일(익일) 환기 예보")

if weather_data and 'daily' in weather_data:
    # 내일 데이터 추출 (Index 1)
    daily = weather_data['daily']
    tom_max_temp = daily['temperature_2m_max'][1]
    tom_min_temp = daily['temperature_2m_min'][1]
    # 평균 습도 (데이터가 없으면 75% 가정)
    tom_mean_hum = daily.get('relative_humidity_2m_mean', [75, 75])[1] 
    
    # 내일의 대표 온도 (낮 최고기온 기준 - 보수적 접근)
    tom_rep_temp = tom_max_temp
    
    # 내일 예상 이슬점
    tom_dew_point = calculate_dew_point(tom_rep_temp, tom_mean_hum)
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.info(f"내일 예상 날씨")
        st.write(f"최고: {int(round(tom_max_temp))}℃")
        st.write(f"평균습도: {int(round(tom_mean_hum))}%")
        st.write(f"예상 이슬점: {tom_dew_point}℃")
        
    with col_b:
        if tom_dew_point >= (underground_temp - safety_margin):
            st.warning("⚠️ 내일도 '환기 주의' 예상")
            st.write(f"내일 낮 시간대 외부 공기가 습할 것으로 보입니다.\n지하 온도가 {underground_temp}℃로 유지된다면 결로 위험이 있습니다.")
        else:
            st.success("🆗 내일은 '적극 환기' 가능")
            st.write(f"내일 외부 공기는 건조할 것으로 예상됩니다.\n오전부터 적극적으로 환기하여 지하를 말리십시오.")

else:
    st.caption("내일 예보 데이터를 불러오지 못했습니다.")

# --- 8. 푸터 ---
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: grey; font-size: 12px;">
        우미건설(주) 울산다운1차 현장사무소 설비팀<br>
        Copyright © 2026 Ulsan Daun 1st Site Facilities Team. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
