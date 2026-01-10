#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
"""

from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
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

        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 设置布局
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 直接显示水印移除页面
        self.watermark_page = ImageGeminiWatermarkPage()
        layout.addWidget(self.watermark_page)
