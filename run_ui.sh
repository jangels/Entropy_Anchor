#!/bin/bash
# 启动 Streamlit UI 的便捷脚本

echo "🌀 启动 Entropy_Anchor UI..."
uv run streamlit run ui/app.py --server.port 8501
