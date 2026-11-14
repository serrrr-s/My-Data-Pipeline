# src/load.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from extract import extract_olist_tables, extract_online_retail

# 加载 .env 中的环境变量
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def get_db_engine():
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    base_engine = create_engine(base_url)
    with base_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4"))
        conn.commit()

    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return create_engine(db_url)


def load_data_to_mysql():
    print("开始执行 ETL 流程...")

    # 1. 抽取数据
    olist_data = extract_olist_tables()
    retail_data = extract_online_retail()

    engine = get_db_engine()

    # 2. 写入 Olist 的 9 个表
    print("\n开始写入 Olist 数据表 (这可能需要一小会儿)...")
    olist_table_names = {
        'customers': 'olist_customers',
        'geolocation': 'olist_geolocation',
        'order_items': 'olist_order_items',
        'payments': 'olist_order_payments',
        'reviews': 'olist_order_reviews',
        'orders': 'olist_orders',
        'products': 'olist_products',
        'sellers': 'olist_sellers',
        'category_translation': 'olist_category_translation'
    }

    for df_key, table_name in olist_table_names.items():
        df = olist_data[df_key]
        # if_exists='replace' 会自动建表并写入，如果表存在会先删掉（适合开发测试阶段）
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        print(f"  -> 表 `{table_name}` 写入完成 ({len(df)} 行)")

    # 3. 写入 Online Retail II
    print("\n开始写入 Online Retail II 数据表...")
    retail_data.to_sql(name='online_retail_ii', con=engine, if_exists='replace', index=False)
    print(f"  -> 表 `online_retail_ii` 写入完成 ({len(retail_data)} 行)")

    print("\n✅ 所有数据加载完成！去 MySQL 里看看吧。")


if __name__ == '__main__':
    load_data_to_mysql()