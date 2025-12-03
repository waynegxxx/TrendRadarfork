# coding=utf-8
"""重试装饰器模块"""

import time
import functools
from typing import Callable, TypeVar, Tuple, Optional, List

from .logger import logger

T = TypeVar('T')


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Exception, ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数
    
    Returns:
        装饰后的函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败"
                        )
                        raise
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt} 次尝试失败: {e}，"
                        f"{current_delay:.2f} 秒后重试..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # 理论上不会到达这里
            if last_exception:
                raise last_exception
            
            raise RuntimeError("重试逻辑异常")
        
        return wrapper
    return decorator


def retry_on_network_error(
    max_attempts: int = 3,
    delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    网络错误重试装饰器（专门用于网络请求）
    
    Args:
        max_attempts: 最大尝试次数
        delay: 延迟时间（秒）
    
    Returns:
        装饰后的函数
    """
    import requests
    
    return retry(
        max_attempts=max_attempts,
        delay=delay,
        exceptions=(requests.RequestException, ConnectionError, TimeoutError)
    )

