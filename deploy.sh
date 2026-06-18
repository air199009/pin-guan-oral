#!/bin/bash
# =============================================================================
# DentalPilot AI - 一键部署脚本（Linux/Mac/Git Bash on Windows）
# =============================================================================

set -e

echo "==============================================="
echo "  DentalPilot AI - 一键部署"
echo "==============================================="
echo ""

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    echo "   请先安装 Python 3.10+"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 2. 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi
echo "✅ 虚拟环境已就绪"

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip -q

# 5. 安装依赖
echo "📦 安装依赖（首次运行约 3-5 分钟）..."
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"

# 6. 创建 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo ""
    echo "⚠️  请编辑 .env 文件，填入你的 API Key："
    echo "   - MINIMAX_API_KEY（推荐）"
    "   - 或 DEEPSEEK_API_KEY / QWEN_API_KEY / ZHIPU_API_KEY"
    echo ""
    read -p "是否现在编辑 .env 文件？[y/N] " yn
    if [[ "$yn" == "y" || "$yn" == "Y" ]]; then
        ${EDITOR:-nano} .env
    fi
fi
echo "✅ .env 文件就绪"

# 7. 创建目录
echo "📁 创建目录..."
mkdir -p models data/uploads outputs logs

# 8. 启动服务
echo ""
echo "==============================================="
echo "  启动 DentalPilot AI 服务"
echo "==============================================="
echo "  访问地址: http://127.0.0.1:7860"
echo "  按 Ctrl+C 停止"
echo "==============================================="
echo ""

python app.py
