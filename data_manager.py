import os
import shutil
import time
import cv2
import numpy as np
import logging

# --- 配置 ---
BASE_DIR = "T:/local_monitor"
RAW_DIR = os.path.join(BASE_DIR, "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
TRASH_DIR = os.path.join(BASE_DIR, "trash")

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def is_garbage(frame):
    """
    极简清洗逻辑：
    1. 标准差检测：画面颜色太单一（纯黑、纯蓝）则剔除
    2. 亮度检测：平均亮度太低则剔除
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 1. 计算标准差 (活跃度)
    std_dev = np.std(gray)
    if std_dev < 15:  # 阈值可调，越小越严格
        return True, f"low_variation({std_dev:.1f})"
    
    # 2. 计算平均亮度
    avg_brightness = np.mean(gray)
    if avg_brightness < 20: # 画面太黑
        return True, f"too_dark({avg_brightness:.1f})"
    
    return False, None

def start_pipeline():
    logging.info("Styio 数据清洗流水线已启动...")
    
    # 确保文件夹存在
    for d in [PROCESSED_DIR, TRASH_DIR]:
        os.makedirs(d, exist_ok=True)

    while True:
        # 获取 raw 目录下所有的 jpg 文件
        files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith('.jpg')]
        
        for f in files:
            raw_path = os.path.join(RAW_DIR, f)
            
            # 读取并处理
            try:
                # 稍微等待文件写入完成，防止读取到空文件
                time.sleep(0.1)
                frame = cv2.imread(raw_path)
                if frame is None: continue

                garbage, reason = is_garbage(frame)
                
                if garbage:
                    logging.info(f"剔除垃圾图片: {f} | 原因: {reason}")
                    shutil.move(raw_path, os.path.join(TRASH_DIR, f))
                else:
                    # 可以在这里统一图片尺寸，方便后续 YOLO 训练
                    # frame = cv2.resize(frame, (1280, 720))
                    # cv2.imwrite(os.path.join(PROCESSED_DIR, f), frame)
                    
                    shutil.move(raw_path, os.path.join(PROCESSED_DIR, f))
                    logging.info(f">>> 有效数据入库: {f}")
            
            except Exception as e:
                logging.error(f"处理文件 {f} 时出错: {e}")

        # 每 2 秒检查一次文件夹
        time.sleep(2)

if __name__ == "__main__":
    start_pipeline()