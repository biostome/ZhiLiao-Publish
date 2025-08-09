# ZhiLiao-Publish

一个用于“任务收集与发布”的仓库，当前包含服务：`task_ingest_service`（FastAPI）。该服务从互联网采集信息，使用 LLM 解析生成标准化任务，经筛选与验证后（可选）发布到你的“任务管理系统”。

---

## 目录结构
```
.
├─ task_ingest_service/        # 任务收集与发布服务（FastAPI + Docker Compose）
│  ├─ app/                     # 应用源码
│  ├─ config/                  # 配置（如数据源 sources.yaml）
│  ├─ Dockerfile
│  ├─ docker-compose.yml
│  ├─ requirements.txt
│  └─ README.md                # 服务的详细文档（强烈推荐阅读）
└─ README.md                   # 当前文件
```

---

## 快速开始（推荐使用 Docker）
前置要求：已安装 Docker 与 Docker Compose 插件。

1) 进入服务目录并创建环境文件（本仓库未提供 `.env.example`，可新建空文件或按需填写）
```bash
cd task_ingest_service
# 最简：创建一个空的 .env（可先不配置任何变量）
: > .env

# 如果你想立即可见行为，可填入一份示例（可选）
cat > .env <<'EOF'
APP_NAME=TaskIngestService
LOG_LEVEL=INFO
SCHEDULER_ENABLED=false
MOCK_PUBLISH=true
ENABLE_AI=false
ENABLE_VALIDATION=false
DATA_SOURCES_FILE=config/sources.yaml
# 若要真实发布，请设置：
# TASK_API_BASE_URL=https://your-task-system.example.com
# TASK_API_TOKEN=xxxx
EOF
```

2) 构建并启动
```bash
docker compose up --build -d
```

3) 验证服务
```bash
# 健康检查
curl -s http://127.0.0.1:8000/health
# 运行一次采集-生成-发布（默认模拟发布）
curl -X POST http://127.0.0.1:8000/run-now
```

默认行为（开箱即用）：
- `MOCK_PUBLISH=true`：发布阶段只返回“发布成功”的模拟结果
- `ENABLE_AI=false`：不调用大模型，由后备逻辑生成
- `ENABLE_VALIDATION=false`：不做外链可达性校验
- `SCHEDULER_ENABLED=false`：不开启定时任务（可手动调用 `/run-now`）

端口映射：
- 应用：`127.0.0.1:8000`
- Redis：`127.0.0.1:6379`
- Postgres：`127.0.0.1:5432`

---

## 常见配置场景
- 开启定时任务：将 `.env` 中 `SCHEDULER_ENABLED=true`，然后 `docker compose restart app`
- 对接真实任务系统发布：设置 `MOCK_PUBLISH=false`、`TASK_API_BASE_URL`、`TASK_API_TOKEN`
- 配置数据源：编辑 `task_ingest_service/config/sources.yaml`
- 监控指标：访问 `GET /metrics`（建议在生产仅对监控系统开放）

更多可配置项（如 AI 模型、校验、去重/存储等）请参考下方文档链接。

---

## 本地开发（不使用 Docker，可选）
在 `task_ingest_service` 目录下：
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# 亦可创建一个 .env（与上方示例一致）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 文档与链接
- 服务详细说明、API、配置项与 FAQ：请阅读 `task_ingest_service/README.md`
- 关键文件：`task_ingest_service/Dockerfile`、`task_ingest_service/docker-compose.yml`、`task_ingest_service/config/sources.yaml`

---

## 许可
MIT
