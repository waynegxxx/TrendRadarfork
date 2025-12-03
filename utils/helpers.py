# coding=utf-8
"""辅助函数模块"""

import re
import html
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz


def get_beijing_time() -> datetime:
    """
    获取北京时间
    
    Returns:
        当前北京时间
    """
    beijing_tz = pytz.timezone("Asia/Shanghai")
    return datetime.now(beijing_tz)


def format_date_folder(date: Optional[datetime] = None) -> str:
    """
    格式化日期文件夹名称
    
    Args:
        date: 日期对象，默认为当前时间
    
    Returns:
        格式化的日期字符串，例如：2025年11月01日
    """
    if date is None:
        date = get_beijing_time()
    return date.strftime("%Y年%m月%d日")


def format_time_filename(date: Optional[datetime] = None) -> str:
    """
    格式化时间文件名
    
    Args:
        date: 日期对象，默认为当前时间
    
    Returns:
        格式化的时间字符串，例如：00时30分
    """
    if date is None:
        date = get_beijing_time()
    return date.strftime("%H时%M分")


def clean_title(title: str) -> str:
    """
    清理标题中的特殊字符
    
    Args:
        title: 原始标题
    
    Returns:
        清理后的标题
    """
    if not title:
        return ""
    
    # 移除多余的空白字符
    title = re.sub(r'\s+', ' ', title).strip()
    
    # 移除控制字符
    title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)
    
    return title


def html_escape(text: str) -> str:
    """
    HTML 转义
    
    Args:
        text: 原始文本
    
    Returns:
        转义后的文本
    """
    if not text:
        return ""
    return html.escape(str(text))


def ensure_directory_exists(directory: str) -> None:
    """
    确保目录存在
    
    Args:
        directory: 目录路径
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_output_path(subfolder: str, filename: str) -> str:
    """
    获取输出文件路径
    
    Args:
        subfolder: 子文件夹名称
        filename: 文件名
    
    Returns:
        完整的文件路径
    """
    output_dir = Path("output") / subfolder
    ensure_directory_exists(str(output_dir))
    return str(output_dir / filename)


def is_valid_url(url: str) -> bool:
    """
    验证 URL 格式
    
    Args:
        url: URL 字符串
    
    Returns:
        是否有效
    """
    if not url or not url.strip():
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url.strip()))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
    
    Returns:
        截断后的文本
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_int(value: any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 要转换的值
        default: 默认值
    
    Returns:
        整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 默认值
    
    Returns:
        浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

