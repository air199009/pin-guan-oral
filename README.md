# 🦷 DentalPilot AI - 口腔影像分析工具

> **本地部署版** | 数据不出诊所 · 算力云端 · 一次性付费

## ✨ 核心特性

- 🏠 **数据本地化** - 影像数据不出诊所，符合医疗数据合规要求
- ☁️ **算力云端** - 不需要本地GPU，调用云端大模型API出报告
- 💰 **0服务器成本** - 模型跑在客户电脑，推理调API按次付费
- 🚀 **一键部署** - Docker一键启动，无需复杂配置
- 🩺 **医生签字流程** - AI辅助分析，最终诊断以医生签字为准
- 🔄 **持续优化** - 医生反馈回流，模型越用越准

## 🎯 客户场景

| 客户类型 | 部署位置 | 网络 | API调用 |
|---|---|---|---|
| 民营连锁口腔诊所 | 客户电脑 | 内网/外网 | 调云端API |
| 公立医院 | 医院电脑 | 内网 | 走API代理 |
| 卫健委/学校 | 本地服务器 | 内网 | 走API代理 |
| 体检机构 | 客户电脑 | 外网 | 调云端API |

## 📋 系统架构

```
┌──────────────────────────────────────────┐
│  客户电脑（本地部署）                       │
│  ┌────────────────────────────────────┐  │
│  │  Gradio Web界面 (端口 7860)        │  │
│  │  YOLOv8 牙齿检测 (本地推理)        │  │
│  │  YOLOv8 病灶识别 (本地推理)        │  │
│  │  DentalSegmentator (CBCT)          │  │
│  └────────────────────────────────────┘  │
│              ↓ HTTPS API                  │
│  ┌────────────────────────────────────┐  │
│  │  云端大模型 (Minimax/DeepSeek)     │  │
│  │  - 影像分析 - 报告生成              │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## 🚀 快速开始（5分钟）

### 1. 准备环境

```bash
# 克隆仓库
git clone https://github.com/air199009/pin-guan-oral.git
cd pin-guan-oral

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API Key

```bash
# 复制环境变量模板
# Windows CMD:
copy .env.example .env
# PowerShell:
Copy-Item .env.example .env
# Linux/Mac:
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
notepad .env   # Windows
nano .env      # Linux/Mac
```

**至少填一个：**
- `MINIMAX_API_KEY` （推荐，你已订阅）
- `DEEPSEEK_API_KEY` （备选，便宜）
- `QWEN_API_KEY` （备选，国内稳定）

### 3. 启动服务

```bash
python app.py
```

打开浏览器访问：http://127.0.0.1:7860

### 4. 训练模型（首次使用）

打开 [Google Colab](https://colab.research.google.com/) ，上传 `train_colab.ipynb`，按步骤运行训练。

训练完成后把权重放到 `models/` 目录。

## 📁 项目结构

```
pin-guan-oral/
├── app.py                   # Gradio 主程序
├── config.py                # 配置管理
├── detect.py                # YOLOv8 检测模块
├── report_gen.py            # AI报告生成
├── train_colab.ipynb        # Google Colab 训练笔记本
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量模板
├── .gitignore               # Git 忽略文件
├── Dockerfile               # Docker 镜像
├── docker-compose.yml       # Docker Compose
├── deploy.sh                # 一键部署脚本
├── README.md                # 本文件
├── docs/                    # 文档
│   ├── 客户部署手册.md
│   ├── 销售合同模板.md
│   └── 演示PPT.md
├── models/                  # 模型权重（不放Git）
│   ├── yolov8n_teeth.pt
│   └── yolov8n_disease.pt
├── data/                    # 数据
│   ├── uploads/             # 客户上传影像
│   └── feedback.jsonl       # 医生反馈
└── outputs/                 # 输出报告
```

## 🔧 常用命令

```bash
# 启动服务
python app.py

# 设置 Gradio 公网分享链接（演示用）
GRADIO_SHARE=true python app.py

# 训练模型（Google Colab）
# 打开 train_colab.ipynb 一键运行

# Docker 部署
docker-compose up -d

# 查看日志
tail -f logs/app.log
```

## 📊 模型性能指标

训练完成后会显示：

| 指标 | 说明 | 目标 |
|---|---|---|
| mAP50 | IoU=0.5时的平均精度 | > 0.85 |
| mAP50-95 | 0.5-0.95 IoU的均值 | > 0.65 |
| Precision | 精确率 | > 0.80 |
| Recall | 召回率 | > 0.75 |

## 💰 商业模型

| 项目 | 价格 |
|---|---|
| 一次性软件部署费 | 3万/家（首单1.5万） |
| API月费 | 客户自付（50-200元/月） |
| 年度升级服务 | 1万/年 |
| 多人培训 | 2000元/场 |
| API代理维护 | 0（我维护） |

## 🔒 合规说明

- **产品定位**：AI辅助影像分析工具，非医疗器械
- **监管依据**：参考菲森科技粤械注准20252210997（二类，**明确"不包括自动分析诊断功能"**）
- **责任划分**：最终诊断以医生签字为准，AI仅供医生参考
- **数据隐私**：本地部署，影像数据不出诊所

## 🛠️ 技术栈

| 用途 | 技术 |
|---|---|
| Web界面 | Gradio 4.x |
| 目标检测 | YOLOv8 (Ultralytics) |
| 影像处理 | pydicom, OpenCV, PIL |
| 大模型API | Minimax M3 / DeepSeek / 通义千问 / 智谱 |
| 部署 | Docker, PyInstaller |
| 代码托管 | GitHub |

## 📞 支持与联系

- **项目主页**：https://github.com/air199009/pin-guan-oral
- **问题反馈**：GitHub Issues
- **商务合作**：联系开发者
- **文档**：[docs/](docs/)

## 📜 许可证

仅限商业用途，未经授权禁止二次销售。

---

**版本**：v0.1.0  
**最后更新**：2026-06-18
