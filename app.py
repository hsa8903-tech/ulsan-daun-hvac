import streamlit as st
import math
import requests
from datetime import datetime, timedelta
import pytz

# --- 1. 앱 기본 설정 및 CSS 적용 ---
st.set_page_config(
    page_title="울산다운2지구 우미린 결로관리",
    page_icon="🏗️",
    layout="centered"
)

# [CSS 커스텀] 로고 배치 및 배경 워터마크 설정
# 우미건설 브랜드 이미지를 우측 하단에 40% 투명도로 배치
st.markdown(
    """
    <style>
    /* 메인 컨테이너 설정 */
    [data-testid="stAppViewContainer"] > .main {
         position: relative;
    }

    /* 배경 이미지 가상 요소 생성 (워터마크 효과) */
    [data-testid="stAppViewContainer"] > .main::before {
         content: "";
         position: absolute;
         top: 0;
         left: 0;
         width: 100%;
         height: 100%;
         /* 우미건설 브랜드 이미지 URL (필요시 변경 가능) */
         background-image: url('https://www.woomi.co.kr/images/sub/introduce/ci_bg.jpg');
         background-repeat: no-repeat;
         background-position: bottom right; /* 우측 하단 배치 */
         background-size: 70%; /* 이미지 크기 조절 */
         opacity: 0.4; /* 선명도 40% 설정 */
         z-index: -1; /* 컨텐츠 뒤로 보내기 */
         pointer-events: none; # 클릭 통과
    }
    
    /* 숫자 입력창 화살표 숨기기 (깔끔하게) */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
      -webkit-appearance: none; 
      margin: 0; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 2. 날씨 데이터 가져오기 (Open-Meteo API) ---
@st.cache_data(ttl=3600)
def get_weather_data():
    # [수정] 울산다운2지구 우미린더시그니처아파트 인근 좌표 반영
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

# 이슬점 계산 함수
def calculate_dew_point(temp, hum):
    b = 17.62
    c = 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    dew_point = (c * gamma) / (b - gamma)
    # [수정] 소수점 첫째 자리까지 반환
    return round(dew_point, 1)

weather_data = get_weather_data()

# --- 3. 사이드바 ---
with st.sidebar:
    st.header("🏗️ 현장 개요")
    st.info("""
    **[PROJECT]**
    **울산다운2지구 우미린**
    **더시그니처 아파트 건설공사**
    * **위치:** 울산 중구 다운동 (다운2지구)
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
            # [수정] 주간예보도 소수점 1자리까지 표시
            t_min = f"{min_temps[i]:.1f}"
            t_max = f"{max_temps[i]:.1f}"
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:5px;">
                <span>{date_str}</span>
                <span>{icon} {t_min}° / {t_max}°</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption("Data: Open-Meteo (다운2지구 기준)")
    else:
        st.error("날씨 정보를 불러올 수 없습니다.")

    st.write("")
    
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


# --- 4. 메인 화면 헤더 (로고 적용) ---
# [수정] 건물 이모지 대신 우미건설 CI 로고 이미지 적용
st.markdown(
    """
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Woomi_Construction_logo.svg/300px-Woomi_Construction_logo.svg.png" alt="Woomi Logo" height="40" style="margin-right: 10px;">
        <h2 style="margin: 0; color: #003478;">Woomi Construction</h2>
    </div>
    """, 
    unsafe_allow_html=True
)
st.title("울산다운2지구 결로 방지 대시보드")
st.warning("📡 현장 인근 기상 데이터를 실시간으로 수신 중입니다.")

st.divider()

# --- 5. 데이터 입력 (소수점 첫째 자리 적용) ---
col1, col2 = st.columns(2)

if weather_data and 'current' in weather_data:
    # [수정] 초기값도 소수점 유지
    init_temp = float(weather_data['current']['temperature_2m'])
    init_hum = float(weather_data['current']['relative_humidity_2m'])
else:
    init_temp = 25.0
    init_hum = 70.0

with col1:
    st.markdown("### 🌡️ 지하 내부")
    # [수정] step=0.1 및 format="%.1f" 적용하여 소수점 입력 가능
    underground_temp = st.slider("벽체/바닥 표면온도 (℃)", 0.0, 35.0, 18.5, step=0.1, format="%.1f")

with col2:
    st.markdown("### ☁️ 외부 날씨")
    # [수정] step=0.1 및 format="%.1f" 적용
    ext_temp = st.number_input("현재 기온 (℃)", value=init_temp, step=0.1, format="%.1f")
    ext_hum = st.number_input("현재 습도 (%)", value=init_hum, step=0.5, format="%.1f")

# --- 6. 실시간 판정 결과 ---
ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0 # [수정] 안전율도 소수점 적용

st.write("") 
st.subheader("📋 실시간 판정 결과")

# 결과 표시에도 f-string으로 소수점 1자리 적용 ({value:.1f})
if ext_dew_point >= (underground_temp - safety_margin):
    # 위험
    st.error(f"⛔ 환기 가동 중지 (OFF)")
    st.markdown(f"""
    <div style="background-color: #ffe6e6; padding: 15px; border-radius: 10px;">
        <b>[위험] 외기 유입 시 결로 발생 확정</b><br>
        - 외기 이슬점: <b>{ext_dew_point:.1f}℃</b> (지하 {underground_temp:.1f}℃ 와 유사/높음)<br>
        - 조치: 셔터/창호 밀폐 후 제습기 가동
    </div>
    """, unsafe_allow_html=True)
else:
    # 안전
    st.success(f"✅ 환기 가동 (ON)")
    st.markdown(f"""
    <div style="background-color: #e6fffa; padding: 15px; border-radius: 10px;">
        <b>[안전] 환기 시 제습 효과 있음</b><br>
        - 외기 이슬점: <b>{ext_dew_point:.1f}℃</b> (지하 {underground_temp:.1f}℃ 보다 낮음)<br>
        - 조치: 급/배기 팬 적극 가동
    </div>
    """, unsafe_allow_html=True)

# --- 7. 내일 예정 판정 ---
st.divider()
st.subheader("🔮 내일(익일) 환기 예보")

if weather_data and 'daily' in weather_data:
    daily = weather_data['daily']
    tom_max_temp = daily['temperature_2m_max'][1]
    tom_mean_hum = daily.get('relative_humidity_2m_mean', [75, 75])[1] 
    
    tom_rep_temp = tom_max_temp
    tom_dew_point = calculate_dew_point(tom_rep_temp, tom_mean_hum)
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.info(f"내일 예상 날씨")
        # [수정] 예상 수치도 소수점 표시
        st.write(f"최고: {tom_max_temp:.1f}℃")
        st.write(f"평균습도: {tom_mean_hum:.1f}%")
        st.write(f"예상 이슬점: {tom_dew_point:.1f}℃")
        
    with col_b:
        if tom_dew_point >= (underground_temp - safety_margin):
            st.warning("⚠️ 내일도 '환기 주의' 예상")
            st.write(f"내일 낮 시간대 외부 공기가 습할 것으로 보입니다.\n지하 온도가 {underground_temp:.1f}℃로 유지된다면 결로 위험이 있습니다.")
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
        우미건설(주) 울산다운2지구 우미린더시그니처 현장 설비팀<br>
        Copyright © 2026 Ulsan Daun 2nd Dist. Site. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
