import os
import pandas as pd

# 获取项目根目录，方便后面引用 data 文件夹
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def extract_olist_tables():
    """
    读取 Olist 的所有 9 个 CSV。
    重点处理：
    1. zip_code 前导零丢失
    2. 时间列转为 datetime
    """
    print("开始读取 Olist 数据...")

    # 1. 客户表 (处理邮编前导零)
    customers = pd.read_csv(
        os.path.join(DATA_DIR, 'olist_customers_dataset.csv'),
        dtype={'customer_zip_code_prefix': str}
    )

    # 2. 地理位置表 (邮编前导零)
    geolocation = pd.read_csv(
        os.path.join(DATA_DIR, 'olist_geolocation_dataset.csv'),
        dtype={'geolocation_zip_code_prefix': str}
    )

    # 3. 订单主表 (包含多个时间戳列)
    orders = pd.read_csv(os.path.join(DATA_DIR, 'olist_orders_dataset.csv'))
    time_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in time_cols:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # 4. 订单明细表
    order_items = pd.read_csv(os.path.join(DATA_DIR, 'olist_order_items_dataset.csv'))
    order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'], errors='coerce')

    # 5. 订单支付表
    payments = pd.read_csv(os.path.join(DATA_DIR, 'olist_order_payments_dataset.csv'))

    # 6. 订单评价表 (注意时间列)
    reviews = pd.read_csv(os.path.join(DATA_DIR, 'olist_order_reviews_dataset.csv'))
    reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
    reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')

    # 7. 商品表
    products = pd.read_csv(os.path.join(DATA_DIR, 'olist_products_dataset.csv'))

    # 8. 卖家表
    sellers = pd.read_csv(
        os.path.join(DATA_DIR, 'olist_sellers_dataset.csv'),
        dtype={'seller_zip_code_prefix': str}
    )

    # 9. 品类翻译表
    category_translation = pd.read_csv(os.path.join(DATA_DIR, 'product_category_name_translation.csv'))

    print("Olist 数据读取完成。")
    return {
        'customers': customers, 'geolocation': geolocation, 'orders': orders,
        'order_items': order_items, 'payments': payments, 'reviews': reviews,
        'products': products, 'sellers': sellers, 'category_translation': category_translation
    }


def extract_online_retail():
    """
    读取 Online Retail II，处理日期和缺失值
    """
    print("开始读取 Online Retail II 数据...")
    file_path = os.path.join(DATA_DIR, 'online_retail_II.csv')

    retail = pd.read_csv(file_path)

    if 'InvoiceDate' in retail.columns:
        retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'], dayfirst=True, errors='coerce')
    if 'Customer ID' in retail.columns:
        retail['Customer ID'] = retail['Customer ID'].astype(str).str.replace('.0', '', regex=False)

    print("Online Retail II 数据读取完成。")
    return retail


if __name__ == '__main__':
    # 测试一下提取逻辑
    olist_data = extract_olist_tables()
    retail_data = extract_online_retail()

    # 验证前导零和日期
    print("\n--- 验证 ---")
    print(f"Olist 客户表前 3 个邮编: {olist_data['customers']['customer_zip_code_prefix'].head(3).tolist()}")
    print(f"Olist 订单表前 3 个购买时间: {olist_data['orders']['order_purchase_timestamp'].head(3).tolist()}")
    print(f"Retail 前 3 个时间: {retail_data['InvoiceDate'].head(3).tolist()}")