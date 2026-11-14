# src/transform_olist.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def get_db_engine():
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return create_engine(db_url)


def build_olist_wide_table():
    print("=== 开始构建 Olist 订单大宽表 ===")
    engine = get_db_engine()

    # 1. 读取需要的表
    print("正在读取相关表...")
    order_items = pd.read_sql("SELECT * FROM olist_order_items", con=engine)
    orders = pd.read_sql("SELECT * FROM olist_orders", con=engine)
    customers = pd.read_sql("SELECT * FROM olist_customers", con=engine)
    products = pd.read_sql("SELECT * FROM olist_products", con=engine)
    translation = pd.read_sql("SELECT * FROM olist_category_translation", con=engine)
    payments = pd.read_sql("SELECT * FROM olist_order_payments", con=engine)

    # 2. 预处理支付表
    # 一个订单可能有多次支付（比如分期付款、代金券），我们需要把金额加总
    print("正在聚合支付数据...")
    payments_agg = payments.groupby('order_id')['payment_value'].sum().reset_index()

    # 3. 开始多表 Join 拼装
    print("正在拼装大宽表 (这可能需要十几秒)...")

    # 第一步：订单明细 + 订单主表
    df = pd.merge(order_items, orders, on='order_id', how='left')

    # 第二步：关联客户表（获取客户所在州）
    df = pd.merge(df, customers[['customer_id', 'customer_state', 'customer_city']], on='customer_id', how='left')

    # 第三步：关联商品表
    df = pd.merge(df, products[['product_id', 'product_category_name']], on='product_id', how='left')

    # 第四步：关联翻译表（把葡萄牙语翻译成英语）
    df = pd.merge(df, translation, on='product_category_name', how='left')
    # 如果没翻译过来的，就叫 'unknown'
    df['product_category_name_english'] = df['product_category_name_english'].fillna('unknown')

    # 第五步：关联聚合后的支付表
    df = pd.merge(df, payments_agg, on='order_id', how='left')

    # 4. 保留我们需要的字段，并重命名
    print("正在挑选最终字段...")
    final_cols = {
        'order_id': 'order_id',
        'order_item_id': 'order_item_id',
        'product_id': 'product_id',
        'seller_id': 'seller_id',
        'price': 'price',
        'freight_value': 'freight_value',
        'order_status': 'order_status',
        'order_purchase_timestamp': 'purchase_time',
        'order_delivered_customer_date': 'delivered_time',
        'order_estimated_delivery_date': 'estimated_delivery_time',
        'customer_state': 'customer_state',
        'customer_city': 'customer_city',
        'product_category_name_english': 'category_english',
        'payment_value': 'order_total_payment'
    }

    df_final = df[list(final_cols.keys())].rename(columns=final_cols)

    # 5. 存入数据库
    print("正在将大宽表写入 MySQL...")
    df_final.to_sql(name='olist_sales_wide', con=engine, if_exists='replace', index=False)
    print(f"  -> 表 `olist_sales_wide` 写入完成，共 {len(df_final)} 行")

    print("\n✅ Olist 建模完成！")


if __name__ == '__main__':
    build_olist_wide_table()