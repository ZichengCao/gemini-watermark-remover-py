# 部署到 GitHub Pages 完整指南

## 已创建的文件

```
web/
├── index.html           # 主页面
├── alpha_maps.js        # 真实的 alpha map 数据（从 bg_48.png 和 bg_96.png 提取）
├── watermark-remover.js # 核心算法
├── app.js              # 应用逻辑
├── extract_alpha_map.py # 提取 alpha map 的脚本
└── README.md           # 部署说明
```

---

## 部署方案

### 方案 A：使用独立的 GitHub Pages 仓库（推荐）

#### 步骤 1：创建新仓库

在 GitHub 上创建一个新仓库：
- 仓库名：`your-username.github.io`
- 设为 Public（公开）
- 初始化 README

#### 步骤 2：克隆仓库并添加文件

```bash
# 克隆仓库
git clone https://github.com/your-username/your-username.github.io.git
cd your-username.github.io

# 复制 web 目录下的所有文件到仓库
# 将 gemini-watermark-remover-py/web/ 下的文件复制到该目录

# 提交并推送
git add .
git commit -m "Add Gemini Watermark Remover web app"
git push origin main
```

#### 步骤 3：访问网站

等待 1-2 分钟后，访问：
```
https://your-username.github.io/
```

---

### 方案 B：从当前项目部署

#### 步骤 1：创建 gh-pages 分支

```bash
cd gemini-watermark-remover-py

# 创建 gh-pages 分支（孤立分支，没有历史）
git checkout --orphan gh-pages

# 清空所有文件
git rm -rf .

# 复制 web 目录下的文件
cp -r web/* .

# 添加文件
git add .
git commit -m "Initial GitHub Pages"

# 推送分支
git push origin gh-pages
```

#### 步骤 2：配置 GitHub Pages

1. 进入仓库的 **Settings**
2. 点击 **Pages**
3. 在 **Source** 中选择：
   - Branch: `gh-pages`
   - Folder: `/root`
4. 点击 **Save**

#### 步骤 3：访问网站

等待 1-2 分钟后，访问：
```
https://your-username.github.io/gemini-watermark-remover-py/
```

---

### 方案 C：使用 docs 文件夹

#### 步骤 1：在项目中创建 docs 文件夹

```bash
cd gemini-watermark-remover-py

# 创建 docs 文件夹（如果不存在）
mkdir -p docs

# 复制 web 目录下的文件到 docs
cp -r web/* docs/
```

#### 步骤 2：提交并推送

```bash
git add docs/
git commit -m "Add GitHub Pages web app to docs folder"
git push origin main
```

#### 步骤 3：配置 GitHub Pages

1. 进入仓库的 **Settings**
2. 点击 **Pages**
3. 在 **Source** 中选择：
   - Branch: `main` (或 `master`)
   - Folder: `/docs`
4. 点击 **Save**

#### 步骤 4：访问网站

等待 1-2 分钟后，访问：
```
https://your-username.github.io/gemini-watermark-remover-py/
```

---

## 本地测试

在部署前，可以先在本地测试：

```bash
cd web

# Python 3
python -m http.server 8000

# 或 Python 2
python -m SimpleHTTPServer 8000
```

然后在浏览器打开：
```
http://localhost:8000
```

---

## 验证部署

### 检查 GitHub Pages 状态

1. 进入仓库的 **Settings** → **Pages**
2. 查看顶部是否显示：
   ```
   Your site is live at https://your-username.github.io/...
   ```

### 常见问题

**Q: 404 Not Found**
A: 等待几分钟再刷新，GitHub Pages 需要时间部署

**Q: 样式显示异常**
A: 打开浏览器控制台（F12），检查是否有加载错误

**Q: 图片处理失败**
A: 确保：
- 上传的是 Gemini 生成的图片（右下角有水印）
- 图片格式是 PNG、JPEG 或 WEBP

---

## 下一步

部署成功后，你可以：
1. 分享链接给其他人使用
2. 添加自定义域名（在 Pages 设置中）
3. 添加更多功能（如批量处理、更多水印选项）
