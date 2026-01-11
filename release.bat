@echo off
REM 一键发布脚本
REM 功能：构建安装包 + 打 Git 标签 + 发布 GitHub Release

echo ========================================
echo   Gemini Watermark Remover 发布工具
echo ========================================
echo.

REM 检查环境变量
if not defined GITHUB_TOKEN (
    echo ❌ 错误: 未设置 GITHUB_TOKEN 环境变量
    echo.
    echo 请先设置 GitHub Token:
    echo 1. 访问 https://github.com/settings/tokens
    echo 2. 生成新的 Personal Access Token (需要 repo 权限)
    echo 3. 设置环境变量:
    echo    set GITHUB_TOKEN=your_token
    echo.
    pause
    exit /b 1
)

REM 检查 PyGithub
python -c "import github" 2>nul
if %errorlevel% neq 0 (
    echo ❌ 缺少 PyGithub 库，正在安装...
    pip install PyGithub
)

REM 步骤 1: 提交代码
echo.
echo [1/4] 检查 Git 状态...
git status --short
echo.
set /p commit_msg="请输入提交信息（留空跳过）: "

if not "%commit_msg%"=="" (
    git add -A
    git commit -m "%commit_msg%"
    echo ✅ 代码已提交
)

REM 步骤 2: 构建安装包
echo.
echo [2/4] 构建安装包...
call build_installer.bat
if %errorlevel% neq 0 (
    echo ❌ 构建失败
    pause
    exit /b 1
)

REM 步骤 3: 打标签并推送
echo.
echo [3/4] 创建 Git 标签...
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin master
git push origin v1.0.1 --force
if %errorlevel% neq 0 (
    echo ❌ Git 推送失败
    pause
    exit /b 1
)
echo ✅ 标签创建并推送成功

REM 步骤 4: 发布到 GitHub Release
echo.
echo [4/4] 发布到 GitHub Release...
python publish_release.py
if %errorlevel% neq 0 (
    echo ❌ 发布失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   🎉 发布完成！
echo ========================================
pause
