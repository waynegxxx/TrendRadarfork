# coding=utf-8
"""
使用新工具模块的示例

展示如何在代码中使用新创建的日志、异常、重试等模块
"""

import os
from typing import Dict, Any

# 导入新创建的模块
from utils.logger import logger
from utils.exceptions import ConfigError, NetworkError, NotificationError
from utils.retry import retry_on_network_error
from utils.config_validator import ConfigValidator
from utils.helpers import get_beijing_time, format_date_folder, clean_title

import requests


# ===== 示例 1: 使用日志模块 =====

def example_logging():
    """日志使用示例"""
    logger.info("程序开始运行")
    logger.debug("这是调试信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    try:
        raise ValueError("示例错误")
    except Exception as e:
        logger.exception("捕获到异常", exc_info=True)


# ===== 示例 2: 使用重试装饰器 =====

@retry_on_network_error(max_attempts=3, delay=1.0)
def fetch_data_with_retry(url: str) -> Dict[str, Any]:
    """
    带重试的数据获取函数
    
    Args:
        url: 请求 URL
    
    Returns:
        响应数据
    
    Raises:
        NetworkError: 网络错误时抛出
    """
    logger.info(f"正在获取数据: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


# ===== 示例 3: 使用配置验证 =====

def example_config_validation(config: Dict[str, Any]):
    """配置验证示例"""
    validator = ConfigValidator()
    
    try:
        # 验证配置文件存在
        validator.validate_config_file("config/config.yaml")
        
        # 验证必需的配置项
        validator.validate_required_keys(config, ["REPORT_MODE", "PLATFORMS"])
        
        # 验证 Webhook URL
        feishu_url = config.get("FEISHU_WEBHOOK_URL", "")
        if feishu_url:
            if not validator.validate_webhook_url(feishu_url, "飞书"):
                logger.warning("飞书 Webhook URL 格式不正确")
        
        # 验证邮件配置
        validator.validate_email_config(config)
        
        # 验证 Telegram 配置
        validator.validate_telegram_config(config)
        
        # 验证推送时间窗口
        validator.validate_push_window(config)
        
        # 验证平台配置
        validator.validate_platforms(config.get("PLATFORMS", []))
        
        # 验证权重配置
        validator.validate_weight_config(config.get("WEIGHT_CONFIG", {}))
        
        logger.info("配置验证通过")
        
    except ConfigError as e:
        logger.error(f"配置错误: {e}")
        raise
    except Exception as e:
        logger.error(f"验证过程出错: {e}")
        raise


# ===== 示例 4: 使用辅助函数 =====

def example_helpers():
    """辅助函数使用示例"""
    # 获取北京时间
    beijing_time = get_beijing_time()
    logger.info(f"当前北京时间: {beijing_time}")
    
    # 格式化日期文件夹
    date_folder = format_date_folder()
    logger.info(f"日期文件夹: {date_folder}")
    
    # 清理标题
    dirty_title = "  这是一个\n\t测试标题  "
    clean = clean_title(dirty_title)
    logger.info(f"清理前: {dirty_title}")
    logger.info(f"清理后: {clean}")


# ===== 示例 5: 使用自定义异常 =====

def example_exceptions():
    """异常处理示例"""
    try:
        # 模拟配置错误
        if not os.path.exists("config/config.yaml"):
            raise ConfigError("配置文件不存在")
        
        # 模拟网络错误
        try:
            response = requests.get("https://invalid-url.example.com", timeout=1)
        except requests.RequestException as e:
            raise NetworkError(f"网络请求失败: {e}") from e
        
        # 模拟通知错误
        webhook_url = ""
        if not webhook_url:
            raise NotificationError("Webhook URL 未配置")
            
    except ConfigError as e:
        logger.error(f"配置错误: {e}")
        # 处理配置错误
    except NetworkError as e:
        logger.error(f"网络错误: {e}")
        # 处理网络错误，可以重试
    except NotificationError as e:
        logger.error(f"通知错误: {e}")
        # 处理通知错误，可以降级处理
    except Exception as e:
        logger.exception("未知错误", exc_info=True)


# ===== 示例 6: 综合使用 =====

class ExampleService:
    """示例服务类，展示如何综合使用各个模块"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化服务
        
        Args:
            config: 配置字典
        
        Raises:
            ConfigError: 配置错误时抛出
        """
        self.config = config
        
        # 验证配置
        validator = ConfigValidator()
        validator.validate_config_file("config/config.yaml")
        validator.validate_required_keys(config, ["REPORT_MODE"])
        
        logger.info("服务初始化成功")
    
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_platform_data(self, platform_id: str) -> Dict[str, Any]:
        """
        获取平台数据
        
        Args:
            platform_id: 平台 ID
        
        Returns:
            平台数据
        
        Raises:
            NetworkError: 网络错误时抛出
        """
        logger.info(f"正在获取平台数据: {platform_id}")
        
        try:
            # 模拟 API 请求
            url = f"https://api.example.com/{platform_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"成功获取平台数据: {platform_id}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"获取平台数据失败: {platform_id}, 错误: {e}")
            raise NetworkError(f"网络请求失败: {platform_id}") from e
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理数据
        
        Args:
            data: 原始数据
        
        Returns:
            处理后的数据
        """
        logger.debug("开始处理数据")
        
        # 使用辅助函数清理数据
        if "title" in data:
            data["title"] = clean_title(data["title"])
        
        logger.info("数据处理完成")
        return data
    
    def send_notification(self, message: str) -> bool:
        """
        发送通知
        
        Args:
            message: 消息内容
        
        Returns:
            是否发送成功
        
        Raises:
            NotificationError: 通知发送失败时抛出
        """
        webhook_url = self.config.get("FEISHU_WEBHOOK_URL", "")
        
        if not webhook_url:
            raise NotificationError("Webhook URL 未配置")
        
        try:
            logger.info("正在发送通知")
            response = requests.post(webhook_url, json={"text": message}, timeout=10)
            response.raise_for_status()
            
            logger.info("通知发送成功")
            return True
            
        except requests.RequestException as e:
            logger.error(f"通知发送失败: {e}")
            raise NotificationError(f"通知发送失败: {e}") from e


# ===== 主函数 =====

def main():
    """主函数，运行所有示例"""
    logger.info("=" * 50)
    logger.info("开始运行示例")
    logger.info("=" * 50)
    
    # 示例 1: 日志
    logger.info("\n--- 示例 1: 日志使用 ---")
    example_logging()
    
    # 示例 2: 重试
    logger.info("\n--- 示例 2: 重试装饰器 ---")
    try:
        # 注意：这个 URL 可能不存在，会触发重试
        # data = fetch_data_with_retry("https://httpbin.org/json")
        # logger.info(f"获取的数据: {data}")
        logger.info("重试装饰器示例（跳过实际请求）")
    except Exception as e:
        logger.error(f"重试失败: {e}")
    
    # 示例 3: 配置验证
    logger.info("\n--- 示例 3: 配置验证 ---")
    example_config = {
        "REPORT_MODE": "daily",
        "PLATFORMS": [
            {"id": "weibo", "name": "微博"}
        ],
        "WEIGHT_CONFIG": {
            "RANK_WEIGHT": 0.6,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.1
        }
    }
    try:
        example_config_validation(example_config)
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
    
    # 示例 4: 辅助函数
    logger.info("\n--- 示例 4: 辅助函数 ---")
    example_helpers()
    
    # 示例 5: 异常处理
    logger.info("\n--- 示例 5: 异常处理 ---")
    example_exceptions()
    
    # 示例 6: 综合使用
    logger.info("\n--- 示例 6: 综合使用 ---")
    try:
        service = ExampleService(example_config)
        logger.info("服务创建成功")
    except Exception as e:
        logger.error(f"服务创建失败: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info("示例运行完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()

