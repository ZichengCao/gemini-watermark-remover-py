#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
"""

from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QIcon
from qfluentwidgets import Pivot, SegmentedWidget, FluentIcon

from .pages.image_gemini_watermark_page import ImageGeminiWatermarkPage
from .pages.file_monitor_page import FileMonitorPage


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

        # 创建导航栏
        self.pivot = Pivot(self.central_widget)
        self.pivot.setStyleSheet("""
            Pivot {
                background: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 8px 16px;
            }
        """)
        layout.addWidget(self.pivot)

        # 创建页面堆栈
        self.stacked_widget = QStackedWidget(self.central_widget)
        layout.addWidget(self.stacked_widget)

        # 创建页面
        self.watermark_page = ImageGeminiWatermarkPage(self.central_widget)
        self.monitor_page = FileMonitorPage(self.central_widget)

        # 添加页面到堆栈
        self.stacked_widget.addWidget(self.watermark_page)
        self.stacked_widget.addWidget(self.monitor_page)

        # 添加导航项
        self.pivot.addItem(
            routeKey='watermark',
            text='批量处理',
            onClick=lambda: self.switch_page('watermark'),
            icon=FluentIcon.DOCUMENT
        )
        self.pivot.addItem(
            routeKey='monitor',
            text='实时监控',
            onClick=lambda: self.switch_page('monitor'),
            icon=FluentIcon.VIEW
        )

        # 设置默认页面
        self.pivot.setCurrentItem('watermark')
        self.stacked_widget.setCurrentWidget(self.watermark_page)

    def switch_page(self, route_key: str):
        """切换页面"""
        if route_key == 'watermark':
            self.stacked_widget.setCurrentWidget(self.watermark_page)
        elif route_key == 'monitor':
            self.stacked_widget.setCurrentWidget(self.monitor_page)
