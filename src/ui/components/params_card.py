#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数配置卡片组件
"""

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QWidget
from PySide6.QtCore import Signal, Qt
from qfluentwidgets import (
    CardWidget, BodyLabel, ComboBox, PushButton,
    Slider, StrongBodyLabel, LineEdit
)


class GeminiWatermarkParamsCard(CardWidget):
    """Gemini 水印移除参数配置卡片"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_dir = ""
        self.setStyleSheet("CardWidget { border-radius: 8px; }")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # 第一行：说明文字
        row1 = QHBoxLayout()
        info_label = BodyLabel("自动移除 Gemini AI 生成图片右下角的水印")
        info_label.setStyleSheet("color: #666;")
        row1.addWidget(info_label)
        row1.addStretch()
        layout.addLayout(row1)

        # 第二行：输出格式
        row2 = QHBoxLayout()
        row2.setSpacing(32)

        format_group = QHBoxLayout()
        format_group.setSpacing(12)
        format_label = BodyLabel("输出格式")
        format_label.setStyleSheet("color: #666;")
        format_group.addWidget(format_label)
        self.format_combo = ComboBox()
        self.format_combo.addItems(["保持原格式", "JPEG", "PNG", "WEBP"])
        self.format_combo.setMinimumWidth(150)
        format_group.addWidget(self.format_combo)
        row2.addLayout(format_group)

        row2.addStretch()
        layout.addLayout(row2)

        # 第三行：质量控制
        row3 = QHBoxLayout()
        row3.setSpacing(12)

        quality_label = BodyLabel("输出质量")
        quality_label.setStyleSheet("color: #666;")
        quality_label.setMinimumWidth(70)
        row3.addWidget(quality_label)

        quality_input_layout = QHBoxLayout()
        quality_input_layout.setSpacing(12)

        self.quality_slider = Slider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_slider.setMinimumWidth(250)
        quality_input_layout.addWidget(self.quality_slider)

        self.quality_value_label = StrongBodyLabel("95")
        self.quality_value_label.setStyleSheet("""
            StrongBodyLabel {
                color: #0078D4;
                font-size: 16px;
                font-weight: 600;
                min-width: 40px;
            }
        """)
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_value_label.setText(str(v))
        )
        quality_input_layout.addWidget(self.quality_value_label)
        quality_input_layout.addStretch(1)

        row3.addLayout(quality_input_layout)
        layout.addLayout(row3)

        # 第四行：输出目录
        row4 = QHBoxLayout()
        row4.setSpacing(12)

        dir_label = BodyLabel("输出目录")
        dir_label.setStyleSheet("color: #666;")
        dir_label.setMinimumWidth(70)
        row4.addWidget(dir_label)

        self.dir_edit = LineEdit()
        self.dir_edit.setPlaceholderText("留空则保存到原图片目录")
        row4.addWidget(self.dir_edit, 1)

        self.dir_btn = PushButton("浏览")
        self.dir_btn.setMinimumWidth(80)
        self.dir_btn.clicked.connect(self.select_output_dir)
        row4.addWidget(self.dir_btn)

        layout.addLayout(row4)

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_dir = directory
            self.dir_edit.setText(directory)

    def get_params(self):
        """获取参数配置"""
        format_text = self.format_combo.currentText()
        output_format = None if format_text == "保持原格式" else format_text

        return {
            'output_format': output_format,
            'quality': self.quality_slider.value(),
            'output_dir': self.output_dir
        }
