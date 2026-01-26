import streamlit as st
import pandas as pd
import math
from datetime import datetime
import pytz

# --- 1. 앱 기본 설정 (브라우저 탭 이름 등) ---
st.set_page_config(
    page_title="울산다운1차 결로관리",
    page_icon="🏗️",
    layout="centered"
)

# --- 2. [커스터마이징] 사이드바: 현장 정보 명시 ---
with st.sidebar:
    st.header("🏗️ 현장 개요")
    st.info("""
    **[PROJECT]**
    **울산다운1차 아파트 건설공사**
    
    * **위치:** 울산광역시 중구 다운동 일원
    * **시공:** 우미건설(주)
    * **관리:** 설비팀 (작성자: 설비과장)
    * **목적:** 지하주차장 결로 Zero화
    """)
    
    # 현재 시간 표시 (울산 현장 기준)
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    st.write(f"🕒 조회시간: {now.strftime('%Y-%m-%d %H:%M')}")
    st.write("---")
    st.caption("Unauthorized access is prohibited.\nFor internal use only.")

# --- 3. 메인 헤더: 현장 소속감 부여 ---
st.markdown("## 🏢 Woomi Construction")
st.title("울산다운1차 결로 방지 대시보드")
st.markdown("##### 📢 현장 설비팀 공지사항")
st.warning("본 시스템은 **울산다운1차 현장 실시간 데이터**를 기반으로 작동합니다. 작업 전 반드시 아래 '가동 신호'를 확인하시기 바랍니다.")

st.divider()

# --- 4. 로직 (이슬점 계산 - Magnus 공식) ---
def calculate_dew_point(temp, hum):
    b = 17.62
    c = 243.12
    gamma = (b * temp / (c + temp)) + math.log(hum / 100.0)
    dew_point = (c * gamma) / (b - gamma)
    return round(dew_point, 2)

# --- 5. 데이터 입력 (현장 상황 시뮬레이션) ---
# 실제 배포 시에는 기상청 API로 자동화 가능
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌡️ 지하 내부")
    underground_temp = st.slider("벽체/바닥 표면온도 (℃)", 0, 35, 18, help="비접촉 온도계로 측정한 지하주차장 최저 온도")

with col2:
    st.markdown("### ☁️ 외부 날씨")
    # 울산의 여름철 평균 데이터를 기본값으로 설정
    ext_temp = st.number_input("현재 기온 (℃)", value=28.0)
    ext_hum = st.number_input("현재 습도 (%)", value=80.0)

# --- 6. 판단 로직 및 결과 표시 ---
ext_dew_point = calculate_dew_point(ext_temp, ext_hum)
safety_margin = 2.0  # 안전율

st.write("") # 여백
st.subheader("📋 실시간 판정 결과")

# 결과 카드 디자인
result_container = st.container()

if ext_dew_point >= (underground_temp - safety_margin):
    # 위험 (결로 발생)
    result_style = """
        <div style="background-color: #ffcccc; padding: 20px; border-radius: 10px; border-left: 10px solid #ff4b4b;">
            <h3 style="color: #ff4b4b; margin:0;">⛔ 환기 시스템 가동 중지 (OFF)</h3>
            <p style="margin-top:10px; font-weight:bold;">지금 외부 공기를 들이면 100% 결로 발생합니다.</p>
        </div>
    """
    st.markdown(result_style, unsafe_allow_html=True)
    st.write("")
    st.error(f"분석: 외기 이슬점({ext_dew_point}℃)이 지하 구조체({underground_temp}℃)보다 높거나 비슷합니다.")
    
else:
    # 안전 (건조 가능)
    result_style = """
        <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 10px solid #28a745;">
            <h3 style="color: #28a745; margin:0;">✅ 환기 시스템 가동 (ON)</h3>
            <p style="margin-top:10px; font-weight:bold;">적극적인 환기로 습기를 제거하세요.</p>
        </div>
    """
    st.markdown(result_style, unsafe_allow_html=True)
    st.write("")
    st.success(f"분석: 외기 이슬점({ext_dew_point}℃)이 지하 구조체({underground_temp}℃)보다 낮아 안전합니다.")

# --- 7. 하단 푸터 (Footer) : 소속 강조 ---
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