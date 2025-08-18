# 任务收集与发布系统

一个智能的任务收集系统，自动从各种数据源采集信息，使用 AI 解析生成标准化任务，并发布到任务管理系统。

## 特性

- 🚀 **开箱即用** - 默认配置下无需外部依赖，一键启动
- 🔌 **可扩展** - 支持 RSS、网页、API 等多种数据源
- 🤖 **AI 驱动** - 集成多种 LLM（GPT、Claude、Gemini、Qwen 等）
- 📊 **可观测** - 内置 Prometheus 指标监控
- 🐳 **容器化** - 完整的 Docker 支持

## 快速开始

### 1. 环境准备

确保已安装 Docker 和 Docker Compose：

```bash
docker --version
docker compose version
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 根据需要编辑配置（可选）
vim .env
```

### 3. 启动服务

```bash
# 启动所有服务
docker compose up --build -d

# 查看日志
docker compose logs -f app
```

### 4. 验证运行

```bash
# 健康检查
curl http://localhost:8000/health

# 手动触发一次任务采集
curl -X POST http://localhost:8000/run-now

# 查看配置信息
curl http://localhost:8000/config
```

## 配置说明

### 核心配置（.env 文件）

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MOCK_PUBLISH` | 模拟发布模式 | `true` |
| `ENABLE_AI` | 启用 AI 生成 | `false` |
| `ENABLE_VALIDATION` | 启用链接验证 | `false` |
| `SCHEDULER_ENABLED` | 启用定时任务 | `false` |

### 数据源配置

编辑 `config/sources.yaml` 文件：

```yaml
sources:
  - id: hackernews
    type: rss
    name: Hacker News
    url: https://news.ycombinator.com/rss
    interval_seconds: 600
  
  - id: github_trending
    type: rss
    name: GitHub Trending
    url: https://github.com/trending/python.atom
    interval_seconds: 3600
```

### AI 模型配置

要启用 AI 功能，需要配置以下环境变量：

```bash
# 启用 AI
ENABLE_AI=true

# OpenAI GPT
MODEL_NAME=gpt-4o-mini
MODEL_API_KEY=your_openai_api_key

# Google Gemini
MODEL_NAME=gemini/gemini-1.5-flash
MODEL_API_KEY=your_gemini_api_key
MODEL_PROVIDER=gemini

# 其他模型（Claude、Qwen 等）
MODEL_NAME=anthropic/claude-3-haiku-20240307
MODEL_API_KEY=your_claude_api_key
```

## API 接口

### 基础接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/config` | 获取配置信息 |
| POST | `/run-now` | 手动触发任务采集 |
| GET | `/metrics` | Prometheus 监控指标 |

### 示例响应

**健康检查**
```json
{
  "status": "ok",
  "app": "TaskIngestService"
}
```

**手动触发**
```json
{
  "status": "done",
  "collected": 15,
  "generated": 12,
  "published": 8
}
```

## 部署指南

### 开发环境

```bash
# 启动开发环境
docker compose up --build

# 实时查看日志
docker compose logs -f app
```

### 生产环境

1. **配置环境变量**
```bash
# 启用真实发布
MOCK_PUBLISH=false
TASK_API_BASE_URL=https://your-task-system.com/api
TASK_API_TOKEN=your_api_token

# 启用定时任务
SCHEDULER_ENABLED=true

# 配置数据库
POSTGRES_DSN=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
```

2. **启用 HTTPS**
```bash
# 使用 Nginx 或 Traefik 反向代理
# 配置 SSL 证书
# 限制 /metrics 端点访问
```

3. **监控配置**
```bash
# 接入 Prometheus
# 配置 Grafana 仪表板
# 设置告警规则
```

## 任务管理系统对接

本服务作为任务生产者，需要对接外部任务管理系统。

### 发布任务接口

**POST** `/tasks`

```json
{
  "title": "任务标题",
  "description": "详细描述",
  "priority": "medium",
  "status": "not_started",
  "source": {
    "source_id": "hackernews",
    "source_url": "https://news.ycombinator.com/item?id=123",
    "external_source_id": "sha256_hash"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "meta": {
    "generator": "gpt-4o-mini"
  }
}
```

### 查询任务接口

**GET** `/tasks?external_source_id=hash`

用于避免重复发布相同任务。

## 监控指标

系统提供以下 Prometheus 指标：

- `ingest_collected_items{collector}` - 采集到的条目数
- `ingest_filtered_items{stage,reason}` - 过滤的条目数
- `ingest_published_tasks` - 发布的任务数
- `ingest_publish_failures{reason}` - 发布失败数

## 故障排除

### 常见问题

**Q: 启动失败？**
A: 检查 Docker 服务状态，确保端口 8000 未被占用

**Q: 无任务生成？**
A: 检查数据源配置，手动调用 `/run-now` 测试

**Q: AI 生成失败？**
A: 验证 API Key 配置，检查网络连接

**Q: 发布失败？**
A: 检查任务管理系统 API 配置和权限

### 调试命令

```bash
# 查看容器状态
docker compose ps

# 查看详细日志
docker compose logs app

# 进入容器调试
docker compose exec app bash

# 重启服务
docker compose restart app
```

## 开发指南

### 项目结构

```
├── app/                 # 应用程序代码
│   ├── main.py         # FastAPI 应用入口
│   ├── config.py       # 配置管理
│   ├── models.py       # 数据模型
│   ├── scheduler.py    # 定时任务
│   ├── collectors/     # 数据采集器
│   ├── ai/            # AI 生成模块
│   ├── filters/       # 内容过滤器
│   ├── validator/     # 内容验证器
│   └── publisher/     # 任务发布器
├── config/             # 配置文件
│   └── sources.yaml   # 数据源配置
├── docker-compose.yml  # Docker 编排
├── Dockerfile         # 容器构建
├── requirements.txt   # Python 依赖
└── .env.example      # 环境变量示例
```

### 扩展开发

**添加新的数据采集器**

1. 在 `app/collectors/` 创建新的采集器类
2. 继承 `BaseCollector` 基类
3. 实现 `collect()` 方法
4. 在配置文件中注册

**添加新的内容过滤器**

1. 在 `app/filters/` 创建过滤器类
2. 继承 `BaseFilter` 基类
3. 实现 `filter()` 方法

## 许可证

MIT License