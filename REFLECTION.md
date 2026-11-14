# 项目反思 (Reflection)

## 1. 实现思路与架构
项目采用了经典的 ETL 分层架构。考虑到两份数据集截然不同的特征：
- **Online Retail II (英国零售)**：采用“先体检，后治理”的策略，重点处理缺失值、退货单（C 开头）、异常价格。
- **Olist (巴西电商)**：采用“星型模型”思路，将 9 张散表通过主外键进行 Join，聚合支付金额后生成大宽表 `olist_sales_wide`，为后续 SQL 分析和看板提供统一的数据底座。

## 2. 踩坑与解决记录 (重点)
在从 0 到 1 搭建的过程中，遇到了几个典型的数据工程问题：

- **坑 1：邮编前导零丢失**
  - 现象：Olist 的邮编 `01151` 读进 Pandas 后变成了 `1151`。
  - 解决：在 `pd.read_csv` 时强制指定 `dtype={'customer_zip_code_prefix': str}`，保留字符串格式。
- **坑 2：零售数据的脏乱差**
  - 现象：退货单伴随着负数的 Quantity 和 Price。
  - 解决：利用 `Invoice` 列是否以 'C' 开头，以及 `Quantity < 0` 作为条件，用 `df[~is_return]` 拆出了干净的 `retail_sales` 表和 `retail_returns` 表，防止污染销售指标。
- **坑 3：Streamlit 执行 SQL 报错**
  - 现象：`ValueError: unsupported format character 'Y'`
  - 解决：因为 Pandas 底层对 `%` 敏感，将 SQL 中的 `DATE_FORMAT(..., '%Y-%m')` 转义为 `'%%Y-%%m'` 后解决。
- **坑 4：数据泄露风险**
  - 现象：初次推送 GitHub 时，误将包含 260 万行数据的 CSV 和 `.env` 密码文件提交。
  - 解决：通过 `git rm -r --cached .` 清除缓存，配置好 `.gitignore`，并重建 Git 历史，确保推送至远程仓库的只有纯净的代码。

## 3. 未完成与改进方向
- 目前 Olist 的地理位置数据（100 万行）尚未在 Streamlit 中做地图可视化。
- 后续可以引入 Docker，将 MySQL 和 Python 环境容器化，实现真正意义上的“一键部署”。
- 针对 LLM 文本抽取：Olist 有 `order_reviews` 表（葡萄牙语评论），后续可以接入 LLM，将评论文本提取为结构化字段（如：物流满意度、商品质量），丰富分析维度。