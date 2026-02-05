import streamlit as st
import time
from datetime import datetime

# --- 1. デザイン・視認性設定 ---
st.set_page_config(page_title="業務部コンシェルジュ", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    /* 入力欄の背景と文字色 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730 !important;
        color: #ffffff !important;
        caret-color: #ffffff !important;
    }
    /* タブの視覚調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center; /* タブも中央寄せ */
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-size: 16px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. データベース（セッション保持・デモ用初期値） ---
KITEI_DB = {
    "育休": "規定第15条：原則1年。申請は1ヶ月前。1日単位での取得とする。",
    "残業": "規定第20条：45時間超は部長承認が必須。事前申請制。",
    "旅費": "規定第25条：新幹線は普通車。4時間以上または部長級はグリーン車可。",
    "退職金": "規定第30条：勤続3年以上が対象。自己都合と会社都合で算定係数が異なる。"
}

DEMO_QUESTION = "男性でも育休を3年間取れますか？"

if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = []
if 'pending_questions' not in st.session_state:
    st.session_state.pending_questions = []
if 'q_input_val' not in st.session_state:
    st.session_state.q_input_val = DEMO_QUESTION

# --- 3. メインレイアウト（タイトル：中央揃え・色調整） ---
st.markdown("<h1 style='text-align: center;'>⚖️ 業務部コンシェルジュ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px; color: #555555; margin-top: -20px; font-weight: bold;'>業務部用チャットボット</p>", unsafe_allow_html=True)
st.write("---")

tab_emp, tab_admin = st.tabs(["👥 一般社員用", "🛡 業務部用（管理者）"])

# --- 【一般社員用タブ】 ---
with tab_emp:
    st.markdown("### ❓ 規定・制度に関する質問を検索")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.text_input("氏名", value="検査 太郎", key="u_name")
    with col_u2:
        st.text_input("部署", value="検査室", key="u_dept")
    st.text_input("メールアドレス", value="taro@example.com", key="u_mail")

    question = st.text_input("質問内容を入力してください", value=st.session_state.q_input_val, key="q_input")

    if st.button("質問を検索", key="search_btn"):
        if question:
            bar = st.progress(0)
            status = st.empty()
            for i in range(1, 101):
                status.text(f"社内規定を100%スキャン中... {i}%")
                bar.progress(i)
                time.sleep(0.005)
            status.text("✅ スキャン完了。判定を出力します。")

            st.markdown("---")
            
            found_learned = [item['answer'] for item in st.session_state.knowledge_base if any(k in question for k in item['keywords'])]
            found_kitei = next((v for k, v in KITEI_DB.items() if k in question), None)

            if found_learned:
                st.success(f"**【業務部の判断（学習済み）】**\n\n{found_learned[0]}")
            elif found_kitei:
                st.info(f"**【規定による回答】**\n\n{found_kitei}")
            
            if not found_learned and ("1時間" in question or "3年" in question or not found_kitei):
                st.error("⚠️ **業務部による個別判断が必要です**")
                st.write(f"ご質問の内容は現行規定に明記されていないか、特例の判断が必要です。")
                st.write(f"担当Aさんへ、本件の判断依頼を送信します
