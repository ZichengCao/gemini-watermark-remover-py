#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数配置卡片组件
"""

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QWidget
from PySide6.QtCore import Signal, Qt
from qfluentwidgets import (
    CardWidget, BodyLabel, ComboBox, PushButton,
    Slider, StrongBodyLabel, LineEdit, SpinBox
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

        # 第一行：水印配置模式
        row1 = QHBoxLayout()
        row1.setSpacing(32)

        mode_group = QHBoxLayout()
        mode_group.setSpacing(12)
        mode_label = BodyLabel("水印配置")
        mode_label.setStyleSheet("color: #666;")
        mode_group.addWidget(mode_label)
        self.watermark_mode_combo = ComboBox()
        self.watermark_mode_combo.addItems(["大水印（默认）", "小水印", "自定义位置"])
        self.watermark_mode_combo.setFixedSize(150, 32)
        self.watermark_mode_combo.currentIndexChanged.connect(self.toggle_custom_watermark)
        mode_group.addWidget(self.watermark_mode_combo)
        row1.addLayout(mode_group)

        row1.addStretch()
        layout.addLayout(row1)

        # 第二行：自定义水印位置（初始隐藏）
        self.custom_watermark_row = QHBoxLayout()
        self.custom_watermark_row.setSpacing(32)

        # 水印尺寸
        size_group = QHBoxLayout()
        size_group.setSpacing(12)
        size_label = BodyLabel("水印尺寸")
        size_label.setStyleSheet("color: #666;")
        size_group.addWidget(size_label)
        self.logo_size_spin = SpinBox()
        self.logo_size_spin.setRange(16, 256)
        self.logo_size_spin.setValue(48)
        self.logo_size_spin.setSuffix(" px")
        self.logo_size_spin.setFixedSize(120, 32)
        size_group.addWidget(self.logo_size_spin)
        self.custom_watermark_row.addLayout(size_group)

        # 右边距
        margin_right_group = QHBoxLayout()
        margin_right_group.setSpacing(12)
        margin_right_label = BodyLabel("右边距")
        margin_right_label.setStyleSheet("color: #666;")
        margin_right_group.addWidget(margin_right_label)
        self.margin_right_spin = SpinBox()
        self.margin_right_spin.setRange(0, 200)
        self.margin_right_spin.setValue(32)
        self.margin_right_spin.setSuffix(" px")
        self.margin_right_spin.setFixedSize(120, 32)
        margin_right_group.addWidget(self.margin_right_spin)
        self.custom_watermark_row.addLayout(margin_right_group)

        # 下边距
        margin_bottom_group = QHBoxLayout()
        margin_bottom_group.setSpacing(12)
        margin_bottom_label = BodyLabel("下边距")
        margin_bottom_label.setStyleSheet("color: #666;")
        margin_bottom_group.addWidget(margin_bottom_label)
        self.margin_bottom_spin = SpinBox()
        self.margin_bottom_spin.setRange(0, 200)
        self.margin_bottom_spin.setValue(32)
        self.margin_bottom_spin.setSuffix(" px")
        self.margin_bottom_spin.setFixedSize(120, 32)
        margin_bottom_group.addWidget(self.margin_bottom_spin)
        self.custom_watermark_row.addLayout(margin_bottom_group)

        self.custom_watermark_row.addStretch()
        layout.addLayout(self.custom_watermark_row)

        # 初始隐藏自定义位置控件
        self.toggle_custom_watermark()

        # 第三行：说明文字
        row3 = QHBoxLayout()
        info_label = BodyLabel("自动移除 Gemini AI 生成图片右下角的水印")
        info_label.setStyleSheet("color: #666;")
        row3.addWidget(info_label)
        row3.addStretch()
        layout.addLayout(row3)

        # 第四行：输出格式
        row4 = QHBoxLayout()
        row4.setSpacing(32)

        format_group = QHBoxLayout()
        format_group.setSpacing(12)
        format_label = BodyLabel("输出格式")
        format_label.setStyleSheet("color: #666;")
        format_group.addWidget(format_label)
        self.format_combo = ComboBox()
        self.format_combo.addItems(["保持原格式", "JPEG", "PNG", "WEBP"])
        self.format_combo.setFixedSize(150, 32)
        format_group.addWidget(self.format_combo)
        row4.addLayout(format_group)

        row4.addStretch()
        layout.addLayout(row4)

        # 第五行：质量控制
        row5 = QHBoxLayout()
        row5.setSpacing(12)

        quality_label = BodyLabel("输出质量")
        quality_label.setStyleSheet("color: #666;")
        quality_label.setMinimumWidth(70)
        row5.addWidget(quality_label)

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

        row5.addLayout(quality_input_layout)
        layout.addLayout(row5)

        # 第六行：输出目录
        row6 = QHBoxLayout()
        row6.setSpacing(12)

        dir_label = BodyLabel("输出目录")
        dir_label.setStyleSheet("color: #666;")
        dir_label.setMinimumWidth(70)
        row6.addWidget(dir_label)

        self.dir_edit = LineEdit()
        self.dir_edit.setPlaceholderText("留空则保存到原图片目录")
        row6.addWidget(self.dir_edit, 1)

        self.dir_btn = PushButton("浏览")
        self.dir_btn.setFixedSize(80, 32)
        self.dir_btn.clicked.connect(self.select_output_dir)
        row6.addWidget(self.dir_btn)

        layout.addLayout(row6)

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_dir = directory
            self.dir_edit.setText(directory)

    def get_params(self):
        """获取参数配置"""
        format_text = self.format_combo.currentText()
        output_format = None if format_text == "保持原格式" else format_text

        # 获取水印配置模式
        watermark_mode = self.watermark_mode_combo.currentText()

        # 根据模式返回不同的配置
        if watermark_mode == "大水印（默认）":
            watermark_config = {
                'logo_size': 96,
                'margin_right': 64,
                'margin_bottom': 64
            }
        elif watermark_mode == "小水印":
            watermark_config = {
                'logo_size': 48,
                'margin_right': 32,
                'margin_bottom': 32
            }
        else:  # 自定义位置
            watermark_config = {
                'logo_size': self.logo_size_spin.value(),
                'margin_right': self.margin_right_spin.value(),
                'margin_bottom': self.margin_bottom_spin.value()
            }

        return {
            'watermark_config': watermark_config,
            'output_format': output_format,
            'quality': self.quality_slider.value(),
            'output_dir': self.output_dir
        }

    def toggle_custom_watermark(self):
        """切换自定义水印位置显示"""
        is_custom = self.watermark_mode_combo.currentText() == "自定义位置"
        # 隐藏/显示自定义水印位置组的所有控件
        for i in range(self.custom_watermark_row.count()):
            widget = self.custom_watermark_row.itemAt(i).widget()
            if widget:
                widget.setVisible(is_custom)
