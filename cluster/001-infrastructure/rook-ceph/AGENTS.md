# rook-ceph/ — Ceph 存储底座

## OVERVIEW
Rook-Ceph Operator + Ceph Cluster（含大量性能/稳定性 tuning、Dashboard、StorageClass）。

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| Operator 安装 | `helm-ceph-operator.yaml` | HelmRelease: `rook-ceph` |
| Cluster 配置/池/SC | `helm-ceph-cluster.yaml` | HelmRelease: `rook-ceph-cluster`；包含 `configOverride` 等 |
| Ceph 配置（带中文注释版本） | `ceph.conf` | `helm-ceph-cluster.yaml` 里提到避免 `configOverride` 写中文注释 |
| 危险运维（OSD 清理） | `scripts/osd-purge.yaml` | 会对磁盘/OSD 做清理动作，谨慎 |

## CONVENTIONS
- 该目录的 Helm values 内含大量“为什么这么配”的注释（比 README 更可信）。

## ANTI-PATTERNS
- 不要忽视 Helm values 内的 **WARNING**（某些开关只允许首次部署设置；错误变更可能导致数据损坏/集群被清空）。
