import json
from pathlib import Path

# 获取 config.py 所在的绝对路径，作为项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()
CONFIG_FILE = PROJECT_ROOT / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"找不到配置文件: {CONFIG_FILE.absolute()}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        
    # 核心修改：将 json 里的相对路径，自动拼接为基于项目根目录的绝对路径 Path 对象
    config_data["tiles_save_dir"] = PROJECT_ROOT / config_data["tiles_save_dir"]
    config_data["full_map_save_dir"] = PROJECT_ROOT / config_data["full_map_save_dir"]
    
    return config_data

# 全局配置字典
settings = load_config()
