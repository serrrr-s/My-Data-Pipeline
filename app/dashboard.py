# app/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 页面基础配置
st.set_page_config(page_title="Olist 电商数据看板", layout="wide")
st.title("🛒 Olist 电商数据质量与业务分析看板")

# 连接数据库
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

@st.cache_resource
def get_db_engine():
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return create_engine(db_url)

engine = get_db_engine()

# 顶部核心指标 (查询第一段 SQL)
query_kpi = """
SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(price + freight_value), 2) AS total_gmv,
    ROUND(AVG(price), 2) AS avg_item_price
FROM olist_sales_wide
WHERE order_status = 'delivered';
"""
df_kpi = pd.read_sql(query_kpi, con=engine)

# 用三列展示指标
col1, col2, col3 = st.columns(3)
col1.metric("总订单量", f"{df_kpi['total_orders'][0]:,} 单")
col2.metric("总 GMV", f"R$ {df_kpi['total_gmv'][0]:,.2f}")
col3.metric("平均客单价", f"R$ {df_kpi['avg_item_price'][0]:,.2f}")

st.divider()

# 画图区域：拆成左右两列
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 月度 GMV 趋势 (2017-2018)")
    # 查询月度趋势 (注意这里改成了 %%Y-%%m)
    query_monthly = """
    SELECT 
        DATE_FORMAT(purchase_time, '%%Y-%%m') AS order_month,
        COUNT(DISTINCT order_id) AS monthly_orders,
        ROUND(SUM(price + freight_value), 2) AS monthly_gmv
    FROM olist_sales_wide
    WHERE order_status = 'delivered' AND purchase_time >= '2017-01-01' AND purchase_time < '2019-01-01'
    GROUP BY DATE_FORMAT(purchase_time, '%%Y-%%m')
    ORDER BY order_month;
    """
    df_monthly = pd.read_sql(query_monthly, con=engine)
    # 用 Plotly 画折线图
    fig_line = px.line(df_monthly, x='order_month', y='monthly_gmv', markers=True,
                       labels={'order_month': '月份', 'monthly_gmv': 'GMV (R$)'})
    st.plotly_chart(fig_line, use_container_width=True)

with right_col:
    st.subheader("🏆 最赚钱的 Top 10 品类")
    # 查询品类
    query_category = """
    SELECT 
        category_english,
        ROUND(SUM(price), 2) AS total_revenue
    FROM olist_sales_wide
    WHERE order_status = 'delivered' AND category_english != 'unknown'
    GROUP BY category_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    df_cat = pd.read_sql(query_category, con=engine)
    # 用 Plotly 画横向柱状图
    fig_bar = px.bar(df_cat, x='total_revenue', y='category_english', orientation='h',
                     labels={'total_revenue': '总销售额 (R$)', 'category_english': ''})
    # 让最赚钱的在最上面
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# 底部表格
st.subheader("🚚 各州客单价及订单分布 (Top 10)")
query_state = """
SELECT 
    customer_state AS '州',
    COUNT(DISTINCT order_id) AS '总订单数',
    ROUND(SUM(price + freight_value) / COUNT(DISTINCT order_id), 2) AS '客单价 (R$)'
FROM olist_sales_wide
WHERE order_status = 'delivered'
GROUP BY customer_state
ORDER BY COUNT(DISTINCT order_id) DESC
LIMIT 10;
"""
df_state = pd.read_sql(query_state, con=engine)
st.dataframe(df_state, use_container_width=True)