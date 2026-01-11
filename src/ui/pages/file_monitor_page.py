#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监控页面
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PySide6.QtCore import Qt, QSettings
from qfluentwidgets import (
    TitleLabel, CaptionLabel, PushButton, PrimaryPushButton,
    CardWidget, LineEdit, BodyLabel, StrongBodyLabel,
    InfoBar, InfoBarPosition, SwitchButton, ScrollArea
)

from ...core.file_monitor import GeminiFileMonitor, ARCHIVE_FOLDER_NAME, FILE_PREFIX


class MonitorLogCard(CardWidget):
    """监控日志卡片"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_entries = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 标题
        title_layout = QHBoxLayout()
        title_label = BodyLabel("处理日志")
        title_label.setStyleSheet("color: #666; font-weight: 600;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # 日志区域（使用滚动区域）
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setMaximumHeight(300)
        self.scroll_area.setStyleSheet("ScrollArea { border: 1px solid #e0e0e0; border-radius: 4px; }")

        self.log_widget = QWidget()
        self.log_layout = QVBoxLayout(self.log_widget)
        self.log_layout.setContentsMargins(12, 12, 12, 12)
        self.log_layout.setSpacing(8)
        self.log_layout.addStretch()
        self.scroll_area.setWidget(self.log_widget)

        layout.addWidget(self.scroll_area)

    def add_log(self, message: str, is_error: bool = False):
        """添加日志"""
        label = CaptionLabel(message)
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        label.setText(f"[{timestamp}] {message}")

        if is_error:
            label.setStyleSheet("color: #D13438;")
        else:
            label.setStyleSheet("color: #333;")

        # 插入到 stretch 之前
        self.log_layout.insertWidget(self.log_layout.count() - 1, label)

        # 滚动到底部
        QTimer.singleShot(50, self._scroll_to_bottom)

        # 限制日志条数
        if self.log_layout.count() > 100:
            item = self.log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """清空日志"""
        while self.log_layout.count() > 1:
            item = self.log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class FileMonitorPage(QWidget):
    """文件监控页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.monitor = GeminiFileMonitor()
        self.settings = QSettings("GeminiWatermarkRemover", "FileMonitor")
        self.setup_ui()
        self._connect_signals()
        self._load_settings()  # 加载保存的配置

    def _connect_signals(self):
        """连接信号"""
        self.monitor.status.connect(self.on_status_update)
        self.monitor.file_processed.connect(self.on_file_processed)
        self.monitor.error.connect(self.on_error)
        self.monitor.monitoring_started.connect(self.on_monitoring_started)
        self.monitor.monitoring_stopped.connect(self.on_monitoring_stopped)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # 标题区域
        title = TitleLabel("实时文件监控")
        layout.addWidget(title)

        subtitle = CaptionLabel("自动监控目录中新下载的 Gemini 生成图片，实时移除水印")
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # 监控设置卡片
        self.setup_settings_card(layout)

        # 状态卡片
        self.setup_status_card(layout)

        # 日志卡片
        self.log_card = MonitorLogCard()
        layout.addWidget(self.log_card, 1)

    def setup_settings_card(self, layout):
        """设置监控设置卡片"""
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        # 标题
        title = StrongBodyLabel("监控设置")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        card_layout.addWidget(title)

        # 监控目录
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(12)

        dir_label = BodyLabel("监控目录")
        dir_label.setStyleSheet("color: #666;")
        dir_label.setMinimumWidth(80)
        dir_layout.addWidget(dir_label)

        self.dir_edit = LineEdit()
        self.dir_edit.setPlaceholderText("选择要监控的目录...")
        self.dir_edit.setReadOnly(True)
        dir_layout.addWidget(self.dir_edit, 1)

        self.browse_btn = PushButton("浏览")
        self.browse_btn.setMinimumWidth(80)
        self.browse_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.browse_btn)

        card_layout.addLayout(dir_layout)

        # 说明文字
        info_layout = QHBoxLayout()
        info_label = CaptionLabel(
            f"将自动处理文件名前缀为 '{FILE_PREFIX}' 的新图片，"
            f"原始文件将移动到 '{ARCHIVE_FOLDER_NAME}' 文件夹"
        )
        info_label.setStyleSheet("color: #999;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        card_layout.addLayout(info_layout)

        # 控制按钮
        control_layout = QHBoxLayout()
        control_layout.addStretch()

        self.switch_label = BodyLabel("监控状态")
        self.switch_label.setStyleSheet("color: #666;")
        control_layout.addWidget(self.switch_label)

        self.monitor_switch = SwitchButton()
        self.monitor_switch.checkedChanged.connect(self.on_switch_changed)
        control_layout.addWidget(self.monitor_switch)

        card_layout.addLayout(control_layout)

        layout.addWidget(card)

    def setup_status_card(self, layout):
        """设置状态卡片"""
        card = CardWidget()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(20)

        # 监控状态
        status_group = QVBoxLayout()
        status_group.setSpacing(4)

        status_label = BodyLabel("当前状态")
        status_label.setStyleSheet("color: #666;")
        status_group.addWidget(status_label)

        self.status_value = StrongBodyLabel("未启动")
        self.status_value.setStyleSheet("""
            StrongBodyLabel {
                color: #999;
                font-size: 18px;
                font-weight: 600;
            }
        """)
        status_group.addWidget(self.status_value)

        card_layout.addLayout(status_group)
        card_layout.addStretch()

        # 统计信息
        stats_group = QVBoxLayout()
        stats_group.setSpacing(4)

        stats_label = BodyLabel("已处理文件")
        stats_label.setStyleSheet("color: #666;")
        stats_group.addWidget(stats_label)

        self.processed_count = StrongBodyLabel("0")
        self.processed_count.setStyleSheet("""
            StrongBodyLabel {
                color: #0078D4;
                font-size: 24px;
                font-weight: 600;
            }
        """)
        stats_group.addWidget(self.processed_count)

        card_layout.addLayout(stats_group)

        layout.addWidget(card)

    def select_directory(self):
        """选择监控目录"""
        current_dir = self.dir_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择监控目录",
            current_dir
        )

        if directory:
            self.dir_edit.setText(directory)
            self._save_settings()

            # 如果正在监控，询问是否重启
            if self.monitor.is_running():
                InfoBar.info(
                    title="提示",
                    content="监控目录已更新，请重新启动监控以生效",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )

    def _load_settings(self):
        """加载配置"""
        last_dir = self.settings.value("last_directory", "", type=str)
        if last_dir and os.path.exists(last_dir):
            self.dir_edit.setText(last_dir)

    def _save_settings(self):
        """保存配置"""
        current_dir = self.dir_edit.text()
        if current_dir:
            self.settings.setValue("last_directory", current_dir)

    def on_switch_changed(self, checked: bool):
        """监控开关状态变化"""
        watch_dir = self.dir_edit.text()

        if not watch_dir:
            self.monitor_switch.setChecked(False)
            InfoBar.warning(
                title="提示",
                content="请先选择要监控的目录",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        if checked:
            # 开始监控
            if not os.path.exists(watch_dir):
                self.monitor_switch.setChecked(False)
                InfoBar.error(
                    title="错误",
                    content="所选目录不存在",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return

            self.processed_count.setText("0")
            self.log_card.clear_logs()
            self.monitor.start_monitoring(watch_dir)
        else:
            # 停止监控
            self.monitor.stop_monitoring()

    def on_status_update(self, message: str):
        """状态更新"""
        self.log_card.add_log(message)

    def on_file_processed(self, original_path: str, processed_path: str):
        """文件处理完成"""
        # 更新计数
        current = int(self.processed_count.text())
        self.processed_count.setText(str(current + 1))

        # 添加日志
        original_name = os.path.basename(original_path)
        processed_name = os.path.basename(processed_path)
        self.log_card.add_log(f"已处理: {original_name} -> {processed_name}")

    def on_error(self, error_msg: str):
        """错误处理"""
        self.log_card.add_log(f"错误: {error_msg}", is_error=True)

        InfoBar.error(
            title="错误",
            content=error_msg,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def on_monitoring_started(self, watch_dir: str):
        """监控已启动"""
        self.status_value.setText("监控中")
        self.status_value.setStyleSheet("""
            StrongBodyLabel {
                color: #107C10;
                font-size: 18px;
                font-weight: 600;
            }
        """)
        self.dir_edit.setEnabled(False)
        self.browse_btn.setEnabled(False)

        self.log_card.add_log(f"监控已启动: {watch_dir}")

        InfoBar.success(
            title="监控已启动",
            content=f"正在监控目录: {watch_dir}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    def on_monitoring_stopped(self):
        """监控已停止"""
        self.status_value.setText("未启动")
        self.status_value.setStyleSheet("""
            StrongBodyLabel {
                color: #999;
                font-size: 18px;
                font-weight: 600;
            }
        """)
        self.dir_edit.setEnabled(True)
        self.browse_btn.setEnabled(True)

        self.log_card.add_log("监控已停止")

        InfoBar.info(
            title="监控已停止",
            content="文件监控已停止",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )


# 导入 QTime
from PySide6.QtCore import QTime
