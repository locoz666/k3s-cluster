# cluster/001-infrastructure/ — 核心基础设施

## OVERVIEW
集群基础设施层：证书、存储、监控、Elastic、GPU 等。该层在 Flux 编排中通常 **prune=false**（避免误删关键资源）。

## STRUCTURE
```text
001-infrastructure/
├── cert-manager/
├── rook-ceph/
├── juicefs/
├── monitoring-system/
├── elastic-system/
├── gpu-operator/
└── kustomization.yaml
```

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| cert-manager 安装参数 | `cert-manager/helm-release.yaml` |
| Ceph Operator/Cluster | `rook-ceph/helm-ceph-operator.yaml` + `rook-ceph/helm-ceph-cluster.yaml` |
| JuiceFS 元数据与 Ceph pools | `juicefs/`（`kustomization.yaml` + `ceph-*-pool.yaml`） |
| 监控（Prom/Grafana） | `monitoring-system/kube-prometheus-stack/helm-release.yaml` |
| Elastic (ECK/ES/Kibana) | `elastic-system/` |
| GPU Operator | `gpu-operator/` |

## ANTI-PATTERNS
- 存储相关（Ceph/JuiceFS）变更前先确认：StorageClass/PVC/池参数一旦上线，回滚成本高。
