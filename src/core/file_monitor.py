#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监控模块

实时监控指定目录下新创建的 Gemini 生成图片，自动移除水印并归档原始文件
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QTimer

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
except ImportError:
    Observer = None
    FileSystemEventHandler = object
    FileCreatedEvent = None
    FileMovedEvent = None

from .gemini_watermark_remover import GeminiWatermarkRemover
from PIL import Image

logger = logging.getLogger('GeminiWatermarkRemover.file_monitor')

ARCHIVE_FOLDER_NAME = "Gemini Watermark Remover Archive"
FILE_PREFIX = "Gemini_Generated_Image"
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}


class GeminiFileHandler(FileSystemEventHandler):
    """Gemini 文件创建事件处理器"""

    def __init__(self, callback: Callable[[str], None], status_callback: Callable[[str], None] = None, delay_seconds: float = 2.0):
        super().__init__()
        self.callback = callback
        self.status_callback = status_callback
        self.delay_seconds = delay_seconds
        self.pending_files = {}
        self.mutex = QMutex()

    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return

        file_path = event.src_path
        path_obj = Path(file_path)

        # 调试：记录所有文件创建事件
        msg = f"创建文件: {path_obj.name}"
        logger.info(msg)
        if self.status_callback:
            self.status_callback(msg)

        # 检查文件扩展名
        if path_obj.suffix.lower() not in IMAGE_EXTENSIONS:
            return

        # 检查文件名前缀
        if not path_obj.name.startswith(FILE_PREFIX):
            return

        msg = f"✓ 匹配 Gemini 图片: {path_obj.name}"
        logger.info(msg)
        if self.status_callback:
            self.status_callback(msg)

        # 使用定时器延迟处理，确保文件写入完成
        import threading
        timer = threading.Timer(self.delay_seconds, self._process_file, args=[file_path])
        timer.start()

    def on_moved(self, event):
        """文件移动/重命名事件"""
        if event.is_directory:
            return

        # 检查目标路径（重命名后的路径）
        dest_path = event.dest_path
        path_obj = Path(dest_path)

        # 调试：记录所有文件移动事件
        msg = f"重命名: {Path(event.src_path).name} -> {path_obj.name}"
        logger.info(msg)
        if self.status_callback:
            self.status_callback(msg)

        # 检查文件扩展名
        if path_obj.suffix.lower() not in IMAGE_EXTENSIONS:
            return

        # 检查文件名前缀
        if not path_obj.name.startswith(FILE_PREFIX):
            return

        msg = f"✓ 匹配 Gemini 图片: {path_obj.name}"
        logger.info(msg)
        if self.status_callback:
            self.status_callback(msg)

        # 使用定时器延迟处理，确保文件操作完成
        import threading
        timer = threading.Timer(self.delay_seconds, self._process_file, args=[dest_path])
        timer.start()

    def _process_file(self, file_path: str):
        """处理文件（在延迟后调用）"""
        try:
            # 再次检查文件是否存在且大小大于0
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在，跳过: {file_path}")
                return

            if os.path.getsize(file_path) == 0:
                logger.warning(f"文件大小为0，跳过: {file_path}")
                return

            # 调用回调函数处理文件
            self.callback(file_path)

        except Exception as e:
            logger.error(f"处理文件时出错 {file_path}: {e}", exc_info=True)


class FileMonitorThread(QThread):
    """文件监控线程"""

    status = Signal(str)
    file_processed = Signal(str, str)  # 原始路径, 处理后路径
    error = Signal(str)
    monitoring_started = Signal(str)
    monitoring_stopped = Signal()

    def __init__(self, watch_dir: str, output_dir: Optional[str] = None):
        super().__init__()
        self.watch_dir = watch_dir
        self.output_dir = output_dir
        self.is_running = False
        self.observer = None
        self.mutex = QMutex()

        # 水印移除器
        self.remover = GeminiWatermarkRemover()
        self.remover.status.connect(self.status.emit)
        self.remover.error.connect(self.error.emit)

        # 创建归档目录
        self.archive_dir = Path(watch_dir) / ARCHIVE_FOLDER_NAME
        self.archive_dir.mkdir(exist_ok=True)

        # 处理队列（防止重复处理）
        self.processed_files = set()
        self.processing_mutex = QMutex()

    def _is_file_processed(self, file_path: str) -> bool:
        """检查文件是否已处理"""
        self.processing_mutex.lock()
        result = file_path in self.processed_files
        self.processing_mutex.unlock()
        return result

    def _mark_file_processed(self, file_path: str):
        """标记文件为已处理"""
        self.processing_mutex.lock()
        self.processed_files.add(file_path)
        self.processing_mutex.unlock()

    def _handle_new_file(self, file_path: str):
        """处理新发现的文件"""
        try:
            # 检查是否已处理
            if self._is_file_processed(file_path):
                logger.debug(f"文件已处理，跳过: {file_path}")
                return

            # 跳过已经处理过的文件（避免死循环）
            if '_no_watermark' in file_path:
                logger.debug(f"跳过已处理的文件: {file_path}")
                return

            self._mark_file_processed(file_path)

            # 获取文件信息
            file_path_obj = Path(file_path)
            filename = file_path_obj.name
            name_without_ext = file_path_obj.stem
            ext = file_path_obj.suffix

            self.status.emit(f"发现新文件: {filename}")

            # 去掉 Gemini_Generated_Image 前缀，避免死循环
            if name_without_ext.startswith(FILE_PREFIX):
                # 例如: Gemini_Generated_Image_1 -> 1
                name_without_ext = name_without_ext[len(FILE_PREFIX):].lstrip('_')

            # 确定输出路径（使用 PNG 格式以保持无损）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Clean_{name_without_ext}_{timestamp}.png"
            output_path = str(file_path_obj.parent / output_filename)

            # 移除水印
            self.status.emit(f"正在处理: {filename}")

            # 使用 remover 处理文件
            with Image.open(file_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 移除水印
                result_img = self.remover.remove_from_image(img)

                # 保存为 PNG（无损，质量最高）
                result_img.save(output_path, 'PNG', compress_level=0)

            self.status.emit(f"水印已移除: {output_filename}")

            # 移动原始文件到归档目录
            archive_path = self.archive_dir / filename
            counter = 1

            # 如果归档目录中已有同名文件，添加数字后缀
            while archive_path.exists():
                name_part = name_without_ext
                archive_path = self.archive_dir / f"{name_part}_{counter}{ext}"
                counter += 1

            # 移动文件
            shutil.move(file_path, str(archive_path))
            self.status.emit(f"原始文件已归档: {archive_path.name}")

            # 发送处理完成信号
            self.file_processed.emit(file_path, output_path)

        except Exception as e:
            logger.error(f"处理文件时出错 {file_path}: {e}", exc_info=True)
            self.error.emit(f"处理失败: {filename} - {str(e)}")

    def run(self):
        """运行监控线程"""
        if Observer is None:
            self.error.emit("未安装 watchdog 库，无法使用文件监控功能")
            return

        try:
            # 检查目录是否存在
            if not os.path.exists(self.watch_dir):
                self.error.emit(f"监控目录不存在: {self.watch_dir}")
                return

            # 创建事件处理器
            handler = GeminiFileHandler(
                callback=self._handle_new_file,
                status_callback=self.status.emit,
                delay_seconds=2.0
            )

            # 创建观察者
            self.observer = Observer()
            self.observer.schedule(handler, self.watch_dir, recursive=False)

            # 启动监控
            self.observer.start()
            self.is_running = True
            self.monitoring_started.emit(self.watch_dir)
            self.status.emit(f"开始监控目录: {self.watch_dir}")

            # 保持线程运行
            while self.is_running:
                self.msleep(100)

        except Exception as e:
            logger.error(f"监控线程错误: {e}", exc_info=True)
            self.error.emit(f"监控出错: {str(e)}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()

    def stop(self):
        """停止监控"""
        self.mutex.lock()
        self.is_running = False
        self.mutex.unlock()
        self.monitoring_stopped.emit()
        self.status.emit("监控已停止")


class GeminiFileMonitor(QObject):
    """Gemini 文件监控器（主控制器）"""

    status = Signal(str)
    file_processed = Signal(str, str)
    error = Signal(str)
    monitoring_started = Signal(str)
    monitoring_stopped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.monitor_thread: Optional[FileMonitorThread] = None
        self.is_monitoring = False

    def start_monitoring(self, watch_dir: str, output_dir: Optional[str] = None):
        """开始监控目录

        Args:
            watch_dir: 要监控的目录路径
            output_dir: 输出目录（留空则保存到原目录）
        """
        if self.is_monitoring:
            self.stop_monitoring()

        # 创建并启动监控线程
        self.monitor_thread = FileMonitorThread(watch_dir, output_dir)
        self.monitor_thread.status.connect(self.status.emit)
        self.monitor_thread.file_processed.connect(self.file_processed.emit)
        self.monitor_thread.error.connect(self.error.emit)
        self.monitor_thread.monitoring_started.connect(self.monitoring_started.emit)
        self.monitor_thread.monitoring_stopped.connect(self.monitoring_stopped.emit)

        self.monitor_thread.start()
        self.is_monitoring = True

    def stop_monitoring(self):
        """停止监控"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait(3000)  # 等待最多3秒
            self.is_monitoring = False

    def is_running(self) -> bool:
        """是否正在监控"""
        return self.is_monitoring and self.monitor_thread is not None
