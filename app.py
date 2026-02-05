import streamlit as st
import time
from datetime import datetime

# --- 1. デザイン・視認性設定 ---
st.set_page_config(page_title="業務部コンシェルジュ", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730 !important;
        color: #ffffff !important;
        caret-color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center;
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

# --- 3. メインレイアウト（中央揃えのタイトル） ---
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
            
            # --- エラー回避版：判定ロジック ---
            found_learned = []
            for item in st.session_state.knowledge_base:
                # キーワードがリスト形式であることを確認し、空文字を除去して判定
                valid_keywords = [k for k in item.get('keywords', []) if k]
                if any(k in question for k in valid_keywords):
                    found_learned.append(item['answer'])

            found_kitei = next((v for k, v in KITEI_DB.items() if k in question), None)

            if found_learned:
                st.success(f"**【業務部の判断（学習済み）】**\n\n{found_learned[0]}")
            elif found_kitei:
                st.info(f"**【規定による回答】**\n\n{found_kitei}")
            
            if not found_learned and ("1時間" in question or "3年" in question or not found_kitei):
                st.error("⚠️ **業務部による個別判断が必要です**")
                st.write("ご質問の内容は現行規定に明記されていないか、特例の判断が必要です。")
                st.write("担当Aさんへ、本件の判断依頼を送信しますか？")
                if st.button("業務部へ質問"):
                    st.session_state.pending_questions.append({
                        "name": st.session_state.u_name, "dept": st.session_state.u_dept, 
                        "mail": st.session_state.u_mail, "q": question, "time": datetime.now().strftime("%H:%M")
                    })
                    st.success("✅ 業務部へ通知（シミュレーション）を送信しました。回答をお待ちください。")

# --- 【業務部用タブ】 ---
with tab_admin:
    st.markdown("### 🛡 業務部判断・学習管理")
    
    if st.sidebar.button("🛠 デモ用データリセット"):
        # セッションを完全にクリアして初期化
        st.session_state.knowledge_base = []
        st.session_state.pending_questions = []
        st.session_state.q_input_val = DEMO_QUESTION
        if 'confirming' in st.session_state: del st.session_state.confirming
        st.rerun()

    if not st.session_state.pending_questions:
        st.write("現在、未回答の質問はありません。")
    else:
        st.write("#### 📩 未回答リスト")
        for i, item in enumerate(st.session_state.pending_questions):
            with st.expander(f"質問者: {item['name']} ({item['dept']}) - {item['time']}", expanded=True):
                st.write(f"**内容:** {item['q']}")
                ans_text = st.text_area("回答を入力してください", value="規定は1年ですが、特別な事情があれば検討します。一度面談しましょう。", key=f"ans_{i}")
                
                words_in_q = [w for w in ["育休", "3年", "残業", "45時間", "グリーン車", "副業", "許可"] if w in item['q']]
                
                st.write("**この言葉をキーワード登録しますか？（複数選択可）**")
                cols = st.columns(len(words_in_q) if words_in_q else 1)
                selected_keywords = []
                for idx, w in enumerate(words_in_q):
                    if cols[idx].checkbox(w, key=f"check_{i}_{idx}", value=True):
                        selected_keywords.append(w)
                
                manual_k = st.text_input("追加でキーワードを直接入力（カンマ区切り）", key=f"manual_{i}", placeholder="例: 男性, 特例")
                if manual_k:
                    selected_keywords.extend([k.strip() for k in manual_k.split(",") if k.strip()])

                if st.button("回答を送信して学習させる", key=f"send_{i}"):
                    if ans_text and selected_keywords:
                        st.session_state.temp_ans = ans_text
                        st.session_state.temp_keys = selected_keywords
                        st.session_state.confirming = i
                    else:
                        st.warning("回答とキーワードを1つ以上入力してください。")

        if 'confirming' in st.session_state:
            st.markdown("---")
            st.info(f"💡 **この判断をデータベースに保存し、次回からAIが自動回答してよろしいですか？**\n\n登録キーワード: {st.session_state.temp_keys}")
            col_c1, col_c2 = st.columns(2)
            if col_c1.button("✅ 承認（AI回答を許可）"):
                # 学習データの重複やエラーを防ぐ
                new_entry = {
                    "keywords": list(set(st.session_state.temp_keys)), # 重複削除
                    "answer": st.session_state.temp_ans
                }
                st.session_state.knowledge_base.append(new_entry)
                st.session_state.pending_questions.pop(st.session_state.confirming)
                del st.session_state.confirming
                st.success("✅ 学習が完了しました。")
                time.sleep(1)
                st.rerun()
            if col_c2.button("❌ キャンセル"):
                del st.session_state.confirming
                st.rerun()
