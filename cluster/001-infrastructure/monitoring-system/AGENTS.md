# monitoring-system/ — 监控与指标

## OVERVIEW
Prometheus/Grafana/Alertmanager 等（kube-prometheus-stack）与 metrics-server。

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| 目录索引 | `kustomization.yaml` | 当前 `vector` 可能被注释掉（需要时再启用） |
| 命名空间 | `namespace.yaml` | 带 `sync-https-wildcard-certificate` label |
| Prom/Grafana/Alertmanager | `kube-prometheus-stack/helm-release.yaml` | Grafana Ingress + 中间件（rfc1918）也在这里 |
| metrics-server | `metrics-server/helm-release.yaml` | 供 HPA/指标等 |

## CONVENTIONS
- Grafana admin 密码来自 `${SECRET_GRAFANA_ADMIN_PASSWORD}`（由 cluster-secrets 注入）。
