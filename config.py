"""
DentalPilot AI - 配置模块
统一加载环境变量、API Key、模型路径
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

# 加载 .env 文件
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    """统一配置管理"""

    # ============== Minimax M3 ==============
    MINIMAX_API_KEY: Optional[str] = os.getenv("MINIMAX_API_KEY")
    MINIMAX_BASE_URL: str = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
    MINIMAX_MODEL: str = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")

    # ============== DeepSeek ==============
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_VL_MODEL: str = os.getenv("DEEPSEEK_VL_MODEL", "deepseek-vl")

    # ============== 通义千问 ==============
    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY")
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    QWEN_VL_MODEL: str = os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")

    # ============== 智谱 ==============
    ZHIPU_API_KEY: Optional[str] = os.getenv("ZHIPU_API_KEY")
    ZHIPU_BASE_URL: str = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    ZHIPU_VL_MODEL: str = os.getenv("ZHIPU_VL_MODEL", "glm-4v-plus")

    # ============== 模型路径 ==============
    YOLO_DETECT_MODEL: str = os.getenv("YOLO_DETECT_MODEL", "./models/yolov8n_teeth.pt")
    YOLO_DISEASE_MODEL: str = os.getenv("YOLO_DISEASE_MODEL", "./models/yolov8n_disease.pt")
    DENTAL_SEG_MODEL: str = os.getenv("DENTAL_SEG_MODEL", "./models/dental_segmentator.pt")

    # ============== 服务配置 ==============
    GRADIO_PORT: int = int(os.getenv("GRADIO_PORT", "7860"))
    GRADIO_HOST: str = os.getenv("GRADIO_HOST", "127.0.0.1")
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "False").lower() == "true"

    PROXY_PORT: int = int(os.getenv("PROXY_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ============== 业务 ==============
    CLIENT_NAME: str = os.getenv("CLIENT_NAME", "default")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")

    # ============== 路径 ==============
    PROJECT_ROOT: Path = PROJECT_ROOT
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    UPLOADS_DIR: Path = PROJECT_ROOT / "uploads"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    @classmethod
    def ensure_dirs(cls):
        """确保目录存在"""
        for d in [cls.MODELS_DIR, cls.DATA_DIR, cls.UPLOADS_DIR, cls.OUTPUTS_DIR, cls.LOGS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_active_provider(cls) -> str:
        """获取当前可用的API提供商"""
        if cls.MINIMAX_API_KEY and cls.MINIMAX_API_KEY.startswith("sk-"):
            return "minimax"
        if cls.DEEPSEEK_API_KEY and cls.DEEPSEEK_API_KEY.startswith("sk-"):
            return "deepseek"
        if cls.QWEN_API_KEY and cls.QWEN_API_KEY.startswith("sk-"):
            return "qwen"
        if cls.ZHIPU_API_KEY:
            return "zhipu"
        return "none"

    @classmethod
    def print_config(cls):
        """打印配置（隐藏key）"""
        print("=" * 60)
        print("DentalPilot AI 配置信息")
        print("=" * 60)
        print(f"  客户端名称: {cls.CLIENT_NAME}")
        print(f"  版本: {cls.APP_VERSION}")
        print(f"  激活API: {cls.get_active_provider()}")
        print(f"  Minimax: {'✓' if cls.MINIMAX_API_KEY else '✗'}")
        print(f"  DeepSeek: {'✓' if cls.DEEPSEEK_API_KEY else '✗'}")
        print(f"  通义千问: {'✓' if cls.QWEN_API_KEY else '✗'}")
        print(f"  智谱: {'✓' if cls.ZHIPU_API_KEY else '✗'}")
        print(f"  Gradio端口: {cls.GRADIO_PORT}")
        print("=" * 60)


# 全局单例
config = Config()
config.ensure_dirs()
