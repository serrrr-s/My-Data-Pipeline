-- ==========================================
-- 1. 业务总览：Olist 历史总 GMV 和订单量
-- ==========================================
USE ecom_platform;
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(price + freight_value), 2) AS total_gmv,
    ROUND(AVG(price), 2) AS avg_item_price
FROM olist_sales_wide
WHERE order_status = 'delivered';


-- ==========================================
-- 2. 月度趋势：2017-2018 年每个月的 GMV
-- ==========================================
USE ecom_platform;
SELECT
    DATE_FORMAT(purchase_time, '%Y-%m') AS order_month,
    COUNT(DISTINCT order_id) AS monthly_orders,
    ROUND(SUM(price + freight_value), 2) AS monthly_gmv
FROM olist_sales_wide
WHERE order_status = 'delivered'
  AND purchase_time >= '2017-01-01'
  AND purchase_time < '2019-01-01'
GROUP BY DATE_FORMAT(purchase_time, '%Y-%m')
ORDER BY order_month;


-- ==========================================
-- 3. 地域分析：哪个州的客单价最高？
-- ==========================================
USE ecom_platform;
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(price + freight_value) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM olist_sales_wide
WHERE order_status = 'delivered'
GROUP BY customer_state
ORDER BY total_orders DESC
LIMIT 10;


-- ==========================================
-- 4. 品类分析：最赚钱的 Top 5 商品品类
-- ==========================================
USE ecom_platform;
SELECT
    category_english,
    COUNT(order_id) AS items_sold,
    ROUND(SUM(price), 2) AS total_revenue
FROM olist_sales_wide
WHERE order_status = 'delivered'
  AND category_english != 'unknown'
GROUP BY category_english
ORDER BY total_revenue DESC
LIMIT 5;


-- ==========================================
-- 5. 配送时效分析：实际送达 vs 预计送达 (延迟天数)
-- ==========================================
USE ecom_platform;
SELECT
    ROUND(AVG(DATEDIFF(delivered_time, purchase_time)), 1) AS avg_delivery_days,
    ROUND(AVG(DATEDIFF(delivered_time, estimated_delivery_time)), 1) AS avg_days_early_or_late
FROM olist_sales_wide
WHERE order_status = 'delivered'
  AND delivered_time IS NOT NULL;


-- ==========================================
-- 6. 数据质量查询 (Retail)：退货率最高的商品 Top 5
-- ==========================================
USE ecom_platform;
SELECT
    description,
    COUNT(invoice) AS return_count,
    ROUND(SUM(ABS(quantity) * price), 2) AS refunded_amount
FROM retail_returns
GROUP BY description
ORDER BY return_count DESC
LIMIT 5;