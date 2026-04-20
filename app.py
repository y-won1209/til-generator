import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="팀원 맞춤형 TIL 생성기", page_icon="📝", layout="wide")
st.title("📝 팀원 맞춤형 TIL 자동 생성기")
st.markdown("회의록과 강조하고 싶은 내용을 입력하면, 각 부원의 기존 말투를 반영하여 TIL을 자동 생성합니다.")

# 사이드바: API 키 입력
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.markdown("[Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받을 수 있습니다.")

if not api_key:
    st.warning("👈 좌측 사이드바에 Gemini API Key를 입력해주세요.")
    st.stop()

# Gemini 모델 설정
genai.configure(api_key=api_key)
# 긴 문맥과 텍스트 생성에 유리한 1.5 Pro 또는 Flash 모델 사용
model = genai.GenerativeModel('gemini-2.5-flash') 

# 공통 입력란: 오늘 회의록
st.header("1. 오늘 회의록 입력")
meeting_minutes = st.text_area("오늘 회의에서 나온 주요 내용, 결정 사항, 진행 상황 등을 상세히 적어주세요.", height=200)

st.header("2. 부원별 TIL 생성")
st.markdown("각 부원의 탭에서 과거 TIL 샘플을 넣고 (말투 학습용), 오늘 강조할 내용을 입력한 뒤 생성 버튼을 누르세요.")

# 8명의 부원 이름 설정 (필요시 실제 이름으로 변경하세요)
member_names = ["부원 1", "부원 2", "부원 3", "부원 4", "부원 5", "부원 6", "부원 7", "부원 8"]
tabs = st.tabs(member_names)

# 각 부원별 탭 생성
for i, tab in enumerate(tabs):
    with tab:
        member = member_names[i]
        st.subheader(f"🗣️ {member}의 TIL 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 말투 학습용 과거 데이터
            past_til = st.text_area(
                "과거 TIL 샘플 (말투 학습용)", 
                placeholder=f"{member}이(가) 평소에 작성했던 TIL 2~3개를 복사해서 넣어주세요. 이 말투를 그대로 따라합니다.", 
                height=150, 
                key=f"past_{i}"
            )
            
        with col2:
            # 개별 강조 사항
            emphasis = st.text_area(
                "오늘 특별히 강조하고 싶은 내용 (선택)", 
                placeholder=f"예: 프론트엔드 API 연결하면서 겪은 에러 해결 과정을 강조해줘. / 오늘은 유독 피곤했지만 팀원들 덕에 힘이 났다는 감상을 넣어줘.", 
                height=150, 
                key=f"emp_{i}"
            )
            
        if st.button(f"✨ {member} TIL 생성하기", key=f"btn_{i}"):
            if not meeting_minutes:
                st.error("위쪽에 오늘 회의록을 먼저 입력해주세요!")
            elif not past_til:
                st.error("말투를 학습할 수 있도록 '과거 TIL 샘플'을 입력해주세요!")
            else:
                with st.spinner(f"{member}의 말투로 TIL을 작성하는 중..."):
                    # 프롬프트 설계
                    prompt = f"""
                    당신은 우리 팀의 '{member}'입니다.
                    아래 제공된 [과거 TIL 샘플]을 철저히 분석하여 당신의 평소 말투, 어조, 자주 쓰는 단어, 문장 길이, 감정 표현 방식을 완벽하게 모방하세요.
                    
                    [과거 TIL 샘플]:
                    {past_til}
                    
                    [오늘의 회의록]:
                    {meeting_minutes}
                    
                    [특별히 강조하고 싶은 내용]:
                    {emphasis if emphasis else "특별한 강조 사항 없음. 회의록 내용을 바탕으로 자연스럽게 작성할 것."}
                    
                    **지시사항:**
                    1. 반드시 [과거 TIL 샘플]의 말투(존댓말/반말 여부, 이모티콘 사용 여부 등)와 100% 일치하게 작성하세요.
                    2. [오늘의 회의록] 내용과 [특별히 강조하고 싶은 내용]을 바탕으로 오늘 배우고 느낀 점을 작성하세요.
                    3. 글자 수는 공백 포함하여 **최소 500자에서 최대 1000자 사이**로 작성하세요. (약 3~4문단 분량)
                    4. 인삿말이나 "네, 작성해 드리겠습니다" 같은 AI스러운 답변은 절대 빼고, 오직 TIL 본문 내용만 출력하세요.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        st.success("생성 완료!")
                        st.markdown("### 📝 완성된 TIL")
                        st.info(response.text)
                        
                        # 글자 수 카운트 확인용
                        st.caption(f"글자 수 (공백 포함): {len(response.text)}자")
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")