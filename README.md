# 🗺️ Z-8 瓦片地图处理工具 CLI 调用说明

本文档详细介绍了如何通过命令行接口 (CLI) 调用地图瓦片的下载与拼接功能。本工具支持智能体 (Agent) 通过 Shell 环境进行自动化流程编排。

## ⚙️ 1. 环境准备与配置

### 依赖安装
在执行任何命令前，请确保环境中已安装必要的 Python 依赖：
```bash
pip install requests Pillow
```

### 全局配置 (`config.json`)
工具的默认行为受 `config.json` 控制。调用前请确认配置文件的正确性：
```json
{
    "map_base_url": "[https://wiki-dev-patch-oss.oss-cn-hangzhou.aliyuncs.com/res/lkwg/map-3.0/](https://wiki-dev-patch-oss.oss-cn-hangzhou.aliyuncs.com/res/lkwg/map-3.0/){z}/tile-{x}_{y}.png",
    "tiles_save_dir": "external_resources/images/map_3_0/map_tiles",
    "full_map_save_dir": "external_resources/images/map_3_0/full_map",
    "tile_size": 256,
    "probe_ranges": {
        "5": {"x_start": -2, "x_end": 20, "y_start": -2, "y_end": 20},
        "8": {"x_start": -10, "x_end": 160, "y_start": -10, "y_end": 160}
    }
}
```
> **提示 (For Agents)：** 当调用 `download` 命令且未指定坐标边界时，程序将自动读取 `probe_ranges` 中的范围进行盲探。

---

## 🚀 2. CLI 命令详解

主程序入口为 `main.py`，支持三个核心子命令：`download`、`stitch-all` 和 `stitch-region`。

### 命令 1：`download` (瓦片下载)
用于从远程 OSS 尝试拉取指定范围内的地图瓦片。对于不存在的瓦片（404），程序会静默跳过。

**参数：**
* `-z`, `--zoom` **(必填)**: 缩放层级（例如 `5` 或 `8`）。
* `--x-start`: 尝试下载的起始 X 坐标。
* `--x-end`: 尝试下载的结束 X 坐标。
* `--y-start`: 尝试下载的起始 Y 坐标。
* `--y-end`: 尝试下载的结束 Y 坐标。

**调用示例：**
```bash
# 场景 A: 智能体不知道边界，使用 config.json 中的默认探测范围去“撞”边界
python main.py download -z 5

# 场景 B: 智能体已通过算法算出精确范围，进行定向下载（高效率）
python main.py download -z 8 --x-start 80 --x-end 87 --y-start 120 --y-end 127
```

### 命令 2：`stitch-all` (全图拼接)
扫描本地指定层级文件夹下所有已下载的瓦片，自动计算全局边界，并拼接成一张完整的大图。

**参数：**
* `-z`, `--zoom` **(必填)**: 需要拼接的缩放层级。

**调用示例：**
```bash
# 将本地 Z5 文件夹下所有零散的瓦片拼接为一张全图
python main.py stitch-all -z 5
```
*输出路径：`full_map_save_dir/map_z5_full.png`*

### 命令 3：`stitch-region` (局部精细拼接)
仅选取本地指定边界范围内的瓦片进行拼接。适用于 Z8 等高层级、数据量庞大的场景，避免生成超大图片导致内存溢出 (OOM)。

**参数：**
* `-z`, `--zoom` **(必填)**: 需要拼接的缩放层级。
* `--min-x` **(必填)**: 目标区域的最小 X 坐标。
* `--max-x` **(必填)**: 目标区域的最大 X 坐标。
* `--min-y` **(必填)**: 目标区域的最小 Y 坐标。
* `--max-y` **(必填)**: 目标区域的最大 Y 坐标。

**调用示例：**
```bash
# 仅拼接 Z8 层级下，X 在 [80, 87] 且 Y 在 [120, 127] 范围内的局部地图
python main.py stitch-region -z 8 --min-x 80 --max-x 87 --min-y 120 --max-y 127
```
*输出路径：`full_map_save_dir/map_z8_region_80_87_120_127.png`*

---

## 🤖 3. 智能体 (Agent) 标准工作流建议

如果你是一个自动化调用的 Agent，处理未知大地图的最佳实践路径如下：

1. **宏观探测：** 执行 `python main.py download -z 5` 获取低分辨率粗略地图的所有瓦片。
2. **宏观预览：** 执行 `python main.py stitch-all -z 5` 生成 Z5 完整概览图，用于图像识别或全局寻路。
3. **坐标映射：** 在 Z5 全图上定位目标后，调用 `mapper.py` 中的数学映射函数，算出 Z8 的目标区域区间（如 `X_start=80, X_end=87`）。
4. **微观获取：** 根据算出的边界，执行定向下载：`python main.py download -z 8 --x-start 80 --x-end 87 --y-start 120 --y-end 127`。
5. **微观拼接：** 对目标区域执行局部出图：`python main.py stitch-region -z 8 --min-x 80 --max-x 87 --min-y 120 --max-y 127`，以此获得高清任务地图。