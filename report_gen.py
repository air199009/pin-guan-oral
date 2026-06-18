"""
DentalPilot AI - AI报告生成模块
支持：Minimax M3、DeepSeek、通义千问、智谱 GLM
出报告：基于检测结果 + 影像 + 临床信息
"""
import os
import base64
import io
from typing import List, Dict, Optional
from openai import OpenAI
from PIL import Image

from config import config


# ============== 提示词模板 ==============

REPORT_SYSTEM_PROMPT = """你是一名资深的口腔医学AI助手，专门为口腔医生撰写影像分析报告。

你的职责：
1. 根据AI检测结果（牙齿标注、病灶标注）撰写专业的影像分析报告草稿
2. 报告语言要专业但易懂，便于医生审核后与患者沟通
3. 严格按照"AI辅助参考，最终诊断以医生签字为准"的原则
4. 风险提示要明确，不夸大、不误导

报告结构：
- 患者基本信息
- 影像类型与质量
- 检测到的异常（按严重程度排序）
- 临床建议（仅供参考）
- 风险提示
"""


REPORT_USER_TEMPLATE = """
请根据以下口腔影像分析结果，撰写一份专业的影像分析报告草稿：

【影像类型】{image_type}
【检测到的牙齿数量】{teeth_count}
【检测到的异常情况】
{disease_list}

【临床背景信息】
{clinical_info}

【要求】
1. 使用专业但易懂的医学语言
2. 明确标注"AI辅助分析结果，最终诊断以医生签字为准"
3. 按严重程度排序异常情况
4. 给出建议性意见（仅供医生参考）
5. 控制在500字以内
6. 使用Markdown格式

请直接输出报告内容：
"""


class ReportGenerator:
    """AI报告生成器 - 支持多provider"""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config.get_active_provider()
        self.client = self._init_client()

    def _init_client(self):
        """根据provider初始化OpenAI兼容客户端"""
        if self.provider == "minimax":
            return OpenAI(
                api_key=config.MINIMAX_API_KEY,
                base_url=config.MINIMAX_BASE_URL
            )
        elif self.provider == "deepseek":
            return OpenAI(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL
            )
        elif self.provider == "qwen":
            return OpenAI(
                api_key=config.QWEN_API_KEY,
                base_url=config.QWEN_BASE_URL
            )
        elif self.provider == "zhipu":
            return OpenAI(
                api_key=config.ZHIPU_API_KEY,
                base_url=config.ZHIPU_BASE_URL
            )
        else:
            return None

    def _get_model_name(self) -> str:
        """获取当前provider的模型名"""
        mapping = {
            "minimax": config.MINIMAX_MODEL,
            "deepseek": config.DEEPSEEK_MODEL,
            "qwen": config.QWEN_MODEL,
            "zhipu": config.ZHIPU_VL_MODEL,
        }
        return mapping.get(self.provider, "gpt-3.5-turbo")

    def _image_to_base64(self, image: Image.Image) -> str:
        """图片转base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def generate_report(
        self,
        image: Image.Image,
        image_type: str = "全景片",
        teeth_count: int = 0,
        diseases: List[Dict] = None,
        clinical_info: str = "无",
        use_vision: bool = True,
    ) -> Dict:
        """
        生成AI影像分析报告
        Args:
            image: PIL Image（原始或标注后）
            image_type: 全景片/CBCT/根尖片
            teeth_count: 检测到的牙齿数量
            diseases: 病灶列表
            clinical_info: 临床背景
            use_vision: 是否使用视觉模型（直接看图）
        Returns:
            {"success": bool, "report": str, "provider": str, "model": str}
        """
        diseases = diseases or []
        disease_list = "\n".join([
            f"- {d.get('label', '未知异常')}: 置信度 {d.get('conf', 0)}"
            for d in diseases
        ]) or "暂未检测到明显异常"

        # 尝试使用视觉模型（直接看图）
        if use_vision and self._has_vision_support() and image is not None:
            return self._generate_with_vision(
                image, image_type, teeth_count, diseases, clinical_info
            )

        # 使用纯文本模型
        return self._generate_with_text(
            image_type, teeth_count, diseases, clinical_info
        )

    def _has_vision_support(self) -> bool:
        """检查当前provider是否支持视觉"""
        return self.provider in ["deepseek", "qwen", "zhipu"]

    def _generate_with_vision(
        self, image: Image.Image, image_type: str,
        teeth_count: int, diseases: List[Dict], clinical_info: str
    ) -> Dict:
        """使用视觉模型生成报告（直接看图）"""
        try:
            disease_list = "\n".join([
                f"- {d.get('label', '未知异常')}: 置信度 {d.get('conf', 0)}"
                for d in diseases
            ]) or "暂未检测到明显异常"

            img_base64 = self._image_to_base64(image)

            vision_model_map = {
                "deepseek": config.DEEPSEEK_VL_MODEL,
                "qwen": config.QWEN_VL_MODEL,
                "zhipu": config.ZHIPU_VL_MODEL,
            }
            model_name = vision_model_map.get(self.provider, self._get_model_name())

            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": REPORT_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": REPORT_USER_TEMPLATE.format(
                                    image_type=image_type,
                                    teeth_count=teeth_count,
                                    disease_list=disease_list,
                                    clinical_info=clinical_info
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.3,
            )

            return {
                "success": True,
                "report": response.choices[0].message.content,
                "provider": self.provider,
                "model": model_name,
                "mode": "vision"
            }
        except Exception as e:
            # 视觉模型失败，回退到文本模型
            print(f"⚠️ 视觉模型调用失败: {e}，回退到文本模型")
            return self._generate_with_text(
                image_type, teeth_count, diseases, clinical_info
            )

    def _generate_with_text(
        self, image_type: str, teeth_count: int,
        diseases: List[Dict], clinical_info: str
    ) -> Dict:
        """使用纯文本模型生成报告"""
        try:
            disease_list = "\n".join([
                f"- {d.get('label', '未知异常')}: 置信度 {d.get('conf', 0)}"
                for d in diseases
            ]) or "暂未检测到明显异常"

            response = self.client.chat.completions.create(
                model=self._get_model_name(),
                messages=[
                    {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                    {"role": "user", "content": REPORT_USER_TEMPLATE.format(
                        image_type=image_type,
                        teeth_count=teeth_count,
                        disease_list=disease_list,
                        clinical_info=clinical_info
                    )},
                ],
                max_tokens=1500,
                temperature=0.3,
            )

            return {
                "success": True,
                "report": response.choices[0].message.content,
                "provider": self.provider,
                "model": self._get_model_name(),
                "mode": "text"
            }
        except Exception as e:
            return {
                "success": False,
                "report": f"❌ 报告生成失败: {str(e)}\n\n请检查API key配置。",
                "provider": self.provider,
                "model": self._get_model_name(),
                "mode": "error"
            }

    def polish_report(self, report: str, style: str = "通俗易懂") -> str:
        """润色报告"""
        try:
            response = self.client.chat.completions.create(
                model=self._get_model_name(),
                messages=[
                    {
                        "role": "system",
                        "content": f"你是口腔医学专家。请将以下报告润色为{style}风格，便于医生与患者沟通。"
                    },
                    {"role": "user", "content": report}
                ],
                max_tokens=2000,
                temperature=0.5,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"润色失败: {e}\n\n原报告:\n{report}"


# 全局实例
report_generator = ReportGenerator()


if __name__ == "__main__":
    config.print_config()
    print(f"\n激活provider: {report_generator.provider}")
    if report_generator.client:
        print("✅ 报告生成器就绪")
    else:
        print("❌ 未配置API key，请在 .env 文件中配置")
