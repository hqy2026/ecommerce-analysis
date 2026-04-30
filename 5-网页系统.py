import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from io import BytesIO

# ================== 全局设置 ==================
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
st.set_page_config(page_title="电商智能分析系统", layout="wide")

# ================== 登录逻辑（修复版） ==================
if "login_status" not in st.session_state:
    st.session_state.login_status = False

def verify_login(username, password):
    return username == "admin" and password == "123456"

if not st.session_state.login_status:
    st.title("电商智能分析系统 - 登录")
    st.sidebar.header("用户登录")
    
    username = st.sidebar.text_input("账号", value="")
    password = st.sidebar.text_input("密码", type="password", value="")
    
    if st.sidebar.button("登录", use_container_width=True):
        if verify_login(username, password):
            st.session_state.login_status = True
            st.rerun()
        else:
            st.sidebar.error("账号或密码错误，请重试")
    
    st.markdown("""
    ### 欢迎使用电商智能分析系统
    请在左侧输入账号密码登录，默认账号：`admin`，默认密码：`123456`
    """)
    st.stop()

# ================== 主系统 ==================
with st.sidebar:
    st.title("电商智能分析系统")
    st.markdown("---")
    st.subheader("数据上传")
    file = st.file_uploader("上传CSV数据", type="csv")
    
    st.markdown("---")
    st.subheader("筛选设置")
    day1 = st.date_input("开始日期", datetime.date(2017,11,25))
    day2 = st.date_input("结束日期", datetime.date(2017,12,3))
    
    if st.button("退出登录", use_container_width=True):
        st.session_state.login_status = False
        st.rerun()

st.title("电商大数据智能分析平台")
st.markdown("---")

# ================== 读取数据（修复日期类型） ==================
@st.cache_data(ttl=3600)
def load_data(file):
    try:
        if file is None:
            # 读取默认数据，强制处理日期类型
            df = pd.read_csv("清洗后的数据.csv", parse_dates=["时间"])
            df["日期"] = df["时间"].dt.date
            df["小时"] = df["时间"].dt.hour
        else:
            # 读取上传数据，处理日期类型
            df = pd.read_csv(file)
            df.columns = ["用户ID","商品ID","商品类目ID","行为类型","时间戳"]
            df["时间"] = pd.to_datetime(df["时间戳"], unit="s")
            df["日期"] = df["时间"].dt.date
            df["小时"] = df["时间"].dt.hour
        
        # 统一处理行为类型
        df["行为类型"] = df["行为类型"].map({
            "pv":"点击","fav":"收藏","cart":"加购","buy":"购买"
        })
        return df
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return None

df = load_data(file)
if df is None: st.stop()

# 日期过滤（现在类型匹配，不会报错）
df = df[(df["日期"] >= day1) & (df["日期"] <= day2)]
buy = df[df["行为类型"]=="购买"]

# ================== 1. 数据概览 ==================
st.subheader("一、数据概览")
a,b,c,d = st.columns(4)
a.metric("总用户数", df["用户ID"].nunique())
b.metric("总商品数", df["商品ID"].nunique())
c.metric("总行为量", len(df))
d.metric("购买次数", len(buy))
st.divider()

# ================== 2. 用户RFM分群 ==================
st.subheader("二、用户价值分层")
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
    c1.dataframe(res, use_container_width=True)
    fig,ax=plt.subplots()
    ax.pie(res["数量"], labels=res["用户类型"], autopct="%1.1f%%")
    c2.pyplot(fig)
else:
    st.info("当前日期范围内无购买数据，无法进行用户分群分析")
st.divider()

# ================== 3. 销量趋势 ==================
st.subheader("三、销量趋势分析")
if len(buy) > 0:
    day_sale = buy.groupby("日期")["商品ID"].count().reset_index()
    day_sale.columns=["日期","销量"]
    st.line_chart(day_sale, x="日期", y="销量", color="#ff6600")
else:
    st.info("当前日期范围内无购买数据，无法展示销量趋势")
st.divider()

# ================== 4. 热门商品TOP10 ==================
st.subheader("四、热门商品TOP10")
if len(buy) > 0:
    top = buy["商品ID"].value_counts().head(10).reset_index()
    top.columns=["商品ID","购买次数"]
    st.dataframe(top, use_container_width=True)
else:
    st.info("当前日期范围内无购买数据，无法展示热门商品")
st.divider()

# ================== 5. 转化漏斗 ==================
st.subheader("五、用户行为转化漏斗")
funnel = df["行为类型"].value_counts().reindex(["点击","收藏","加购","购买"]).fillna(0)
st.bar_chart(funnel, color="#3399ff")
st.divider()

# ================== 6. 导出报告 ==================
st.subheader("六、导出分析报告")
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

st.download_button("下载完整Excel报告", excel(), "电商分析报告.xlsx")