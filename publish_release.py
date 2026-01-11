#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Release 自动发布脚本

使用方法：
1. 确保 GitHub Token 已设置 (环境变量 GITHUB_TOKEN)
2. 先运行 build_installer.bat 构建安装包
3. 先创建并推送 Git 标签（如 git tag v1.0.1 && git push origin v1.0.1）
4. 运行此脚本: python publish_release.py

环境变量：
- GITHUB_TOKEN: GitHub 个人访问令牌 (需要 repo 权限)

可选参数：
- --version VERSION: 指定版本号（默认从 Git 标签获取）
- --repo REPO: 指定仓库名（默认从 git remote 获取）
"""

import os
import sys
import subprocess
import re
from pathlib import Path

try:
    from github import Github
except ImportError:
    print("❌ 缺少 PyGithub 库，请安装:")
    print("   pip install PyGithub")
    sys.exit(1)


def get_git_tag():
    """从 Git 获取当前标签"""
    try:
        # 获取最近的标签
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
    except subprocess.CalledProcessError:
        return None


def get_git_remote_url():
    """从 Git remote 获取仓库信息"""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        # 解析 URL 获取 owner/repo
        # 支持 HTTPS: https://github.com/owner/repo.git
        # 支持 SSH: git@github.com:owner/repo.git
        patterns = [
            r'github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$',  # HTTPS or SSH
            r'github\.com/([^/]+)/([^/]+)',  # HTTPS without .git
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                return f"{owner}/{repo}"

        raise ValueError(f"无法解析仓库 URL: {url}")
    except subprocess.CalledProcessError:
        return None


def get_release_notes(version):
    """从 README.md 提取更新日志"""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return None

    content = readme_path.read_text(encoding='utf-8')

    # 查找对应的版本更新日志
    # 匹配 ### v1.0.1 (2026-01-11) 到下一个 ### 之间的内容
    pattern = rf'### {re.escape(version)}.*?\n(.*?)(?=\n### v|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        notes = match.group(1).strip()
        return f"## 📝 更新日志\n\n{notes}"

    return None


# 解析命令行参数
VERSION = None
REPO_NAME = None

for i, arg in enumerate(sys.argv[1:], 1):
    if arg == '--version' and i + 1 < len(sys.argv):
        VERSION = sys.argv[i + 1]
    elif arg == '--repo' and i + 1 < len(sys.argv):
        REPO_NAME = sys.argv[i + 1]

# 如果没有指定，自动获取
if not VERSION:
    VERSION = get_git_tag()
    if not VERSION:
        print("❌ 错误: 无法获取版本号")
        print("\n请先创建 Git 标签:")
        print("   git tag v1.0.1")
        print("   git push origin v1.0.1")
        print("\n或者使用 --version 参数指定:")
        print("   python publish_release.py --version v1.0.1")
        sys.exit(1)

if not REPO_NAME:
    REPO_NAME = get_git_remote_url()
    if not REPO_NAME:
        print("❌ 错误: 无法获取仓库名")
        print("\n请使用 --repo 参数指定:")
        print("   python publish_release.py --repo owner/repo")
        sys.exit(1)

# Release 信息
RELEASE_TITLE = f"Gemini Watermark Remover {VERSION}"

# 尝试从 README 读取更新日志，否则使用默认内容
release_notes_content = get_release_notes(VERSION)

if release_notes_content:
    # 简化的 Release Notes
    RELEASE_NOTES = f"""## 🎉 {VERSION} 发布

{release_notes_content}

---

Full Changelog: https://github.com/{REPO_NAME}/compare/v1.0.0...{VERSION}
"""
else:
    RELEASE_NOTES = f"""## 🎉 Gemini Watermark Remover {VERSION}

Release {VERSION} 已发布！

详细更新日志请查看 [README](https://github.com/{REPO_NAME}/blob/master/README.md)。

Full Changelog: https://github.com/{REPO_NAME}/compare/v1.0.0...{VERSION}
"""


def get_built_version():
    """获取已构建的版本号"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        return None

    # 查找 exe 文件
    exe_files = list(dist_dir.glob("GeminiWatermarkRemover_*.exe"))
    if not exe_files:
        return None

    # 从文件名提取版本号: GeminiWatermarkRemover_1.0.1.exe
    import re
    for exe in exe_files:
        match = re.search(r'GeminiWatermarkRemover_([\d.]+)\.exe$', exe.name)
        if match:
            return match.group(1)

    return None


def check_build_version():
    """检查构建版本是否匹配当前标签"""
    current_version = VERSION.lstrip('v')
    built_version = get_built_version()

    if not built_version:
        print(f"⚠️  未找到构建文件")
        return False

    if built_version != current_version:
        print(f"⚠️  版本不匹配:")
        print(f"   当前标签: {VERSION}")
        print(f"   构建版本: v{built_version}")
        print()
        choice = input("是否重新构建? (Y/n): ").strip().lower()
        if choice != 'n':
            return True  # 需要重新构建
        else:
            print("⚠️  使用已有构建文件继续发布...")
            return False
    else:
        print(f"✅ 版本匹配: {VERSION}")
        return False


def build_executable():
    """构建可执行文件"""
    print()
    print("=" * 50)
    print("  开始构建")
    print("=" * 50)
    print()

    import subprocess
    result = subprocess.run([sys.executable, 'build.py'])
    if result.returncode != 0:
        print("❌ 构建失败")
        sys.exit(1)
    print("✅ 构建成功")


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
    print(f"📦 版本: {VERSION}")
    print(f"📍 仓库: {REPO_NAME}")
    print()

    try:
        g = Github(token)
        repo = g.get_repo(REPO_NAME)

        print(f"✅ 成功连接到仓库: {REPO_NAME}")
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


if __name__ == "__main__":
    print("=" * 50)
    print("  GitHub Release 自动发布工具")
    print("=" * 50)
    print()
    print(f"📦 版本: {VERSION}")
    print(f"📍 仓库: {REPO_NAME}")
    print()

    # 检查构建版本
    need_rebuild = check_build_version()

    if need_rebuild:
        build_executable()
        print()

    # 创建 GitHub Release
    try:
        create_github_release()
    except KeyboardInterrupt:
        print("\n❌ 用户取消")
        sys.exit(1)
