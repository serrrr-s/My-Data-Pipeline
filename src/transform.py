# src/transform.py
# src/transform.py
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


def transform_retail():
    print("=== 开始清洗 Online Retail II 数据 ===")
    engine = get_db_engine()

    # 1. 读取数据
    df = pd.read_sql("SELECT * FROM online_retail_ii", con=engine)
    # 统一列名格式
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]

    # 2. 基础类型转换
    df['invoice'] = df['invoice'].astype(str)
    df['invoicedate'] = pd.to_datetime(df['invoicedate'])

    # 3. 拆分取消/退货订单（Invoice 以 'C' 开头，或者 quantity < 0）
    # 逻辑：只要 invoice 以 C 开头，或者数量小于 0，我们就认为这是退货/异常
    is_return = df['invoice'].str.startswith('C') | (df['quantity'] < 0)

    df_returns = df[is_return].copy()
    df_sales = df[~is_return].copy()

    # 4. 清洗正常销售表 (retail_sales)
    # 剔除价格 <= 0 的异常行（赠品或错误）
    df_sales = df_sales[df_sales['price'] > 0]

    # 如果描述为空，填一个 "Unknown"
    df_sales['description'] = df_sales['description'].fillna('Unknown')

    # 5. 清洗退货表 (retail_returns)
    # 同样填一下描述
    df_returns['description'] = df_returns['description'].fillna('Unknown')

    print(f"清洗完成！")
    print(f"  -> 正常销售数据: {len(df_sales)} 行")
    print(f"  -> 退货/异常数据: {len(df_returns)} 行")

    # 6. 写回数据库 (覆盖之前的表，生成两张干净的新表)
    print("\n正在将清洗后的数据写回数据库...")

    df_sales.to_sql(name='retail_sales', con=engine, if_exists='replace', index=False)
    print("  -> 表 `retail_sales` 写入完成")

    df_returns.to_sql(name='retail_returns', con=engine, if_exists='replace', index=False)
    print("  -> 表 `retail_returns` 写入完成")

    print("\n✅ Retail 数据清洗并拆分完毕！")


if __name__ == '__main__':
    transform_retail()