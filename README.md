# 🛒 Olist & Retail E-Commerce Data Platform

这是一个端到端的电商数据工程个人项目。项目基于 Kaggle 上的两个公开数据集：
1. **Brazilian E-Commerce Public Dataset by Olist**（巴西电商数据，多维业务分析）
2. **Online Retail II**（英国零售流水，脏数据治理与退货分析）

构建了一套从数据抽取、质量评估、清洗拆分、多表建模到可视化看板的完整 ETL 管道。

## 🏗️ 架构与流程
- **Extract**: 读取原始 CSV，处理编码、日期格式转换、邮编前导零丢失等坑。
- **Load**: 使用 SQLAlchemy 自动建库建表，将百万级数据高速写入 MySQL 8.0+。
- **Transform**: 
  - 对 Online Retail II 进行质量体检，拆分出正常销售表与退货异常表。
  - 对 Olist 的 9 张散表进行关联，聚合并构建出 `olist_sales_wide` 订单大宽表。
- **Dashboard**: 使用 Streamlit + Plotly 构建交互式数据看板。

## 📁 项目结构
```text
olist-retail-data-platform/
├── data/                  # 原始 CSV 存放目录 (gitignore)
├── sql/                   # 业务分析 SQL 集合
├── src/
│   ├── extract.py         # 数据抽取与基础类型修正
│   ├── load.py            # 连接 MySQL 并写入原始表
│   ├── transform.py       # Retail 数据质量体检与清洗
│   └── transform_olist.py # Olist 多表关联与宽表建模
├── app/
│   └── dashboard.py       # Streamlit 可视化看板
├── run_all.py             # 一键执行 ETL 全流程脚本
├── requirements.txt       # Python 依赖
└── .env                   # 数据库账号密码配置 (gitignore)