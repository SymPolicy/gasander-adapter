import math
from config import settings

def map_tile_z5_to_z8_range(x5: int, y5: int) -> dict:
    """
    将一张 z5 瓦片的坐标，映射为 z8 层级对应的 8x8 (共64张) 瓦片坐标范围
    """
    delta_z = 8 - 5
    scale = 2 ** delta_z
    
    x8_start = x5 * scale
    y8_start = y5 * scale
    
    return {
        "x_range": (x8_start, x8_start + scale - 1),
        "y_range": (y8_start, y8_start + scale - 1)
    }

def map_pixel_z5_to_z8_tile(x5: int, y5: int, pixel_x: int, pixel_y: int) -> tuple:
    """
    已知目标在 z5 瓦片内的像素坐标 (pixel_x, pixel_y)，
    计算出它在 z8 层级中具体属于哪一张瓦片 (x8, y8)
    """
    delta_z = 8 - 5
    scale = 2 ** delta_z
    tile_size = settings["tile_size"]  # 从配置读取
    
    offset_x = math.floor((pixel_x / tile_size) * scale)
    offset_y = math.floor((pixel_y / tile_size) * scale)
    
    x8 = x5 * scale + offset_x
    y8 = y5 * scale + offset_y
    
    return (x8, y8)