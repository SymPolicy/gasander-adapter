import requests
from config import settings

def download_tiles(z: int, x_start: int = None, x_end: int = None, y_start: int = None, y_end: int = None):
    if None in (x_start, x_end, y_start, y_end):
        ranges = settings["probe_ranges"].get(str(z))
        if not ranges:
            print(f"❌ 未提供坐标，且 config 中无 Z{z} 的默认范围。")
            return
        x_start, x_end = ranges["x_start"], ranges["x_end"]
        y_start, y_end = ranges["y_start"], ranges["y_end"]

    # 直接使用解析好的绝对路径
    base_tile_dir = settings["tiles_save_dir"]
    base_url = settings["map_base_url"]
    
    z_dir = base_tile_dir / f"z{z}"
    z_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"开始尝试下载 Z{z} 瓦片, 范围 X:[{x_start},{x_end}], Y:[{y_start},{y_end}]...")
    print(f"保存路径: {z_dir.absolute()}")
    
    success_count = 0
    for x in range(x_start, x_end + 1):
        for y in range(y_start, y_end + 1):
            url = base_url.format(z=z, x=x, y=y)
            file_path = z_dir / f"tile_z{z}_{x}_{y}.png"
            
            if file_path.exists():
                success_count += 1
                continue
                
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    success_count += 1
                    print(f"✅ 成功: {file_path.name}")
            except Exception:
                pass
                
    print(f"下载探测结束。共确认 {success_count} 张有效瓦片。")