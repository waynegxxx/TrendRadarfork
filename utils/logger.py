# coding=utf-8
"""日志模块 - 提供统一的日志记录功能"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """日志管理器"""
    
    def __init__(
        self,
        name: str = "TrendRadar",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        format_string: Optional[str] = None
    ):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别
            log_file: 日志文件路径（可选）
            format_string: 日志格式字符串（可选）
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 默认格式
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(message)s'
            )
        
        formatter = logging.Formatter(format_string)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定）
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info=True, **kwargs):
        """记录异常信息"""
        self.logger.error(message, *args, exc_info=exc_info, **kwargs)


# 创建默认日志器实例
logger = Logger()

