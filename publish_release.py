#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Release 自动发布脚本

使用方法：
1. 确保 GitHub Token 已设置 (环境变量 GITHUB_TOKEN)
2. 先运行 build_installer.bat 构建安装包
3. 运行此脚本: python publish_release.py

环境变量：
- GITHUB_TOKEN: GitHub 个人访问令牌 (需要 repo 权限)
"""

import os
import sys
from pathlib import Path

try:
    from github import Github
except ImportError:
    print("❌ 缺少 PyGithub 库，请安装:")
    print("   pip install PyGithub")
    sys.exit(1)


# 版本配置
VERSION = "v1.0.1"
REPO_NAME = "yourusername/gemini-watermarkRemover-py"  # 修改为你的仓库

# Release 信息
RELEASE_TITLE = f"Gemini Watermark Remover {VERSION}"
RELEASE_NOTES = f"""## 🎉 {VERSION} 更新内容

### ⚡ 新功能
- **实时监控** - 新增实时文件监控功能，自动处理目录中新下载的 Gemini 图片
- **自动归档** - 处理后的原始文件自动归档到 `Gemini Watermark Remover Archive` 文件夹
- **智能监听** - 支持文件创建和重命名事件，兼容浏览器下载场景
- **配置持久化** - 自动保存监控目录配置，重启后自动恢复
- **页面导航** - 添加顶部导航栏，支持批量处理和实时监控页面切换

### 🐛 Bug 修复
- 修复监控死循环问题，输出文件重命名为 `Clean_` 前缀
- 优化文件处理延迟机制

### ⚙️ 技术更新
- 新增 `watchdog` 库用于文件系统监控

### 📦 下载
- Windows: `GeminiWatermarkRemover-Setup.exe`
- 源代码: 请克隆本仓库

---

## 📖 使用说明

### 批量处理模式
1. 启动程序，切换到「批量处理」标签
2. 拖拽带水印的图片到窗口
3. 配置输出参数（可选）
4. 点击「开始处理」

### 实时监控模式
1. 切换到「实时监控」标签
2. 选择要监控的目录
3. 打开监控开关
4. 下载新图片，自动处理

---

## ⚠️ 注意事项

- 本工具仅限移除 Gemini AI 生成图片的水印
- 请勿用于非法用途
- 仅供学习和个人使用

Full Changelog: https://github.com/{REPO_NAME}/compare/v1.0.0...{VERSION}
"""


def create_github_release():
    """创建 GitHub Release"""

    # 获取 GitHub Token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ 错误: 未找到 GITHUB_TOKEN 环境变量")
        print("\n请设置 GitHub Token:")
        print("1. 访问 https://github.com/settings/tokens")
        print("2. 生成新的 Personal Access Token (需要 repo 权限)")
        print("3. 设置环境变量: set GITHUB_TOKEN=your_token")
        sys.exit(1)

    print(f"🔑 正在连接 GitHub...")

    try:
        g = Github(token)
        repo = g.get_repo(REPO_NAME)

        print(f"✅ 成功连接到仓库: {REPO_NAME}")
        print(f"📦 准备发布: {VERSION}")
        print()

        # 检查是否已存在该版本的 release
        try:
            existing_release = repo.get_release(VERSION)
            print(f"⚠️  Release {VERSION} 已存在")
            choice = input("是否删除并重新创建? (y/N): ").strip().lower()
            if choice == 'y':
                existing_release.delete()
                print(f"🗑️  已删除旧的 Release")
            else:
                print("❌ 取消发布")
                sys.exit(0)
        except:
            print(f"✅ Release {VERSION} 不存在，将创建新的")

        # 创建 Release
        print(f"📝 正在创建 Release...")
        release = repo.create_git_release(
            tag=VERSION,
            name=RELEASE_TITLE,
            message=RELEASE_NOTES,
            draft=False,
            prerelease=False
        )

        print(f"✅ Release 创建成功: {release.html_url}")

        # 查找安装包文件
        dist_dir = Path("installer_output")
        if not dist_dir.exists():
            print(f"⚠️  警告: 未找到 {dist_dir} 目录")
            print(f"   请先运行 build_installer.bat 构建安装包")
            print(f"\n💡 提示: 你可以手动上传文件到:")
            print(f"   {release.html_url}")
            return

        # 查找 exe 文件
        exe_files = list(dist_dir.glob("*.exe"))
        if not exe_files:
            print(f"⚠️  警告: 未找到安装包文件 (*.exe)")
            print(f"   请先运行 build_installer.bat 构建安装包")
            return

        # 上传安装包
        for exe_file in exe_files:
            print(f"📤 正在上传: {exe_file.name}")
            with open(exe_file, 'rb') as f:
                release.upload_asset(
                    f.name,
                    f.read(),
                    content_type='application/x-msdownload'
                )
            print(f"✅ 上传成功: {exe_file.name}")

        print()
        print("=" * 50)
        print(f"🎉 发布完成!")
        print(f"📍 Release 地址: {release.html_url}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_git_tag():
    """创建 Git 标签"""
    import subprocess

    print(f"🏷️  正在创建 Git 标签: {VERSION}")

    try:
        # 检查标签是否已存在
        result = subprocess.run(
            ['git', 'tag', '-l', VERSION],
            capture_output=True,
            text=True
        )

        if VERSION in result.stdout:
            print(f"⚠️  标签 {VERSION} 已存在")
            choice = input("是否删除并重新创建? (y/N): ").strip().lower()
            if choice == 'y':
                # 删除本地标签
                subprocess.run(['git', 'tag', '-d', VERSION], check=True)
                # 删除远程标签
                subprocess.run(['git', 'push', 'origin', f':refs/tags/{VERSION}'],
                             capture_output=True)
                print(f"🗑️  已删除旧标签")
            else:
                return

        # 创建标签
        subprocess.run([
            'git', 'tag', '-a', VERSION,
            '-m', f'Release {VERSION}'
        ], check=True)

        print(f"✅ 本地标签创建成功")

        # 推送标签到远程
        print(f"📤 正在推送标签到远程...")
        subprocess.run(['git', 'push', 'origin', VERSION], check=True)
        print(f"✅ 标签推送成功")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("  GitHub Release 自动发布工具")
    print("=" * 50)
    print()

    # 1. 创建 Git 标签
    try:
        create_git_tag()
        print()
    except KeyboardInterrupt:
        print("\n❌ 用户取消")
        sys.exit(1)

    # 2. 创建 GitHub Release
    try:
        create_github_release()
    except KeyboardInterrupt:
        print("\n❌ 用户取消")
        sys.exit(1)
