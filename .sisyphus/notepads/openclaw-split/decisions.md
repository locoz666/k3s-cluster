## 2026-02-22

- 在 `openclaw` HelmRelease 中继续使用 `registry-gitlab.${SECRET_DOMAIN}/loco/dev-container:latest`，以最小改动完成从 dev-container 服务拆分。
- Service 在 HelmRelease 中定义为 `main`/`gateway`（`18789`，`HTTP`），为后续 Ingress 绑定 openclaw gateway 提供稳定端口。

- `openclaw/app/ingress.yaml` 采用标准 `Ingress` + `Service` 的形式，保留现有 TLS secret `${SECRET_DOMAIN/./-}-tls` 与 `kube-system-rfc1918@kubernetescrd` 中间件，满足域名和安全策略要求，同时保持 `openclaw` 的拆分边界清晰。
