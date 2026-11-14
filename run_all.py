# run_all.py
import subprocess
import sys
import os


def run_script(script_path, description):
    print(f"\n{'=' * 50}")
    print(f"🚀 正在执行: {description}")
    print(f"{'=' * 50}")

    # 使用当前 Python 解释器运行子脚本
    result = subprocess.run([sys.executable, script_path], capture_output=False)

    if result.returncode != 0:
        print(f"❌ {description} 执行失败，请检查上方报错。")
        sys.exit(1)
    print(f"✅ {description} 执行成功！")


if __name__ == '__main__':
    print("🌟 开始 Olist-Retail-Data-Platform 全流程 ETL 与建模 🌟")

    # 1. 加载原始数据到 MySQL
    run_script('src/load.py', '加载原始数据至 MySQL (E & L)')

    # 2. 清洗 Retail 数据并拆表
    run_script('src/transform.py', '清洗 Online Retail II 数据 (T)')

    # 3. 构建 Olist 宽表
    run_script('src/transform_olist.py', '构建 Olist 核心业务宽表 (T)')

    print("\n🎉 所有数据流水线执行完毕！")
    print("👉 请在终端运行以下命令启动数据看板：")
    print("   streamlit run app/dashboard.py")