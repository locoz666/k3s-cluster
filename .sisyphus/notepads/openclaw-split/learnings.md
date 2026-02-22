## 2026-02-22

- Task 4 的 HelmRelease 需要沿用 `app-template` chart `4.3.0`（与 `dev-container` 一致）并保留 renovate 注释，避免后续版本跟踪断裂。
- OpenClaw 启动参数来自 `clawdbot` s6 run 脚本：`openclaw gateway --port 18789 --verbose --ws-log full --raw-stream --raw-stream-path /tmp/clawdbot/raw-stream.jsonl`。
- 健康检测端点使用根路径 `/`，并同时配置 liveness/readiness/startup 三种 HTTP 探针。
- `dev-share-files` 的 OpenClaw 挂载 `subPath` 必须与 `dev-container` 完全一致：`.openclaw`、`clawd`、`/tmp/clawdbot`、`clawd/skills`。

- 任务 5 采用独立的 `app/ingress.yaml`（B 方案）定义 `LoadBalancer` Service 与 Traefik Ingress：避免在 `openclaw` HelmRelease 中再改动现有 `app-template` `service` 配置。
