# 100-virtual-machine-base/ — 虚拟化基础

## OVERVIEW
KubeVirt + CDI + Multus 等虚拟化基础能力（operator/CRD/daemonset 级别清单，文件通常很大）。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 顶层索引 | `kustomization.yaml` |
| KubeVirt operator/CRD 清单 | `kubevirt/kubevirt-operator.yaml` |
| CDI operator/CRD 清单 | `kubevirt-cdi/cdi-operator.yaml` |
| Multus CNI | `multus-cni/` |

## ANTI-PATTERNS
- 这些大清单更像“vendor manifests”；改动前先确认来源与升级路径，避免手工 diff 维护成本爆炸。
