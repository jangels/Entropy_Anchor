#!/bin/bash
# 启动 FastAPI 服务的便捷脚本

echo "🚀 启动 Entropy_Anchor API 服务..."
uv run uvicorn api.routes:app --reload --host 0.0.0.0 --port 8003
