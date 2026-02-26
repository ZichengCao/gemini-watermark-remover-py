#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从背景图中提取 Alpha Map 数据用于 JavaScript 版本

运行此脚本生成 alpha map JSON 文件，然后将数据复制到 watermark-remover.js 中
"""

import json
from pathlib import Path
from PIL import Image


def extract_alpha_map(image_path: Path) -> list:
    """从背景图提取 alpha map

    Alpha 值取 RGB 通道的最大值，归一化到 [0, 1]

    Args:
        image_path: 背景图片路径

    Returns:
        Alpha 值列表 (一维数组，行主序)
    """
    img = Image.open(image_path)
    arr = img.load()

    width, height = img.size
    alpha_map = []

    for y in range(height):
        for x in range(width):
            # 取 RGB 三个通道的最大值作为 alpha
            if img.mode == 'RGB':
                r, g, b = arr[x, y][:3]
            else:
                r, g, b = arr[x, y][:3]

            alpha = max(r, g, b) / 255.0
            alpha_map.append(alpha)

    return alpha_map


def alpha_map_to_js_array(alpha_map: list, indent: int = 12) -> str:
    """将 alpha map 转换为 JavaScript 数组格式

    Args:
        alpha_map: alpha 值列表
        indent: 缩进空格数

    Returns:
        JavaScript 数组字符串
    """
    # 将数据格式化为每行 16 个值
    lines = []
    for i in range(0, len(alpha_map), 16):
        chunk = alpha_map[i:i+16]
        values = ', '.join(f'{v:.6f}' for v in chunk)
        lines.append(' ' * indent + values)

    return '[\n' + ',\n'.join(lines) + '\n' + ' ' * (indent - 4) + ']'


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    assets_dir = project_root / "assets" / "gemini_watermark"

    # 检查背景图是否存在
    bg_48 = assets_dir / "bg_48.png"
    bg_96 = assets_dir / "bg_96.png"

    if not bg_48.exists():
        print(f"错误: 未找到 {bg_48}")
        print("请先运行 extract_bg_images.py 生成背景图")
        return

    if not bg_96.exists():
        print(f"错误: 未找到 {bg_96}")
        print("请先运行 extract_bg_images.py 生成背景图")
        return

    # 提取 alpha map
    print("正在提取 48px alpha map...")
    alpha_48 = extract_alpha_map(bg_48)
    print(f"✓ 提取完成: {len(alpha_48)} 个值")

    print("正在提取 96px alpha map...")
    alpha_96 = extract_alpha_map(bg_96)
    print(f"✓ 提取完成: {len(alpha_96)} 个值")

    # 保存为 JSON（用于备份）
    json_output = script_dir / "alpha_maps.json"
    with open(json_output, 'w') as f:
        json.dump({
            '48': alpha_48,
            '96': alpha_96
        }, f, indent=2)
    print(f"✓ 已保存 JSON 到: {json_output}")

    # 生成 JavaScript 代码片段
    js_output = script_dir / "alpha_maps.js"
    with open(js_output, 'w', encoding='utf-8') as f:
        f.write('/**\n')
        f.write(' * Alpha Maps for Gemini Watermark Remover\n')
        f.write(' * Auto-generated from background images\n')
        f.write(' */\n\n')
        f.write('// Alpha map for 48px watermark\n')
        f.write('const ALPHA_48 = ' + alpha_map_to_js_array(alpha_48) + ';\n\n')
        f.write('// Alpha map for 96px watermark\n')
        f.write('const ALPHA_96 = ' + alpha_map_to_js_array(alpha_96) + ';\n')
    print(f"✓ 已生成 JavaScript 到: {js_output}")

    # 生成替换说明
    print("\n" + "="*60)
    print("使用说明:")
    print("="*60)
    print("1. 打开 alpha_maps.js 查看生成的数据")
    print("2. 将 ALPHA_48 的数据替换 watermark-remover.js 中的 getAlpha48() 返回值")
    print("3. 将 ALPHA_96 的数据替换 watermark-remover.js 中的 getAlpha96() 返回值")
    print("4. 或者直接删除 getAlpha48() 和 getAlpha96() 方法，")
    print("   在 loadAlphaMaps() 中直接使用: return { 48: ALPHA_48, 96: ALPHA_96 };")
    print("="*60)


if __name__ == "__main__":
    main()
