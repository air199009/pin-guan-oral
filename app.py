"""
DentalPilot AI - Gradio Web界面
提供：医生上传影像 → AI分析 → 出报告 → 医生签字 → 下载
"""
import os
import json
from datetime import datetime
from typing import Optional
import gradio as gr
from PIL import Image

from config import config
from detect import detector
from report_gen import report_generator


# ============== 反馈收集 ==============

FEEDBACK_FILE = config.DATA_DIR / "feedback.jsonl"


def save_feedback(image_path: str, ai_result: str, doctor_correction: str):
    """保存医生反馈（用于后续模型训练）"""
    feedback = {
        "timestamp": datetime.now().isoformat(),
        "image_path": image_path,
        "ai_result": ai_result,
        "doctor_correction": doctor_correction,
        "client": config.CLIENT_NAME,
    }
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback, ensure_ascii=False) + "\n")
    return f"✅ 反馈已保存，感谢！"


# ============== 主分析函数 ==============

def analyze_image(
    image: Image.Image,
    image_type: str,
    clinical_info: str,
    use_vision: bool,
    confidence: float,
):
    """
    完整影像分析流程
    """
    if image is None:
        return None, "❌ 请先上传影像", "", "", ""

    # 1. 牙齿检测
    teeth_result = detector.detect_teeth(image, conf=confidence)

    # 2. 病灶识别
    disease_result = detector.detect_diseases(image, conf=confidence)

    # 3. 生成报告
    report_result = report_generator.generate_report(
        image=image,
        image_type=image_type,
        teeth_count=teeth_result["teeth_count"],
        diseases=disease_result["diseases"],
        clinical_info=clinical_info or "无",
        use_vision=use_vision,
    )

    # 4. 准备UI输出
    annotated_image = disease_result["annotated_image"]

    # 牙齿信息
    teeth_info = json.dumps(teeth_result["teeth_list"], ensure_ascii=False, indent=2)
    if not teeth_info or teeth_info == "[]":
        teeth_info = "⚠️ 未检测到牙齿（需要先训练模型或加载权重）"

    # 病灶信息
    diseases_info = json.dumps(disease_result["diseases"], ensure_ascii=False, indent=2)
    if not diseases_info or diseases_info == "[]":
        diseases_info = "✅ 暂未检测到明显异常（需要先训练病灶识别模型）"

    # 报告
    if report_result["success"]:
        report_text = f"""## 影像分析报告

> 📌 **AI辅助分析结果，最终诊断以医生签字为准**
> 🔧 模型: {report_result['provider']} / {report_result['model']} ({report_result['mode']} mode)

---

{report_result['report']}

---

**诊所信息：** {config.CLIENT_NAME}  
**分析时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    else:
        report_text = f"❌ 报告生成失败\n\n{report_result['report']}"

    # 保存上传图片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = config.UPLOADS_DIR / f"{timestamp}.png"
    try:
        image.save(save_path)
    except Exception:
        pass

    return (
        annotated_image,
        report_text,
        teeth_info,
        diseases_info,
        f"📁 已保存: {save_path.name}",
    )


def submit_feedback(correction_text: str, progress=gr.Progress()):
    """提交医生反馈"""
    if not correction_text:
        return "⚠️ 请填写修正内容"
    progress(0.5, "保存反馈中...")
    save_feedback(
        image_path="latest",
        ai_result="see latest",
        doctor_correction=correction_text,
    )
    progress(1.0, "完成")
    return "✅ 反馈已保存到 data/feedback.jsonl"


# ============== Gradio界面 ==============

def build_ui():
    """构建Gradio Web界面"""

    with gr.Blocks(
        title="DentalPilot AI 口腔影像分析工具",
        theme=gr.themes.Soft(),
    ) as demo:

        gr.Markdown(f"""
# 🦷 DentalPilot AI 口腔影像分析工具

**版本：** {config.APP_VERSION}  |  **客户端：** {config.CLIENT_NAME}  |  **API：** {report_generator.provider}

> ⚠️ 本工具为AI辅助分析工具，结果仅供参考，最终诊断以医生签字为准。
        """)

        with gr.Tabs():
            # ============ Tab 1: 影像分析 ============
            with gr.TabItem("📊 影像分析"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📥 输入")
                        image_input = gr.Image(
                            label="上传口腔影像",
                            type="pil",
                            sources=["upload", "clipboard"],
                            height=400,
                        )
                        image_type = gr.Radio(
                            choices=["全景片", "CBCT", "根尖片", "头颅侧位片", "口内照"],
                            value="全景片",
                            label="影像类型",
                        )
                        clinical_info = gr.Textbox(
                            label="临床信息（主诉/病史）",
                            placeholder="例：患者男，35岁，主诉左下后牙冷热痛一周...",
                            lines=2,
                        )
                        with gr.Row():
                            use_vision = gr.Checkbox(
                                label="使用视觉模型（看图分析）",
                                value=True,
                            )
                            confidence = gr.Slider(
                                minimum=0.1,
                                maximum=0.9,
                                value=0.25,
                                step=0.05,
                                label="检测置信度",
                            )
                        analyze_btn = gr.Button(
                            "🚀 开始AI分析",
                            variant="primary",
                            size="lg",
                        )

                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 检测结果")
                        output_image = gr.Image(
                            label="标注后影像",
                            type="pil",
                            height=400,
                        )
                        save_info = gr.Textbox(
                            label="保存信息",
                            interactive=False,
                        )

                with gr.Row():
                    with gr.Column():
                        teeth_output = gr.Textbox(
                            label="🦷 牙齿检测结果",
                            lines=8,
                            interactive=False,
                        )
                    with gr.Column():
                        diseases_output = gr.Textbox(
                            label="⚠️ 病灶识别结果",
                            lines=8,
                            interactive=False,
                        )

                gr.Markdown("### 📋 AI报告草稿")
                report_output = gr.Markdown(
                    value="*等待分析...*"
                )

                with gr.Row():
                    download_btn = gr.Button("📥 复制报告文本")
                    polish_btn = gr.Button("✨ 润色为患者易懂版")

                analyze_btn.click(
                    fn=analyze_image,
                    inputs=[image_input, image_type, clinical_info, use_vision, confidence],
                    outputs=[output_image, report_output, teeth_output, diseases_output, save_info],
                )

            # ============ Tab 2: 医生反馈（用于持续训练） ============
            with gr.TabItem("🩺 医生反馈"):
                gr.Markdown("""
### 医生修正反馈

> 💡 您的每次修正都会用于模型持续优化，让AI越用越准。

请在下方填写您对AI结果的修正意见。
                """)
                with gr.Row():
                    with gr.Column():
                        feedback_image = gr.Image(
                            label="上传同一张影像（方便我们对照）",
                            type="pil",
                        )
                        correction_text = gr.Textbox(
                            label="医生修正意见",
                            placeholder="例：AI标注的第16牙是龋齿，实际为正常磨耗；第26牙AI未识别，临床检查有根尖暗影...",
                            lines=8,
                        )
                        feedback_btn = gr.Button(
                            "📤 提交反馈",
                            variant="primary",
                        )
                    with gr.Column():
                        feedback_output = gr.Textbox(
                            label="提交结果",
                            lines=3,
                            interactive=False,
                        )
                        gr.Markdown("""
### 📊 累计反馈统计
                        """)
                        feedback_count = gr.Textbox(
                            label="已收集反馈数",
                            value="0",
                            interactive=False,
                        )

                feedback_btn.click(
                    fn=submit_feedback,
                    inputs=[correction_text],
                    outputs=[feedback_output],
                )

            # ============ Tab 3: 系统信息 ============
            with gr.TabItem("⚙️ 系统信息"):
                gr.Markdown(f"""
### 当前配置

| 项目 | 值 |
|---|---|
| 客户端 | {config.CLIENT_NAME} |
| 版本 | {config.APP_VERSION} |
| 激活API | {report_generator.provider} |
| Minimax | {'✅' if config.MINIMAX_API_KEY else '❌'} |
| DeepSeek | {'✅' if config.DEEPSEEK_API_KEY else '❌'} |
| 通义千问 | {'✅' if config.QWEN_API_KEY else '❌'} |
| 智谱 | {'✅' if config.ZHIPU_API_KEY else '❌'} |
| Gradio端口 | {config.GRADIO_PORT} |

### 模型状态

- 牙齿检测模型: `{'✅ 已加载' if detector.detect_model else '❌ 未加载'}`
- 病灶识别模型: `{'✅ 已加载' if detector.disease_model else '⚠️ 未训练'}`

### 文件位置

- 上传影像: `{config.UPLOADS_DIR}`
- 输出报告: `{config.OUTPUTS_DIR}`
- 反馈数据: `{FEEDBACK_FILE}`

### 部署说明

- 详细文档：见 `docs/客户部署手册.md`
- 销售合同：见 `docs/销售合同模板.md`
- 培训视频：见 `docs/演示PPT.md`
                """)

        gr.Markdown(f"""
---
© 2026 DentalPilot AI | 数据本地化 · 算力云端 | v{config.APP_VERSION}
        """)

    return demo


# ============== 启动 ==============

if __name__ == "__main__":
    config.print_config()
    print("\n🚀 正在启动 DentalPilot AI...")
    print(f"📍 访问地址: http://{config.GRADIO_HOST}:{config.GRADIO_PORT}")
    if config.GRADIO_SHARE:
        print("🌐 将生成公网分享链接...")
    print()

    # 预加载模型
    print("⏳ 加载AI模型中...")
    detector.load_models()
    print()

    demo = build_ui()
    demo.launch(
        server_name=config.GRADIO_HOST,
        server_port=config.GRADIO_PORT,
        share=config.GRADIO_SHARE,
        show_error=True,
    )
