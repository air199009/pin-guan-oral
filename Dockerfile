# =============================================================================
# DentalPilot AI - Docker 镜像
# =============================================================================
FROM python:3.10-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

# 创建目录
RUN mkdir -p models data/uploads data/feedback outputs logs

# 环境变量
ENV GRADIO_PORT=7860
ENV GRADIO_HOST=0.0.0.0
ENV LOG_LEVEL=INFO

EXPOSE 7860

# 启动
CMD ["python", "app.py"]
