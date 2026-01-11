#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态构建脚本
根据 Git 标签自动添加版本号到输出文件名
"""

import sys
import subprocess
import re
from pathlib import Path

def get_git_tag():
    """从 Git 获取当前标签"""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True,
            check=True
        )
        tag = result.stdout.strip()
        if tag and not tag.startswith('v'):
            tag = f'v{tag}'
        return tag
    except:
        return None

def get_version_from_tag(tag):
    """从标签中提取版本号（去除 v 前缀）"""
    if not tag:
        return None
    return tag.lstrip('v')

if __name__ == '__main__':
    # 获取版本号
    version = get_git_tag()

    if not version:
        print("❌ 错误: 无法获取 Git 标签")
        print("\n请先创建标签:")
        print("   git tag v1.0.1")
        print("   git push origin v1.0.1")
        sys.exit(1)

    version_num = get_version_from_tag(version)

    # 设置输出文件名
    exe_name = f'GeminiWatermarkRemover_{version_num}'

    print(f"📦 构建版本: {version}")
    print(f"📁 输出文件: {exe_name}.exe")
    print()

    # 修改 spec 文件
    spec_file = Path('gemini_watermark_remover.spec')
    spec_content = spec_file.read_text(encoding='utf-8')

    # 替换 name
    import re
    spec_content = re.sub(
        r"name='GeminiWatermarkRemover'",
        f"name='{exe_name}'",
        spec_content
    )

    # 写回临时 spec 文件
    temp_spec = Path('gemini_watermark_remover_build.spec')
    temp_spec.write_text(spec_content, encoding='utf-8')

    print(f"✅ 已生成构建配置: {temp_spec}")

    # 调用 PyInstaller
    import os
    os.system(f'pyinstaller --clean {temp_spec}')

    # 清理临时文件
    if temp_spec.exists():
        temp_spec.unlink()

    print()
    print("=" * 50)
    print(f"✅ 构建完成!")
    print(f"📍 输出位置: dist/{exe_name}.exe")
    print("=" * 50)
