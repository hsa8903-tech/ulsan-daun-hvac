import streamlit as st
import math
import requests
from datetime import datetime
import pytz
import base64
import os
from PIL import Image

# --- 1. 앱 기본 설정 ---
# 아이콘 설정
icon_file = "Lynn BI.png"
page_icon = "🏗️"
if os.path.exists(icon_file):
    try:
        page_icon = Image.open(icon_file)
    except:
        pass

st.set_page_config(
    page_title="울산다운1차 결로관리", # 브라우저 탭 이름
    page_icon=page_icon,
    layout="centered"
)

# --- 2. 이미지 처리 함수 ---
def get_base64_of_bin_file(bin_file):
    """이미지 파일을 읽어서 Base64 문자열로 변환"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_file = "bg.png"       
logo_file = "Lynn BI.png" 

# --- 3. CSS 스타일 ---
bg_css = ""
if os.path.exists(img_file):
    bin_str = get_base64_of_bin_file(img_file)
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

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{ position: relative; }}
    {bg_css}
    
    /* 숫자 입력창 화살표 제거 */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}
    
    /* 주간 날씨 텍스트 크기 조정 */
    .weather-row {{ font-size: 14px; margin-bottom: 5px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
    </style>
    """,
    unsafe_allow_html=True
)

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
    
    if weather_data and 'daily' in weather_data:
        daily = weather_data['daily']
        
        # 헤더
        c1, c2, c3 = st.columns([1.2, 1.5, 1.5]) # 기온 컬럼 너비 확보
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
            # [수정] 소수점 1자리 표기 (:.1f)
            cols[1].write(f"{d_min:.1f}~{d_max:.1f}°")
            
            if d_prob >= 50:
                cols[2].markdown(f"{d_hum:.0f}% <span style='color:blue'>☔{d_prob:.0f}%</span>", unsafe_allow_html=True)
            else:
                cols[2].write(f"{d_hum:.0f}%")
            
            st.markdown("<div style='margin-bottom: 5px; border-bottom: 1px solid #eee;'></div>", unsafe_allow_html=True)

    else:
        st.error("데이터 수신 대기 중")

    st.markdown("""
    <br>
    <a href="https://www.weather.go.kr/w/index.do" target="_blank" style="text-decoration:none;">
        <div style="background-color:#0056b3; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold;">
            ☁️ 기상청 날씨누리 접속
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    st.divider()
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    st.caption(f"Update: {now.strftime('%Y-%m-%d %H:%M')}")


# --- 6. 메인 헤더 ---
if os.path.exists(logo_file):
    logo_bin = get_base64_of_bin_file(logo_file)
    header_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: rgba(255,255,255,0.85); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="data:image/png;base64,{logo_bin}" style="height: 50px; margin-right: 15px;">
        <h2 style="margin: 0; padding-top: 5px; color: #e06000; font-family: sans-serif; letter-spacing: -1px;">
            Woomi Construction
        </h2>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.title("Woomi Construction")

# [수정] 타이틀 변경: 결로 관리 시스템
st.markdown("""
<div style="background-color: rgba(255,255,255,0.85); padding: 15px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <h1 style='margin:0; font-size: 2rem;'>울산다운1차 결로 관리 시스템</h1>
    <p style='margin:10px 0 0 0; color: #666;'>📡 현장 실시간 기상 데이터를 분석 중입니다.</p>
</div>
""", unsafe_allow_html=True)
st.divider()


# --- 7. 데이터 입력 (내부 표기 수정) ---
if weather_data and 'current' in weather_data:
    api_temp = float(weather_data['current']['temperature_2m'])
    api_hum = float(weather_data['current']['relative_humidity_2m'])
else:
    api_temp, api_hum = 25.0, 70.0

if 'u_temp' not in st.session_state: st.session_state['u_temp'] = 18.5
if 'u_hum' not in st.session_state: st.session_state['u_hum'] = 60.0 
if 'e_temp' not in st.session_state: st.session_state['e_temp'] = api_temp
if 'e_hum' not in st.session_state: st.session_state['e_hum'] = api_hum

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌡️ 지하 내부")
    # [수정] 슬라이더 제거 -> 외부 날씨와 동일한 숫자 입력창(Number Input)으로 변경
    underground_temp = st.number_input("표면온도 (℃)", value=st.session_state['u_temp'], step=0.1, format="%.1f", key='u_temp_input')
    underground_hum = st.number_input("내부습도 (%)", value=st.session_state['u_hum'], step=1.0, format="%.0f", key='u_hum_input')
    
    # 세션 스테이트 업데이트 (입력값 유지)
    st.session_state['u_temp'] = underground_temp
    st.session_state['u_hum'] = underground_hum
    
    st.caption("※ 습도계가 없다면 70%로 설정하세요.")

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


# --- 8. 판정 로직 (유인휀 추가) ---
def calculate_dew_point(temp, hum):
    b, c = 17.62, 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    return round((c * gamma) / (b - gamma), 1)

ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0
target_humidity = 70.0 

st.write("")
st.subheader("📋 실시간 제어 가이드")

# 1. 환기 가능 여부 판단
is_vent_safe = False
if ext_dew_point < (underground_temp - safety_margin):
    is_vent_safe = True

# 2. 결과 출력
if is_vent_safe:
    # [상황 1] 환기 가능 -> 환기 ON / 유인휀 ON / 제습기 OFF
    # [수정] 유인휀 표시 추가
    st.success(f"✅ 환기: ON  |  🌀 유인휀: ON  |  ⚡ 제습기: OFF")
    st.markdown(f"""
    <div style="background-color:#e6fffa;padding:15px;border-radius:10px;">
        <b>[안전] 적극 환기 (에너지 절약)</b><br>
        <ul style="margin-bottom:5px;">
            <li><b>메인 환기</b>: <span style="color:green; font-weight:bold;">ON (가동)</span> - 외기로 건조</li>
            <li><b>유인휀</b>: <span style="color:green; font-weight:bold;">ON (가동)</span> - 공기 순환</li>
            <li><b>제습기</b>: <span style="color:gray; font-weight:bold;">OFF (정지)</span> - ⚡불필요한 전력 낭비 방지</li>
        </ul>
        <hr style="margin:10px 0; border: 0; border-top: 1px solid #b3e6c9;">
        - 외기 이슬점({ext_dew_point}℃)이 낮아 환기만으로 충분합니다.
    </div>
    """, unsafe_allow_html=True)

else:
    # [상황 2] 환기 불가
    if underground_hum > target_humidity:
        # [2-A] 내부 습함 -> 환기 OFF / 유인휀 ON / 제습기 ON
        # [수정] 유인휀 표시 추가 (제습 효율 위해 가동)
        st.error(f"⛔ 환기: OFF  |  🌀 유인휀: ON  |  💧 제습기: ON")
        st.markdown(f"""
        <div style="background-color:#ffe6e6;padding:15px;border-radius:10px;">
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
        # [2-B] 내부 건조함 -> 환기 OFF / 유인휀 OFF / 제습기 OFF
        # [수정] 유인휀 표시 추가 (절전 위해 정지)
        st.warning(f"⛔ 환기: OFF  |  🌀 유인휀: OFF  |  ⚡ 제습기: OFF")
        st.markdown(f"""
        <div style="background-color:#fff3cd;padding:15px;border-radius:10px;">
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


# --- 9. 내일 예보 ---
st.divider()
st.subheader("🔮 내일(익일) 환기 예보")
if weather_data and 'daily' in weather_data:
    t_max = weather_data['daily']['temperature_2m_max'][1]
    t_hum = weather_data['daily']['relative_humidity_2m_mean'][1]
    t_prob = weather_data['daily']['precipitation_probability_max'][1]
    t_dew = calculate_dew_point(t_max, t_hum)
    
    c1, c2 = st.columns([1,2])
    with c1:
        st.info("내일 예상")
        st.write(f"최고: {t_max:.1f}℃")
        st.write(f"습도: {t_hum:.1f}%")
        st.write(f"강수: {t_prob:.0f}%")
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
