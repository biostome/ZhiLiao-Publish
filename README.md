## 任务收集与发布系统 (Task Ingest Service)

持续从互联网采集信息，使用 LLM 解析生成标准化任务，经筛选与验证后发布到“任务管理系统”。采用 FastAPI + 可插拔采集器 + LiteLLM（支持 GPT/Claude/Gemini/Qwen…）。

---

### 你将获得什么
- 开箱即用：默认关闭 AI/验证，开启模拟发布，不依赖外部系统，一条命令即可跑通全链路。
- 可扩展：RSS/网页/API 采集、可替换 LLM、可接入你的“任务管理系统”。
- 可观测：内置 /metrics 指标，便于接入 Prometheus + Grafana。

---

## 一分钟上手（开箱即用）
1) 复制环境配置
```bash
cp .env.example .env
```
2) 一条命令启动（Docker 推荐）
```bash
docker compose up --build -d
```
3) 验证
```bash
# 健康检查
curl -s http://127.0.0.1:8000/health
# 运行一次采集-生成-发布（模拟发布，不会请求外部）
curl -X POST http://127.0.0.1:8000/run-now
```
默认行为：
- `MOCK_PUBLISH=true`，发布阶段只返回“发布成功”的模拟结果。
- `ENABLE_AI=false`，不调用大模型；使用安全后备生成。
- `ENABLE_VALIDATION=false`，不做外链校验。
- `SCHEDULER_ENABLED=false`，不开启定时任务（可手动 `/run-now`）。

---

## 部署指南（详细版）
### 环境要求
- Linux x86_64，2 核 CPU、4GB+ 内存
- Docker + Docker Compose 插件

验证：
```bash
docker -v
docker compose version
```

### 配置环境
- 复制并编辑 `.env`
  - 若保持“开箱即用”，可不改。
  - 若要真实发布，至少需要：`MOCK_PUBLISH=false`、设置 `TASK_API_BASE_URL` 与 `TASK_API_TOKEN`。

- 配置数据源 `config/sources.yaml`（已给示例）
```yaml
sources:
  - id: hn
    type: rss
    name: Hacker News
    url: https://news.ycombinator.com/rss
    interval_seconds: 600
```

### 启动与管理
```bash
# 启动
docker compose up --build -d
# 查看日志
docker compose logs -f app
# 重启
docker compose restart app
# 停止
docker compose down
```

### 开启定时任务（可选）
编辑 `.env`：
```
SCHEDULER_ENABLED=true
```
然后：
```bash
docker compose restart app
```

### 生产建议
- 置于 Nginx/Traefik 后，通过 HTTPS 暴露
- 限制 /metrics 只给监控系统访问
- 合理设置采集间隔与 User-Agent，避免过载目标站
- Postgres 定期备份；Redis 可开启持久化（可选）

---

## 配置说明（.env 关键项）
- 应用运行
  - `APP_NAME`：应用名称
  - `LOG_LEVEL`：日志级别（INFO/DEBUG…）
  - `SCHEDULER_ENABLED`：是否开启定时任务（默认 false）
  - `DATA_SOURCES_FILE`：数据源配置文件路径

- 去重与存储
  - `REDIS_URL`：Redis 连接串（用于去重；不可用时自动降级为“不去重”）
  - `POSTGRES_DSN`：Postgres DSN（如未连通，系统自动跳过初始化，不影响跑通）

- 发布（对接任务管理系统）
  - `MOCK_PUBLISH`：模拟发布（默认 true）
  - `TASK_API_BASE_URL`、`TASK_API_TOKEN`：真实发布所需

- AI 生成
  - `ENABLE_AI`：是否启用大模型（默认 false）
  - `MODEL_NAME`：模型名（示例：`gpt-4o-mini`、`gemini/gemini-1.5-flash`、`qwen/qwen2.5-7b-instruct` 等）
  - `MODEL_API_KEY`：模型 API Key
  - `MODEL_PROVIDER`：可选辅助（openai/anthropic/gemini 等）

- 校验
  - `ENABLE_VALIDATION`：是否访问源链接进行可达性校验

---

## 模型配置（含 Gemini 支持）
使用 LiteLLM 统一封装，支持 GPT/Claude/Gemini/Qwen/Mistral 等。

- 启用 Gemini（Google API）
```
ENABLE_AI=true
MODEL_NAME=gemini/gemini-1.5-flash
MODEL_API_KEY=你的_Gemini_API_Key
MODEL_PROVIDER=gemini
```
- 若使用 Vertex AI：
```
ENABLE_AI=true
MODEL_NAME=vertex_ai/gemini-1.5-pro
# 配置 GCP 凭据（例如）
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
```

提示：不想立即配置模型？保持 `ENABLE_AI=false` 即可，系统会用后备逻辑直接生成任务。

---

## 运行与监控
- 健康检查
```bash
curl -s http://127.0.0.1:8000/health
```
- 运行一次流水线
```bash
curl -X POST http://127.0.0.1:8000/run-now
```
- 配置快照（敏感信息已脱敏）
```bash
curl -s http://127.0.0.1:8000/config | jq .
```
- Prometheus 指标
```bash
curl -s http://127.0.0.1:8000/metrics | head
```

---

## 本服务 API 文档
- Base URL：`http://<host>:8000`
- 认证：默认无（生产建议加网关或网络层限制）

1) GET `/health`
- 返回：`{"status":"ok","app":"TaskIngestService"}`

2) GET `/config`
- 返回：当前配置（Key/Token 已脱敏）

3) POST `/run-now`
- 作用：触发一次采集→生成→筛选→验证→发布
- 返回：`{"status":"done"}`

4) GET `/metrics`
- Prometheus 指标：
  - `ingest_collected_items{collector}`
  - `ingest_filtered_items{stage,reason}`
  - `ingest_published_tasks`
  - `ingest_publish_failures{reason}`

---

## 对接“任务管理系统”协议（本服务调用外部）
- 认证：
  - Header：`Authorization: Bearer <TASK_API_TOKEN>`，`Content-Type: application/json`
  - 传输：HTTPS

- 端点：
  1) POST `/tasks`（发布新任务）
```json
{
  "title": "示例标题",
  "description": "任务详细描述……",
  "priority": "medium",
  "status": "not_started",
  "source": {
    "source_id": "hn",
    "source_url": "https://example.com/item/123",
    "external_source_id": "sha256hash123..."
  },
  "created_at": "2025-01-01T12:00:00Z",
  "meta": {"generator": "gpt-4o-mini"}
}
```
响应（建议任一兼容）：
```json
{"id": "12345"}
```
或：
```json
{"task_id": "12345"}
```
或：
```json
{"data": {"id": "12345"}}
```

  2) GET `/tasks`（根据 `external_source_id` 查询，避免重复）
- 查询参数：`external_source_id=<值>`
- 响应（建议）：
```json
{"items": [{"id": "12345", "external_source_id": "sha256hash123..."}]}
```

  3) PATCH `/tasks/{id}`（更新任务）
```json
{"title": "新标题","description": "新描述","priority": "high","status": "in_progress"}
```

- 字段约定（建议）：
  - `title`：1-200 字；`description`：<=2000 字
  - `priority`：low|medium|high（默认 medium）
  - `status`：not_started|in_progress|done|blocked（默认 not_started）
  - `source.source_id`：数据源 ID；`source.source_url`：原文链接
  - `source.external_source_id`：来源幂等键（本服务用 source_id+URL 计算 sha256）
  - `created_at`：ISO8601
  - `meta`：扩展信息

- 幂等与去重：建议任务系统对 `external_source_id` 建立唯一约束，并支持查询参数。

---

## FAQ
- 一直无任务？
  - 先手动调用 `/run-now`；检查 `config/sources.yaml` 是否可访问；看 `/metrics` 的过滤原因。
- 发布 401/403？
  - 检查 `TASK_API_TOKEN` 与权限；未对接前可先用 `MOCK_PUBLISH=true` 验链路。
- 要用 AI？
  - `ENABLE_AI=true` + 设置 `MODEL_API_KEY` + 按需选择 `MODEL_NAME`（支持 Gemini，见上）。
- 校验失败？
  - 若源站不稳定，可先 `ENABLE_VALIDATION=false`。

---

## 许可
MIT