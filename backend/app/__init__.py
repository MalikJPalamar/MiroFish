"""
MiroFish Backend - Flask应用工厂
"""

import os
import time
import warnings
import psutil
from datetime import datetime, timezone

# 抑制 multiprocessing resource_tracker 的警告（来自第三方库如 transformers）
# 需要在所有其他导入之前设置
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, jsonify
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger
from .utils.metrics import MetricsMiddleware, metrics_endpoint


def create_app(config_class=Config):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置JSON编码：确保中文直接显示（而不是 \uXXXX 格式）
    # Flask >= 2.3 使用 app.json.ensure_ascii，旧版本使用 JSON_AS_ASCII 配置
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False
    
    # 设置日志
    logger = setup_logger('mirofish')
    
    # 只在 reloader 子进程中打印启动信息（避免 debug 模式下打印两次）
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process
    
    if should_log_startup:
        logger.info("=" * 50)
        logger.info("MiroFish Backend 启动中...")
        logger.info("=" * 50)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 初始化Prometheus指标中间件
    metrics = MetricsMiddleware(app)
    if should_log_startup:
        logger.info("已初始化Prometheus指标中间件")
    
    # 注册模拟进程清理函数（确保服务器关闭时终止所有模拟进程）
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("已注册模拟进程清理函数")
    
    # 请求日志中间件
    @app.before_request
    def log_request():
        logger = get_logger('mirofish.request')
        logger.debug(f"请求: {request.method} {request.path}")
        if request.content_type and 'json' in request.content_type:
            logger.debug(f"请求体: {request.get_json(silent=True)}")
    
    @app.after_request
    def log_response(response):
        logger = get_logger('mirofish.request')
        logger.debug(f"响应: {response.status_code}")
        return response
    
    # 注册蓝图
    from .api import graph_bp, simulation_bp, report_bp
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    
    # 健康检查端点
    @app.route('/health')
    def health():
        """
        健康检查端点
        
        返回服务健康状态和基本信息
        
        返回：
            {
                "status": "ok|degraded|unhealthy",
                "service": "MiroFish Backend",
                "timestamp": "2024-01-01T00:00:00Z",
                "uptime_seconds": 12345,
                "version": "1.0.0",
                "checks": {
                    "memory": "ok|warning|critical",
                    "cpu": "ok|warning|critical"
                }
            }
        """
        try:
            # 获取内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_status = 'ok'
            if memory_percent > 90:
                memory_status = 'critical'
            elif memory_percent > 75:
                memory_status = 'warning'
            
            # 获取CPU使用情况
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_status = 'ok'
            if cpu_percent > 90:
                cpu_status = 'critical'
            elif cpu_percent > 75:
                cpu_status = 'warning'
            
            # 获取进程信息
            process = psutil.Process(os.getpid())
            process_memory_mb = process.memory_info().rss / 1024 / 1024
            
            # 决定整体状态
            overall_status = 'ok'
            if memory_status == 'critical' or cpu_status == 'critical':
                overall_status = 'unhealthy'
            elif memory_status == 'warning' or cpu_status == 'warning':
                overall_status = 'degraded'
            
            return jsonify({
                "status": overall_status,
                "service": "MiroFish Backend",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0",
                "checks": {
                    "memory": memory_status,
                    "cpu": cpu_status
                },
                "details": {
                    "memory_percent": memory_percent,
                    "cpu_percent": cpu_percent,
                    "process_memory_mb": round(process_memory_mb, 2),
                    "process_threads": process.num_threads()
                }
            })
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "service": "MiroFish Backend",
                "error": str(e)
            }), 503
    
    # Prometheus指标端点
    @app.route('/metrics')
    def metrics_route():
        """
        Prometheus指标端点
        
        返回Prometheus格式的指标数据，供Prometheus服务器抓取
        
        包含指标：
            - mirofish_request_latency_seconds: 请求延迟分布
            - mirofish_requests_total: 请求总数（按方法、端点、状态码）
            - mirofish_active_simulations: 当前活跃模拟数
            - mirofish_errors_total: 错误总数
            - mirofish_simulation_events_total: 模拟事件总数
            - mirofish_requests_in_progress: 进行中的请求数
        """
        return metrics_endpoint()
    
    if should_log_startup:
        logger.info("MiroFish Backend 启动完成")
        logger.info("  - 健康检查: /health")
        logger.info("  - Prometheus指标: /metrics")
    
    return app
