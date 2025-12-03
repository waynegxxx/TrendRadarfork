# coding=utf-8
"""自定义异常类"""


class TrendRadarException(Exception):
    """基础异常类"""
    pass


class ConfigError(TrendRadarException):
    """配置错误"""
    pass


class NetworkError(TrendRadarException):
    """网络请求错误"""
    pass


class NotificationError(TrendRadarException):
    """通知发送错误"""
    pass


class DataProcessingError(TrendRadarException):
    """数据处理错误"""
    pass


class ValidationError(TrendRadarException):
    """数据验证错误"""
    pass

