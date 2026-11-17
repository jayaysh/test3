import streamlit as st

from translator import TranslationError, translate

MAX_CHARS = 5000
# (버튼 라벨, 번역 대상 언어명)
LANGUAGES = [("EN · 영어", "영어"), ("JA · 일본어", "일본어"), ("VI · 베트남어", "베트남어")]

st.set_page_config(page_title="AI 번역기", page_icon="🌐", layout="centered")

# 디자인용 CSS (라이트/다크 모두에서 보이도록 반투명 색상 사용)
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
html, body, [class*="st-"], button, textarea {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
}
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 760px; padding-top: 2.5rem; padding-bottom: 3rem; }

/* 헤더 */
.stMarkdown p.app-title { font-size: 2rem !important; font-weight: 700; margin: 0; letter-spacing: -0.02em; line-height: 1.3; }
.stMarkdown p.app-sub { opacity: .65; margin: .25rem 0 1.5rem; font-size: .95rem; }

/* 카드 */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,.25);
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
/* 결과 카드는 포인트 색 틴트로 입력 카드와 구분 */
.st-key-result-card [data-testid="stVerticalBlockBorderWrapper"],
.st-key-result-card {
    background: rgba(79,70,229,.06);
    border-radius: 16px;
}
.card-label { font-size: .8rem; font-weight: 700; letter-spacing: .04em; opacity: .6; margin-bottom: .25rem; }
.result-empty { opacity: .55; padding: 1.2rem 0; text-align: center; }

/* 텍스트 영역 */
textarea { font-size: 1rem !important; line-height: 1.6 !important; }

/* 언어 버튼: 한 줄 균등 배치 (모바일에서도 줄바꿈 방지) */
.st-key-lang-row [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; gap: .6rem; }
.st-key-lang-row [data-testid="stColumn"] { min-width: 0; }
.st-key-lang-row button {
    height: 3rem; border-radius: 12px; font-weight: 600;
    border: 1px solid rgba(79,70,229,.45);
    transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
}
.st-key-lang-row button:hover {
    transform: translateY(-1px);
    background: rgba(79,70,229,.12);
    border-color: #4F46E5;
    box-shadow: 0 4px 12px rgba(79,70,229,.25);
}
.st-key-lang-row button:active { transform: translateY(0); }

@media (prefers-color-scheme: dark) {
    .st-key-lang-row button { border-color: rgba(129,140,248,.6); }
    .st-key-lang-row button:hover {
        background: rgba(129,140,248,.18); border-color: #818CF8;
        box-shadow: 0 4px 12px rgba(129,140,248,.25);
    }
    .st-key-result-card { background: rgba(129,140,248,.08); }
}

/* 알림 */
[data-testid="stAlert"] { border-radius: 12px; }

@media (max-width: 480px) {
    .stMarkdown p.app-title { font-size: 1.6rem !important; }
    .st-key-lang-row button { font-size: .85rem; padding: 0 .25rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# 헤더
st.markdown('<p class="app-title">🌐 AI 번역기</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-sub">글을 입력하고 언어를 선택하면 바로 번역해 드려요.</p>',
    unsafe_allow_html=True,
)

# 입력 카드
with st.container(border=True):
    st.markdown('<div class="card-label">원문</div>', unsafe_allow_html=True)
    # max_chars를 쓰면 초과 입력이 잘려서 안내할 수 없으므로 직접 검증
    text = st.text_area(
        "번역할 글",
        placeholder="번역할 글을 입력하세요",
        height=180,
        label_visibility="collapsed",
    )
    length = len(text)
    if length > MAX_CHARS:
        st.markdown(f":red[{length:,} / {MAX_CHARS:,}자 (초과)]")
    else:
        st.caption(f"{length:,} / {MAX_CHARS:,}자")

# 언어 선택 버튼 (같은 너비, 한 줄)
clicked = None
with st.container(key="lang-row"):
    for col, (label, lang) in zip(st.columns(3), LANGUAGES):
        if col.button(label, use_container_width=True):
            clicked = lang

# 버튼 클릭 시: 검증 → 번역 → 결과를 세션에 저장
if clicked:
    st.session_state.pop("result", None)
    if not text.strip():
        st.warning("번역할 내용을 입력해주세요.")
    elif length > MAX_CHARS:
        st.warning(f"입력이 {MAX_CHARS:,}자를 초과했습니다. 글자 수를 줄여주세요.")
    else:
        try:
            with st.spinner(f"{clicked}로 번역 중..."):
                result = translate(text, clicked)
            st.session_state["result"] = (clicked, result)
        except TranslationError as e:
            st.error(e.user_message)
        except Exception:
            st.error("번역 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

# 결과 카드
with st.container(border=True, key="result-card"):
    if "result" in st.session_state:
        lang, result = st.session_state["result"]
        st.markdown(f'<div class="card-label">번역 결과 · {lang}</div>', unsafe_allow_html=True)
        st.code(result, language=None, wrap_lines=True)
    else:
        st.markdown('<div class="card-label">번역 결과</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="result-empty">언어 버튼을 누르면 번역 결과가 여기에 표시됩니다.</div>',
            unsafe_allow_html=True,
        )
