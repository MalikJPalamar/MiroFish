"""
日志配置模块
提供统一的日志管理，同时输出到控制台和文件
支持结构化JSON日志格式，便于日志收集和分析
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


class StructuredLogFormatter(logging.Formatter):
    """
    结构化JSON日志格式化器
    将日志转换为JSON格式，便于日志收集系统（如ELK、Loki）解析
    """
    
    def __init__(self, include_extra=True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if self.include_extra and hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


def _ensure_utf8_stdout():
    """
    确保 stdout/stderr 使用 UTF-8 编码
    解决 Windows 控制台中文乱码问题
    """
    if sys.platform == 'win32':
        # Windows 下重新配置标准输出为 UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

# 是否启用JSON格式日志（用于生产环境）
USE_JSON_LOGGING = os.environ.get('USE_JSON_LOGGING', 'false').lower() == 'true'


def setup_logger(name: str = 'mirofish', level: int = logging.DEBUG, use_json: bool = None) -> logging.Logger:
    """
    设置日志器
    
    Args:
        name: 日志器名称
        level: 日志级别
        
    Returns:
        配置好的日志器
    """
    # 确保日志目录存在
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 阻止日志向上传播到根 logger，避免重复输出
    logger.propagate = False
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 日志格式
    # 决定是否使用JSON格式
    should_use_json = use_json if use_json is not None else USE_JSON_LOGGING
    
    if should_use_json:
        # JSON格式 - 用于生产环境和日志收集系统
        file_formatter = StructuredLogFormatter(include_extra=True)
        console_formatter = StructuredLogFormatter(include_extra=True)
    else:
        # 文本格式 - 用于开发环境
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
    
    # 1. 文件处理器 - 详细日志（按日期命名，带轮转）
    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_filename),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # 2. 控制台处理器 - 简洁日志（INFO及以上）
    # 确保 Windows 下使用 UTF-8 编码，避免中文乱码
    _ensure_utf8_stdout()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = 'mirofish') -> logging.Logger:
    """
    获取日志器（如果不存在则创建）
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# 创建默认日志器
logger = setup_logger()


# 便捷方法
def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)


def log_structured(level: int, msg: str, **kwargs):
    """
    结构化日志记录方法
    
    Args:
        level: 日志级别 (logging.DEBUG, logging.INFO, etc.)
        msg: 日志消息
        **kwargs: 额外的结构化字段
    
    Example:
        log_structured(logging.INFO, "用户登录成功", user_id="123", ip="192.168.1.1")
    """
    extra = kwargs.get('extra', {})
    extra['extra_fields'] = {k: v for k, v in kwargs.items() if k != 'extra'}
    logger.log(level, msg, extra=extra)

