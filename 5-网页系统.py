import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from io import BytesIO
import json
import os

# ================== 全局配置与美化CSS ==================
st.set_page_config(
    page_title="HQY商分平台",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义全局CSS美化
st.markdown("""
<style>
/* 全局字体与背景 */
* {
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}
[data-testid="stAppViewContainer"] {
    background-color: #f8f9fa;
}
/* 卡片样式 */
.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}
.card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}
/* 按钮美化 */
.stButton>button {
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    background: linear-gradient(90deg, #ff7e33, #ff5500);
    color: white;
    border: none;
    font-weight: 500;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ff5500, #ff3300);
    transform: scale(1.02);
}
/* 侧边栏美化 */
[data-testid="stSidebar"] {
    background-color: white;
    box-shadow: 2px 0 10px rgba(0,0,0,0.05);
}
/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a;
    }
    .card {
        background: #2d2d2d;
        color: white;
    }
}
/* 登录页居中 */
.login-container {
    max-width: 400px;
    margin: 5rem auto;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ================== 用户账号存储 ==================
USERS_FILE = "users.json"
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin": "123456"}
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ================== 状态控制 ==================
if "login_status" not in st.session_state:
    st.session_state.login_status = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ================== 美化版登录/注册页 ==================
if not st.session_state.login_status:
    # 登录页居中卡片
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🛒 电商智能分析平台")
    st.markdown("---")

    # 切换登录/注册
    col1, col2 = st.columns(2)
    with col1:
        if st.button("登录", use_container_width=True, disabled=st.session_state.auth_mode == "login"):
            st.session_state.auth_mode = "login"
            st.rerun()
    with col2:
        if st.button("注册", use_container_width=True, disabled=st.session_state.auth_mode == "register"):
            st.session_state.auth_mode = "register"
            st.rerun()

    # 登录表单
    if st.session_state.auth_mode == "login":
        st.subheader("用户登录")
        username = st.text_input("账号", placeholder="请输入账号")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        if st.button("登录系统", use_container_width=True):
            users = load_users()
            if username in users and users[username] == password:
                st.session_state.login_status = True
                st.session_state.current_user = username
                st.rerun()
            else:
                st.error("账号或密码错误，请重试！")

    # 注册表单
    elif st.session_state.auth_mode == "register":
        st.subheader("注册新账号")
        new_username = st.text_input("设置账号（不可重复）", placeholder="请输入账号")
        new_password = st.text_input("设置密码", type="password", placeholder="请输入密码（至少6位）")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        if st.button("立即注册", use_container_width=True):
            users = load_users()
            if new_username in users:
                st.error("该账号已存在，请换一个！")
            elif new_password != confirm_password:
                st.error("两次输入的密码不一致！")
            elif len(new_password) < 6:
                st.error("密码长度至少6位！")
            else:
                users[new_username] = new_password
                save_users(users)
                st.success("注册成功！请切换到登录页登录~")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================== 主系统侧边栏（美化版） ==================
with st.sidebar:
    st.title(f"👋 欢迎，{st.session_state.current_user}")
    st.markdown("---")
    # 主题切换
    st.subheader("⚙️ 设置")
    theme = st.selectbox("界面主题", ["浅色模式", "深色模式"], index=0)
    st.markdown("---")
    # 数据上传
    st.subheader("📤 数据上传")
    file = st.file_uploader("上传CSV数据", type="csv")
    st.markdown("---")
    # 筛选设置
    st.subheader("📅 筛选设置")
    day1 = st.date_input("开始日期", datetime.date(2017,11,25))
    day2 = st.date_input("结束日期", datetime.date(2017,12,3))
    st.markdown("---")
    # 退出按钮
    if st.button("退出登录", use_container_width=True):
        st.session_state.login_status = False
        st.session_state.current_user = None
        st.session_state.auth_mode = "login"
        st.rerun()

# 深色模式适配（通过CSS变量控制）
if theme == "深色模式":
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {background-color: #1a1a1a; color: white;}
    .card {background: #2d2d2d; color: white;}
    [data-testid="stSidebar"] {background-color: #2d2d2d; color: white;}
    </style>
    """, unsafe_allow_html=True)

# ================== 主界面标题 ==================
st.title("📊 电商大数据智能分析平台")
st.markdown("---")

# ================== 数据加载（带加载动画） ==================
@st.cache_data(ttl=3600)
def load_data(file):
    try:
        if file is None:
            df = pd.read_csv("清洗后的数据.csv", parse_dates=["时间"])
            df["日期"] = df["时间"].dt.date
            df["小时"] = df["时间"].dt.hour
        else:
            df = pd.read_csv(file)
            df.columns = ["用户ID","商品ID","商品类目ID","行为类型","时间戳"]
            df["时间"] = pd.to_datetime(df["时间戳"], unit="s")
            df["日期"] = df["时间"].dt.date
            df["小时"] = df["时间"].dt.hour
        df["行为类型"] = df["行为类型"].map({"pv":"点击","fav":"收藏","cart":"加购","buy":"购买"})
        return df
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return None

with st.spinner("正在加载数据，请稍候..."):
    df = load_data(file)
if df is None: st.stop()

df = df[(df["日期"] >= day1) & (df["日期"] <= day2)]
buy = df[df["行为类型"]=="购买"]

# ================== 1. 数据概览（卡片式布局） ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📌 数据概览")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总用户数", df["用户ID"].nunique(), help="平台活跃用户总数")
with col2:
    st.metric("总商品数", df["商品ID"].nunique(), help="平台在售商品总数")
with col3:
    st.metric("总行为量", len(df), help="用户操作总次数")
with col4:
    st.metric("购买次数", len(buy), help="成功购买订单数")
st.markdown('</div>', unsafe_allow_html=True)

# ================== 2. 用户价值分层（美化图表） ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("👥 用户价值分层")
if len(buy) > 0:
    now = buy["时间"].max()
    rfm = buy.groupby("用户ID").agg(
        R=("时间", lambda x:(now - x.max()).days),
        F=("商品ID","count")
    ).reset_index()
    rfm["R等级"] = pd.cut(rfm["R"], bins=[-1,1,3,7,1000], labels=[4,3,2,1])
    rfm["F等级"] = pd.cut(rfm["F"], bins=[0,1,3,10,1000], labels=[1,2,3,4])
    def get_type(r,f):
        if r>=3 and f>=3: return "高价值用户"
        elif r>=3: return "活跃新用户"
        elif f>=3: return "流失高价值用户"
        else: return "一般用户"
    rfm["用户类型"] = rfm.apply(lambda x:get_type(x["R等级"],x["F等级"]), axis=1)
    res = rfm["用户类型"].value_counts().reset_index()
    res.columns=["用户类型","数量"]
    c1,c2 = st.columns(2)
    with c1:
        st.dataframe(res, use_container_width=True)
    with c2:
        fig,ax=plt.subplots(figsize=(6,4))
        colors = ["#ff7e33", "#3399ff", "#66cc66", "#ffcc00"]
        ax.pie(res["数量"], labels=res["用户类型"], autopct="%1.1f%%", colors=colors, startangle=90)
        ax.set_title("用户类型占比", fontsize=12, pad=10)
        st.pyplot(fig)
else:
    st.info("当前日期范围内无购买数据，无法进行用户分群分析")
st.markdown('</div>', unsafe_allow_html=True)

# ================== 3. 销量趋势（美化图表） ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📈 销量趋势分析")
if len(buy) > 0:
    day_sale = buy.groupby("日期")["商品ID"].count().reset_index()
    day_sale.columns=["日期","销量"]
    st.line_chart(day_sale, x="日期", y="销量", color="#ff7e33", use_container_width=True)
else:
    st.info("当前日期范围内无购买数据，无法展示销量趋势")
st.markdown('</div>', unsafe_allow_html=True)

# ================== 4. 热门商品TOP10 ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔥 热门商品TOP10")
if len(buy) > 0:
    top = buy["商品ID"].value_counts().head(10).reset_index()
    top.columns=["商品ID","购买次数"]
    st.dataframe(top, use_container_width=True)
else:
    st.info("当前日期范围内无购买数据，无法展示热门商品")
st.markdown('</div>', unsafe_allow_html=True)

# ================== 5. 转化漏斗 ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔄 用户行为转化漏斗")
funnel = df["行为类型"].value_counts().reindex(["点击","收藏","加购","购买"]).fillna(0)
st.bar_chart(funnel, color="#3399ff", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================== 6. 导出报告（美化按钮） ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📥 导出分析报告")
def excel():
    io = BytesIO()
    with pd.ExcelWriter(io, engine="openpyxl") as writer:
        df.head(2000).to_excel(writer, sheet_name="原始数据", index=False)
        if len(buy) > 0:
            res.to_excel(writer, sheet_name="用户分群", index=False)
            day_sale.to_excel(writer, sheet_name="销量趋势", index=False)
            top.to_excel(writer, sheet_name="热门商品", index=False)
    io.seek(0)
    return io
st.download_button("📊 下载完整Excel报告", excel(), "电商分析报告.xlsx", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
