## 任务收集与发布系统 (Task Ingest Service)

FastAPI 驱动的“任务收集与发布系统”。持续从互联网采集信息，使用 LLM 生成标准化任务，过滤/验证后通过“任务管理系统 API”进行发布。

### 特性
- 多数据源采集（RSS、网页等，可扩展）
- LLM 解析与任务生成（LiteLLM 封装，支持多模型）
- 去重、规则过滤、有效性验证
- 通过 RESTful API 发布至任务管理系统
- 定时调度，Prometheus 指标，Docker 部署

### 运行
1. 复制环境配置
```
cp .env.example .env
```
2. 修改 `.env` 中的 `TASK_API_BASE_URL`、`TASK_API_TOKEN`、`MODEL_API_KEY` 等。
3. 启动（最省心：一条命令）
```
docker compose up --build -d
```
- 开箱即用：已默认关闭 AI/验证、开启模拟发布（不会请求外部任务系统）
- 服务暴露在 `http://localhost:8000`
- 想要真实发布：在 `.env` 里设置 `MOCK_PUBLISH=false`，补齐 `TASK_API_BASE_URL` 和 `TASK_API_TOKEN`

### 重要端点
- GET `/health` 健康检查
- POST `/run-now` 立即执行一次采集与发布流水线
- GET `/config` 当前配置快照（敏感字段已过滤）
- GET `/metrics` Prometheus 指标

### 配置数据源
编辑 `config/sources.yaml`，示例：
```yaml
sources:
  - id: cn_ycombinator
    type: rss
    name: Y Combinator Hacker News
    url: https://news.ycombinator.com/rss
    interval_seconds: 600
  - id: cn_gov_example
    type: rss
    name: 中国政府网示例
    url: https://www.gov.cn/rss/bm/zwb.htm
    interval_seconds: 1800
```

### 环境变量（节选）
详见 `.env.example`。
- `TASK_API_BASE_URL`, `TASK_API_TOKEN`：任务管理系统 API
- `MODEL_NAME`, `MODEL_API_KEY`：LLM 模型
- `REDIS_URL`：去重缓存
- `POSTGRES_DSN`：PostgreSQL 持久化

### 发布字段（到任务管理系统）
- 标题、描述、优先级、状态（默认未开始）
- 来源信息（URL / source_id / external_source_id）
- 时间戳

### 开发
```
uvicorn app.main:app --reload
```

### 许可
MIT