import streamlit as st
import time
from datetime import datetime

# --- 1. 零(ZERO) ブランドデザイン設定 ---
st.set_page_config(page_title="業務部コンシェルジュ", page_icon="⚖️")

# カスタムCSSでデザインをネイビー・シルバー調に
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #1f2937;
        color: #c0c0c0;
        border: 1px solid #c0c0c0;
        width: 100%;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #c0c0c0;
        color: #0e1117;
    }
    .stTextInput>div>div>input {
        background-color: #1f2937;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 知識ベース（架空規定） ---
KITEI_DB = {
    "育休": "第15条：原則1年。申請は1ヶ月前。1日単位での取得とする。",
    "残業": "第20条：45時間超は部長承認が必須。事前申請制。",
    "旅費": "第25条：新幹線は普通車。4時間以上または部長級はグリーン車可。",
    "退職金": "第30条：勤続3年以上が対象。自己都合と会社都合で係数が異なる。"
}

# 業務部判断の蓄積（セッション保持）
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = {
        "精密機器": "精密機器携行時は4時間未満でもグリーン車可（業務部判断済）"
    }

# --- 3. UIレイアウト ---
st.title("⚖️ 業務部コンシェルジュ")
st.markdown("### **零 (ZERO) - 規定参照型AIプロトタイプ**")
st.write("---")

# 利用者情報（検査室からのアクセスを想定）
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        u_name = st.text_input("氏名", "検査 太郎")
    with col2:
        u_dept = st.text_input("部署", "検査室")
    u_mail = st.text_input("メールアドレス", "taro@example.com")

st.write("---")

# 質問入力（お題）
question = st.text_input("❓ 規定・制度について質問してください", placeholder="例：育休を1時間単位で取れますか？")

if st.button("零（ZERO）エンジンで解析を実行"):
    if question:
        # インパクト重視の演出：プログレスバー
        bar = st.progress(0)
        status = st.empty()
        for i in range(1, 101):
            status.text(f"社内規定を100%スキャン中... {i}%")
            bar.progress(i)
            time.sleep(0.01)
        status.text("✅ スキャン完了。判定を出力します。")
        
        st.markdown("---")
        
        # 判定ロジック
        found_kitei = None
        for key in KITEI_DB:
            if key in question:
                found_kitei = KITEI_DB[key]
                break
        
        if found_kitei:
            st.success(f"**【規定による回答】**\n\n{found_kitei}")
        
        # 教師データ（過去の判断）の照合
        for key in st.session_state.knowledge_base:
            if key in question:
                st.info(f"**【過去の業務部判断を発見】**\n\n{st.session_state.knowledge_base[key]}")
        
        # 案A（安全重視）：規定外・曖昧なケース
        if "1時間" in question or "3年" in question or not found_kitei:
            st.error("⚠️ **【案A：安全重視】判断を保留します**")
            st.write("ご質問の内容は現行規定に明記されていないか、特例の判断が必要です。")
            st.write(f"担当Aさんへ、本件（{question}）の判断依頼を送信しますか？")
            if st.button("担当Aさんへエスカレーションを実行"):
                st.success("✅ Aさんへ通知を送信しました。回答をお待ちください。")
        
        st.markdown("---")
        st.caption("「私はプロセスを100%制御しています。詳細は業務部へ。」")

# --- 4. 学習モード（プレゼンの見せ場） ---
with st.expander("🛠 管理者メニュー（業務部判断の蓄積）"):
    st.write("担当Aさんの判断を教師データとして学習させ、AIを成長させます。")
    new_q = st.text_input("判断が必要なキーワード（例：副業）")
    new_a = st.text_area("業務部としての判断（例：原則禁止だが、許可制で認める場合がある）")
    if st.button("知恵をデータベースに蓄積"):
        st.session_state.knowledge_base[new_q] = f"{new_a}（業務部判断 {datetime.now().strftime('%Y/%m/%d')}）"
        st.success("ナレッジを保存しました。次回から同様の質問に回答可能になります。")
