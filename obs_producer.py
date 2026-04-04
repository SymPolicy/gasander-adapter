import obspython as obs
import os
import time

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# --- 全局变量 ---
interval = 2.0
enabled = False
target_dir = "T:/obs-output/raw"
max_storage_gb = 10
cleanup_percent = 80

# --- 模块化配置 ---
use_scaling = True      # 选项1：是否缩放到 1280x720
use_compression = True  # 选项2：是否转换为 JPG 压缩
jpg_quality = 85
target_width = 1280
target_height = 720

capture_count = 0 

def script_description():
    return "<b>数据采集生产者 (V7 模块化控制版)</b><br>支持独立控制缩放与压缩逻辑。"

def script_defaults(settings):
    obs.obs_data_set_default_double(settings, "interval", 2.0)
    obs.obs_data_set_default_bool(settings, "enabled", False)
    obs.obs_data_set_default_string(settings, "target_dir", "T:/obs-output/raw")
    obs.obs_data_set_default_int(settings, "max_storage_gb", 10)
    obs.obs_data_set_default_int(settings, "cleanup_percent", 80)
    
    # 拆分后的默认值
    obs.obs_data_set_default_bool(settings, "use_scaling", True)
    obs.obs_data_set_default_bool(settings, "use_compression", True)
    obs.obs_data_set_default_int(settings, "jpg_quality", 85)

def script_properties():
    props = obs.obs_properties_create()
    
    obs.obs_properties_add_float(props, "interval", "采集间隔 (秒)", 0.1, 60.0, 0.1)
    obs.obs_properties_add_bool(props, "enabled", "开启自动化采集")
    obs.obs_properties_add_path(props, "target_dir", "图片存储路径", obs.OBS_PATH_DIRECTORY, "", "")
    
    # 存储保护
    obs.obs_properties_add_int(props, "max_storage_gb", "存储上限 (GB)", 1, 5000, 1)
    obs.obs_properties_add_int(props, "cleanup_percent", "清理至目标比例 (%)", 1, 99, 1)
    
    # --- 拆分的两个选项 ---
    obs.obs_properties_add_bool(props, "use_scaling", "启用 720p 尺寸缩放 (1280x720)")
    obs.obs_properties_add_bool(props, "use_compression", "启用 JPG 格式压缩转换")
    obs.obs_properties_add_int(props, "jpg_quality", "JPG 质量 (1-100)", 1, 100, 1)
    
    return props

def script_update(settings):
    global interval, enabled, target_dir, max_storage_gb, cleanup_percent
    global use_scaling, use_compression, jpg_quality
    
    interval = max(0.1, obs.obs_data_get_double(settings, "interval"))
    enabled = obs.obs_data_get_bool(settings, "enabled")
    target_dir = obs.obs_data_get_string(settings, "target_dir")
    max_storage_gb = obs.obs_data_get_int(settings, "max_storage_gb")
    cleanup_percent = obs.obs_data_get_int(settings, "cleanup_percent")
    
    use_scaling = obs.obs_data_get_bool(settings, "use_scaling")
    use_compression = obs.obs_data_get_bool(settings, "use_compression")
    jpg_quality = obs.obs_data_get_int(settings, "jpg_quality")

    # 定时器管理
    obs.timer_remove(do_capture)
    if enabled:
        obs.timer_add(do_capture, int(interval * 1000))

def process_image(file_path):
    """根据选项进行组合处理"""
    if not HAS_PILLOW or (not use_scaling and not use_compression):
        return

    try:
        time.sleep(0.1) # 避开 IO 锁
        
        with Image.open(file_path) as img:
            # 逻辑 A：缩放
            if use_scaling:
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # 逻辑 B：压缩转换
            if use_compression:
                # 转换为 RGB 后存为 JPG
                img_final = img.convert("RGB")
                new_path = file_path.rsplit('.', 1)[0] + ".jpg"
                img_final.save(new_path, "JPEG", quality=jpg_quality)
                # 只有转了 JPG 后才删原 PNG
                os.remove(file_path)
            else:
                # 只缩放不转 JPG，则覆盖原 PNG 或另存为缩小的 PNG
                img.save(file_path, "PNG")
                
    except Exception as e:
        print(f"[Processor] 异常: {e}")

# --- 以下事件监听与采集逻辑保持不变 ---
def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_SCREENSHOT_TAKEN:
        path = obs.obs_frontend_get_last_screenshot()
        if path and path.lower().endswith('.png'):
            process_image(path)

def do_capture():
    global capture_count
    if not enabled: return
    if hasattr(obs, 'obs_frontend_take_screenshot'):
        obs.obs_frontend_take_screenshot()

    capture_count += 1
    if capture_count >= 15:
        run_storage_guardian()
        capture_count = 0

def run_storage_guardian():
    if not target_dir or not os.path.exists(target_dir): return
    max_bytes = max_storage_gb * 1024 * 1024 * 1024
    target_bytes = max_bytes * (cleanup_percent / 100.0)
    try:
        files = []
        total = 0
        with os.scandir(target_dir) as it:
            for e in it:
                if e.is_file():
                    s = e.stat()
                    files.append({'p': e.path, 't': s.st_mtime, 's': s.st_size})
                    total += s.st_size
        if total > max_bytes:
            files.sort(key=lambda x: x['t'])
            for f in files:
                os.remove(f['p'])
                total -= f['s']
                if total <= target_bytes: break
    except: pass

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)

def script_unload():
    obs.obs_frontend_remove_event_callback(on_event)
    obs.timer_remove(do_capture)