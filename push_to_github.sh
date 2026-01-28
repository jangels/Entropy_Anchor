#!/bin/bash
# 推送 Entropy_Anchor 到 GitHub 的脚本

set -e

echo "🚀 准备推送 Entropy_Anchor 到 GitHub..."

# 检查是否已设置远程仓库
if ! git remote get-url origin &>/dev/null; then
    echo "📦 添加远程仓库..."
    git remote add origin https://github.com/jangels/Entropy_Anchor.git
else
    echo "✅ 远程仓库已存在"
    git remote set-url origin https://github.com/jangels/Entropy_Anchor.git
fi

# 重命名分支为 main（如果当前是 master）
current_branch=$(git branch --show-current)
if [ "$current_branch" = "master" ]; then
    echo "🔄 重命名分支 master -> main"
    git branch -M main
fi

# 显示当前状态
echo ""
echo "📊 当前状态:"
git status --short

echo ""
echo "📝 最近的提交:"
git log --oneline -1

echo ""
echo "🌐 远程仓库:"
git remote -v

echo ""
echo "⚠️  请手动执行以下命令推送代码:"
echo ""
echo "  git push -u origin main"
echo ""
echo "或者如果远程仓库已有内容，使用:"
echo ""
echo "  git push -u origin main --force"
echo ""
