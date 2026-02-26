# GitHub Pages 部署指南

## 部署步骤

### 1. 创建 GitHub Pages 仓库

在 GitHub 上创建一个新仓库，命名为 `your-username.github.io`（或者使用现有的 gh-pages 分支）

### 2. 添加文件到项目

将 `web/` 目录下的文件复制到你的 GitHub Pages 仓库的根目录或 `docs/` 文件夹：

```
your-username.github.io/
├── index.html
├── watermark-remover.js
├── app.js
└── README.md
```

### 3. 推送到 GitHub

```bash
cd your-username.github.io
git add .
git commit -m "Add Gemini Watermark Remover web app"
git push origin main
```

### 4. 启用 GitHub Pages

1. 进入仓库的 **Settings**
2. 点击左侧菜单的 **Pages**
3. 在 **Source** 下选择：
   - Branch: `main` (或 `master`)
   - Folder: `/root` (或 `/docs` 如果放在 docs 文件夹)
4. 点击 **Save**

### 5. 访问网站

几分钟后，你的网站将在以下地址可用：

```
https://your-username.github.io/
```

---

## 从当前项目部署

如果你想直接从 `gemini-watermark-remover-py` 仓库部署：

### 方案 1: 使用 docs 文件夹

1. 在项目根目录创建 `docs` 文件夹（如果不存在）
2. 将 `web/` 目录下的文件复制到 `docs/` 文件夹
3. 在 GitHub 仓库设置中，将 Pages source 设置为 `/docs`

### 方案 2: 使用 gh-pages 分支

```bash
# 在 gemini-watermark-remover-py 项目中
git checkout --orphan gh-pages
git rm -rf .
cp -r web/* .
git add .
git commit -m "Initial GitHub Pages"
git push origin gh-pages
```

然后在 GitHub Pages 设置中选择 `gh-pages` 分支。

---

## 注意事项

### Alpha Map 数据

当前的 `watermark-remover.js` 使用简化的 alpha map 模拟数据。要获得最佳效果，需要：

1. 从 `assets/gemini_watermark/bg_48.png` 和 `bg_96.png` 提取真实的 alpha 值
2. 将提取的数据替换 `getAlpha48()` 和 `getAlpha96()` 方法中的数据

运行以下 Python 脚本提取 alpha map：

```python
from PIL import Image
import json

def extract_alpha_map(image_path, output_path):
    """Extract alpha map from background image"""
    img = Image.open(image_path)
    arr = img.load()

    width, height = img.size
    alpha_map = []

    for y in range(height):
        for x in range(width):
            # Get max RGB value and normalize to [0, 1]
            r, g, b = arr[x, y][:3]
            alpha = max(r, g, b) / 255.0
            alpha_map.append(alpha)

    # Save as JSON
    with open(output_path, 'w') as f:
        json.dump(alpha_map, f)

    return alpha_map

# Extract for both sizes
extract_alpha_map('assets/gemini_watermark/bg_48.png', 'alpha_48.json')
extract_alpha_map('assets/gemini_watermark/bg_96.png', 'alpha_96.json')
```

然后将生成的 JSON 数据复制到 JS 代码中。

---

## 测试本地部署

在部署到 GitHub 前，你可以先在本地测试：

1. 安装 Python HTTP 服务器：
   ```bash
   python -m http.server 8000
   ```

2. 在浏览器打开：
   ```
   http://localhost:8000
   ```

---

## 故障排除

### 404 错误
- 确保 GitHub Pages 设置正确
- 等待几分钟后刷新页面

### 样式显示异常
- 检查浏览器控制台是否有错误
- 确保所有 JS 文件正确加载

### 图片处理失败
- 检查浏览器控制台错误信息
- 确保上传的是 Gemini 生成的图片
