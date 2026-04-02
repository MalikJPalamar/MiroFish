# API Rate Limiting

MiroFish Backend使用Flask-Limiter实现API速率限制，保护服务免受滥用和过度负载。

## 概述

Rate Limiting通过限制客户端在特定时间窗口内的请求数量来保护API服务。这有助于：
- 防止DDoS攻击和恶意爬虫
- 确保公平使用，避免个别用户占用过多资源
- 保护昂贵的API调用（如LLM调用）

## 配置

### 存储后端

- **开发环境**: 内存存储 (`memory://`)
- **生产环境**: 建议使用Redis (`redis://localhost:6379`)

### 速率限制

| 端点类型 | 限制 | 说明 |
|---------|------|------|
| 默认API | 100/minute | 大多数API端点 |
| 创建模拟 | 10/minute | `POST /api/simulation/create` |
| 准备模拟 | 5/minute | `POST /api/simulation/prepare` - LLM生成配置和人设 |
| 运行模拟 | 5/minute | `POST /api/simulation/start` |
| 生成人设 | 10/minute | `POST /api/simulation/generate-profiles` |
| 采访Agent | 30/minute | `POST /api/simulation/interview` |
| 批量采访 | 10/minute | `POST /api/simulation/interview/batch` |
| 全局采访 | 5/minute | `POST /api/simulation/interview/all` |
| 环境操作 | 30/minute | `POST /api/simulation/env-status`, `/close-env` |
| 健康检查 | 无限制 | `GET /health` |

## 响应头

启用Rate Limiting后，响应会包含以下headers：

| Header | 说明 |
|--------|------|
| `X-RateLimit-Limit` | 当前时间窗口内的最大请求数 |
| `X-RateLimit-Remaining` | 剩余可用请求数 |
| `X-RateLimit-Reset` | 时间窗口重置时间戳 |
| `Retry-After` | 当触发限制时，返回需要等待的秒数 |

## 限流响应

当请求超过限制时，API返回HTTP 429状态码：

```json
{
  "success": false,
  "error": "请求过于频繁，请稍后再试",
  "retry_after": "60"
}
```

## 生产环境配置

### 使用Redis

1. 安装Redis:
```bash
apt install redis-server
pip install flask-limiter[redis]
```

2. 修改应用配置:
```python
# app/ratelimit.py
limiter = Limiter(
    key_func=get_remote_address,
    app=None,
    default_limits=["100 per minute"],
    storage_uri="redis://localhost:6379",  # 生产环境使用Redis
    strategy="fixed-window",
)
```

### 环境变量

可以通过环境变量配置限制：
```bash
export RATELIMIT_DEFAULT="200 per minute"
export RATELIMIT_STORAGE_URI="redis://redis-host:6379"
```

## 注意事项

1. **限流基于IP**: 默认使用客户端IP地址作为限流键
2. **全局限制**: 100/minute是全局限制，适用于所有未单独配置的端点
3. **昂贵操作**: LLM相关操作（prepare, generate-profiles等）有更严格的限制
4. **幂等性**: GET请求通常不受限制（查看操作）

## 文件结构

```
backend/
├── app/
│   ├── __init__.py      # 应用工厂，初始化Limiter
│   ├── ratelimit.py     # Rate Limiting配置和常量
│   └── api/
│       └── simulation.py # 仿真端点，使用特定限流
└── docs/
    └── RATE_LIMITING.md  # 本文档
```
