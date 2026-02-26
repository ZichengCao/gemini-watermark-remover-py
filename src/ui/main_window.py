#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
"""

from pathlib import Path
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon

from .pages.image_gemini_watermark_page import ImageGeminiWatermarkPage


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Watermark Remover")
        self.resize(900, 700)

        # 设置窗口图标
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 创建并设置主页面
        self.watermark_page = ImageGeminiWatermarkPage()
        self.setCentralWidget(self.watermark_page)
