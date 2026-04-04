import argparse
from downloader import download_tiles
from stitcher import stitch_all, stitch_region

def main():
    parser = argparse.ArgumentParser(description="🗺️ Z-8 瓦片地图处理工具 (供 Agent 调用)")
    subparsers = parser.add_subparsers(dest="command", help="可用命令", required=True)

    # --- 命令 1: download ---
    parser_dl = subparsers.add_parser("download", help="尝试下载瓦片 (可指定边界，不指定则使用 config 默认值)")
    parser_dl.add_argument("-z", "--zoom", type=int, required=True, help="缩放层级 (如 5 或 8)")
    parser_dl.add_argument("--x-start", type=int, help="起始 X 坐标")
    parser_dl.add_argument("--x-end", type=int, help="结束 X 坐标")
    parser_dl.add_argument("--y-start", type=int, help="起始 Y 坐标")
    parser_dl.add_argument("--y-end", type=int, help="结束 Y 坐标")

    # --- 命令 2: stitch-all ---
    parser_sa = subparsers.add_parser("stitch-all", help="拼接本地已有的全部瓦片")
    parser_sa.add_argument("-z", "--zoom", type=int, required=True, help="缩放层级")

    # --- 命令 3: stitch-region ---
    parser_sr = subparsers.add_parser("stitch-region", help="局部拼接 (按指定边界)")
    parser_sr.add_argument("-z", "--zoom", type=int, required=True, help="缩放层级")
    parser_sr.add_argument("--min-x", type=int, required=True, help="最小 X 坐标")
    parser_sr.add_argument("--max-x", type=int, required=True, help="最大 X 坐标")
    parser_sr.add_argument("--min-y", type=int, required=True, help="最小 Y 坐标")
    parser_sr.add_argument("--max-y", type=int, required=True, help="最大 Y 坐标")

    args = parser.parse_args()

    if args.command == "download":
        download_tiles(args.zoom, args.x_start, args.x_end, args.y_start, args.y_end)
    elif args.command == "stitch-all":
        stitch_all(args.zoom)
    elif args.command == "stitch-region":
        stitch_region(args.zoom, args.min_x, args.max_x, args.min_y, args.max_y)

if __name__ == "__main__":
    main()
