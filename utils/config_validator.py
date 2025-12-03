# coding=utf-8
"""配置验证模块"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from .exceptions import ConfigError, ValidationError
from .logger import logger


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_config_file(config_path: str) -> None:
        """
        验证配置文件是否存在
        
        Args:
            config_path: 配置文件路径
        
        Raises:
            ConfigError: 配置文件不存在时抛出
        """
        if not Path(config_path).exists():
            raise ConfigError(f"配置文件 {config_path} 不存在")
    
    @staticmethod
    def validate_required_keys(config: Dict[str, Any], required_keys: List[str]) -> None:
        """
        验证必需的配置键是否存在
        
        Args:
            config: 配置字典
            required_keys: 必需的键列表
        
        Raises:
            ConfigError: 缺少必需键时抛出
        """
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ConfigError(f"缺少必需的配置项: {', '.join(missing_keys)}")
    
    @staticmethod
    def validate_webhook_url(url: str, platform: str) -> bool:
        """
        验证 Webhook URL 格式
        
        Args:
            url: Webhook URL
            platform: 平台名称
        
        Returns:
            是否有效
        """
        if not url or not url.strip():
            return False
        
        url = url.strip()
        
        # 基本 URL 格式验证
        if not (url.startswith("http://") or url.startswith("https://")):
            logger.warning(f"{platform} Webhook URL 格式不正确: {url}")
            return False
        
        return True
    
    @staticmethod
    def validate_email_config(config: Dict[str, Any]) -> None:
        """
        验证邮件配置
        
        Args:
            config: 配置字典
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        email_from = config.get("EMAIL_FROM", "").strip()
        email_to = config.get("EMAIL_TO", "").strip()
        email_password = config.get("EMAIL_PASSWORD", "").strip()
        
        if email_from and email_to and email_password:
            # 验证邮箱格式
            if "@" not in email_from or "@" not in email_to:
                raise ValidationError("邮箱地址格式不正确")
        elif email_from or email_to or email_password:
            # 部分配置缺失
            raise ValidationError("邮件配置不完整，需要同时配置 EMAIL_FROM、EMAIL_TO 和 EMAIL_PASSWORD")
    
    @staticmethod
    def validate_telegram_config(config: Dict[str, Any]) -> None:
        """
        验证 Telegram 配置
        
        Args:
            config: 配置字典
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        bot_token = config.get("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = config.get("TELEGRAM_CHAT_ID", "").strip()
        
        if bot_token and not chat_id:
            raise ValidationError("Telegram 配置不完整，需要同时配置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
        if chat_id and not bot_token:
            raise ValidationError("Telegram 配置不完整，需要同时配置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
    
    @staticmethod
    def validate_push_window(config: Dict[str, Any]) -> None:
        """
        验证推送时间窗口配置
        
        Args:
            config: 配置字典
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        push_window = config.get("PUSH_WINDOW", {})
        if not push_window.get("ENABLED", False):
            return
        
        time_range = push_window.get("TIME_RANGE", {})
        start = time_range.get("START", "")
        end = time_range.get("END", "")
        
        if not start or not end:
            raise ValidationError("推送时间窗口配置不完整，需要同时配置 START 和 END")
        
        # 验证时间格式
        try:
            from datetime import datetime
            datetime.strptime(start, "%H:%M")
            datetime.strptime(end, "%H:%M")
        except ValueError:
            raise ValidationError("推送时间窗口格式不正确，应为 HH:MM 格式")
    
    @staticmethod
    def validate_platforms(platforms: List[Dict[str, Any]]) -> None:
        """
        验证平台配置
        
        Args:
            platforms: 平台列表
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        if not platforms:
            raise ValidationError("至少需要配置一个平台")
        
        platform_ids = []
        for platform in platforms:
            if "id" not in platform:
                raise ValidationError("平台配置缺少 'id' 字段")
            if "name" not in platform:
                raise ValidationError("平台配置缺少 'name' 字段")
            
            platform_id = platform["id"]
            if platform_id in platform_ids:
                raise ValidationError(f"平台 ID 重复: {platform_id}")
            platform_ids.append(platform_id)
    
    @staticmethod
    def validate_weight_config(weight_config: Dict[str, float]) -> None:
        """
        验证权重配置
        
        Args:
            weight_config: 权重配置字典
        
        Raises:
            ValidationError: 配置无效时抛出
        """
        rank_weight = weight_config.get("RANK_WEIGHT", 0)
        frequency_weight = weight_config.get("FREQUENCY_WEIGHT", 0)
        hotness_weight = weight_config.get("HOTNESS_WEIGHT", 0)
        
        total_weight = rank_weight + frequency_weight + hotness_weight
        
        # 允许一定的误差（浮点数精度问题）
        if abs(total_weight - 1.0) > 0.01:
            raise ValidationError(
                f"权重配置总和应为 1.0，当前为 {total_weight:.2f}"
            )
        
        # 验证权重范围
        for name, weight in [
            ("排名权重", rank_weight),
            ("频次权重", frequency_weight),
            ("热度权重", hotness_weight)
        ]:
            if weight < 0 or weight > 1:
                raise ValidationError(f"{name}应在 0-1 之间，当前为 {weight}")

