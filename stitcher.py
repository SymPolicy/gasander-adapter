import os
import re
from PIL import Image
from config import settings

def _get_available_tiles(z: int):
    """内部辅助函数：获取已下载的瓦片列表"""
    # 直接使用解析好的绝对路径
    tile_dir = settings["tiles_save_dir"] / f"z{z}"
    if not tile_dir.exists():
        return []
        
    pattern = re.compile(rf"z{z}-tile_(-?\d+)_(-?\d+)\.png")
    tiles_info = []
    for file_name in os.listdir(tile_dir):
        match = pattern.match(file_name)
        if match:
            tiles_info.append({
                "x": int(match.group(1)), 
                "y": int(match.group(2)), 
                "path": tile_dir / file_name
            })
    return tiles_info

def stitch_region(z: int, min_x: int, max_x: int, min_y: int, max_y: int):
    all_tiles = _get_available_tiles(z)
    target_tiles = [
        t for t in all_tiles 
        if min_x <= t["x"] <= max_x and min_y <= t["y"] <= max_y
    ]
    
    if not target_tiles:
        print(f"⚠️ 在指定范围 X:[{min_x},{max_x}] Y:[{min_y},{max_y}] 内未找到 Z{z} 的瓦片文件。")
        return

    _do_stitch(z, target_tiles, f"map_z{z}_region_{min_x}_{max_x}_{min_y}_{max_y}.png")

def stitch_all(z: int):
    target_tiles = _get_available_tiles(z)
    if not target_tiles:
        print(f"⚠️ 没有找到任何 Z{z} 的瓦片文件。请先下载。")
        return
        
    _do_stitch(z, target_tiles, f"map_z{z}_full.png")

def _do_stitch(z: int, tiles_info: list, output_filename: str):
    tile_size = settings["tile_size"]
    # 直接使用解析好的绝对路径
    out_dir = settings["full_map_save_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    
    min_x = min(t["x"] for t in tiles_info)
    max_x = max(t["x"] for t in tiles_info)
    min_y = min(t["y"] for t in tiles_info)
    max_y = max(t["y"] for t in tiles_info)
    
    width = (max_x - min_x + 1) * tile_size
    height = (max_y - min_y + 1) * tile_size
    
    print(f"开始拼接 Z{z}，实际边界 X:[{min_x}, {max_x}] Y:[{min_y}, {max_y}]...")
    full_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    for t in tiles_info:
        img = Image.open(t["path"])
        paste_x = (t["x"] - min_x) * tile_size
        paste_y = (t["y"] - min_y) * tile_size
        full_image.paste(img, (paste_x, paste_y))

    output_path = out_dir / output_filename
    full_image.save(output_path)
    print(f"✅ 拼接完成！文件已保存至: {output_path.absolute()}")