"""
DentalPilot AI - YOLOv8 影像检测模块
负责：牙齿检测、病灶识别、CBCT关键解剖结构检测
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from PIL import Image

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

from config import config


class DentalDetector:
    """口腔影像AI检测器"""

    # 牙齿编号（FDI标准）
    TOOTH_LABELS = {
        # 右上 (1象限)
        11: "上中切牙", 12: "上侧切牙", 13: "上尖牙",
        14: "上第一前磨牙", 15: "上第二前磨牙",
        16: "上第一磨牙", 17: "上第二磨牙", 18: "上第三磨牙(智齿)",
        # 左上 (2象限)
        21: "上中切牙", 22: "上侧切牙", 23: "上尖牙",
        24: "上第一前磨牙", 25: "上第二前磨牙",
        26: "上第一磨牙", 27: "上第二磨牙", 28: "上第三磨牙(智齿)",
        # 左下 (3象限)
        31: "下中切牙", 32: "下侧切牙", 33: "下尖牙",
        34: "下第一前磨牙", 35: "下第二前磨牙",
        36: "下第一磨牙", 37: "下第二磨牙", 38: "下第三磨牙(智齿)",
        # 右下 (4象限)
        41: "下中切牙", 42: "下侧切牙", 43: "下尖牙",
        44: "下第一前磨牙", 45: "下第二前磨牙",
        46: "下第一磨牙", 47: "下第二磨牙", 48: "下第三磨牙(智齿)",
    }

    # 病灶类别
    DISEASE_LABELS = {
        0: "龋齿(疑似)",
        1: "根尖病变",
        2: "牙周炎",
        3: "牙结石",
        4: "牙髓炎",
        5: "阻生齿",
        6: "残根",
        7: "缺失牙",
        8: "修复体",
        9: "种植体",
    }

    def __init__(self):
        self.detect_model = None
        self.disease_model = None
        self.model_loaded = False

    def load_models(self):
        """加载模型权重"""
        if not YOLO_AVAILABLE:
            print("⚠️ ultralytics 未安装，请运行: pip install ultralytics")
            return False

        try:
            # 牙齿检测模型
            detect_path = Path(config.YOLO_DETECT_MODEL)
            if detect_path.exists():
                self.detect_model = YOLO(str(detect_path))
                print(f"✅ 加载牙齿检测模型: {detect_path}")
            else:
                # 使用预训练的yolov8n作为占位符（首次使用）
                print(f"⚠️ 牙齿检测模型不存在: {detect_path}")
                print("   将使用YOLOv8n预训练权重（占位符），训练后会自动替换")
                self.detect_model = YOLO("yolov8n.pt")

            # 病灶识别模型
            disease_path = Path(config.YOLO_DISEASE_MODEL)
            if disease_path.exists():
                self.disease_model = YOLO(str(disease_path))
                print(f"✅ 加载病灶识别模型: {disease_path}")
            else:
                print(f"⚠️ 病灶识别模型不存在: {disease_path}")
                self.disease_model = None

            self.model_loaded = True
            return True

        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False

    def detect_teeth(self, image: Image.Image, conf: float = 0.25) -> Dict:
        """
        检测牙齿并标注
        Args:
            image: PIL Image
            conf: 置信度阈值
        Returns:
            {
                "annotated_image": 标注后的图片,
                "teeth_count": 牙齿数量,
                "teeth_list": [{"id": 1, "label": "...", "conf": 0.9, "bbox": [...]}, ...]
            }
        """
        if not self.model_loaded:
            self.load_models()

        if self.detect_model is None:
            return {
                "annotated_image": image,
                "teeth_count": 0,
                "teeth_list": [],
                "error": "模型未加载"
            }

        try:
            # 转换PIL Image为numpy
            img_array = np.array(image)

            # YOLOv8推理
            results = self.detect_model(img_array, conf=conf, verbose=False)

            # 解析结果
            teeth_list = []
            for r in results:
                boxes = r.boxes
                for i, box in enumerate(boxes):
                    cls_id = int(box.cls[0])
                    conf_score = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                    # FDI编号（如果模型输出的是class id）
                    fdi_id = cls_id + 11  # 简化映射
                    label = self.TOOTH_LABELS.get(fdi_id, f"牙位{cls_id}")

                    teeth_list.append({
                        "id": i + 1,
                        "fdi": fdi_id,
                        "label": label,
                        "conf": round(conf_score, 3),
                        "bbox": [round(c) for c in bbox]
                    })

            # 生成标注图
            annotated = results[0].plot() if results else img_array
            annotated_img = Image.fromarray(annotated)

            return {
                "annotated_image": annotated_img,
                "teeth_count": len(teeth_list),
                "teeth_list": teeth_list,
                "error": None
            }

        except Exception as e:
            return {
                "annotated_image": image,
                "teeth_count": 0,
                "teeth_list": [],
                "error": str(e)
            }

    def detect_diseases(self, image: Image.Image, conf: float = 0.3) -> Dict:
        """
        检测口腔病灶
        """
        if not self.model_loaded:
            self.load_models()

        if self.disease_model is None:
            return {
                "annotated_image": image,
                "diseases": [],
                "error": "病灶识别模型未加载（需要先训练）"
            }

        try:
            img_array = np.array(image)
            results = self.disease_model(img_array, conf=conf, verbose=False)

            diseases = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf_score = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()

                    disease_name = self.DISEASE_LABELS.get(cls_id, f"异常{cls_id}")
                    diseases.append({
                        "label": disease_name,
                        "conf": round(conf_score, 3),
                        "bbox": [round(c) for c in bbox]
                    })

            annotated = results[0].plot() if results else img_array
            annotated_img = Image.fromarray(annotated)

            return {
                "annotated_image": annotated_img,
                "diseases": diseases,
                "error": None
            }

        except Exception as e:
            return {
                "annotated_image": image,
                "diseases": [],
                "error": str(e)
            }

    def full_analysis(self, image: Image.Image, conf: float = 0.25) -> Dict:
        """完整分析：牙齿检测 + 病灶识别"""
        teeth_result = self.detect_teeth(image, conf)
        disease_result = self.detect_diseases(image, conf)

        return {
            "teeth": teeth_result,
            "diseases": disease_result,
            "final_image": disease_result["annotated_image"]
        }


# 全局实例
detector = DentalDetector()


if __name__ == "__main__":
    # 测试
    config.print_config()
    detector.load_models()
    print("✅ 检测器初始化完成")
