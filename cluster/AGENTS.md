# cluster/ — GitOps 主目录

## OVERVIEW
本目录是集群“源代码”：Flux 以此为准对集群持续 reconcile（分层目录 + Flux Kustomization CR 编排）。

## STRUCTURE
```text
cluster/
├── 000-base/                 # Flux 入口 + repos + namespaces + cluster-secrets + 分层 Kustomization CR
├── 001-infrastructure/       # 核心基础设施（存储/监控/证书/ELK/GPU 等）
├── 002-infrastructure-extra/ # 额外基础设施（如 Issuer/证书、JuiceFS CSI 等）
├── apps/                     # 应用（按 namespace 分组；default/kube-system/...）
├── 100-virtual-machine-base/ # KubeVirt 基础（operator/CRD 等）
├── 101-virtual-machine-base-extra/
├── 102-virtual-machine/      # 具体 VM（ISO、VM YAML、PVC 等）
└── 240-smart-home/           # 智能家居（home-assistant / node-red 等）
```

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| “分层编排”的事实来源 | `000-base/kustomization.yaml` | 这是 kustomize 的 resources 列表（包含 repos/flux-system/secrets/各层 ks） |
| Flux Kustomization CR（层级） | `000-base/{001,002,100,101,102,240}.yaml` + `000-base/apps.yaml` | 每个文件一个 `Kustomization` CR，配置 `dependsOn/path/prune` |
| 应用是否启用 | `apps/<ns>/kustomization.yaml` | 通过 include 某个 app 的 `ks.yaml`（通常可注释掉） |
| 单应用编排 | `apps/**/<app>/ks.yaml` | 常见：postgres/redis/app 多段 Kustomization + `dependsOn` 链 |

## CONVENTIONS
- 分层目录名以数字前缀保证“阅读顺序”，**真正的执行顺序**以 Flux `Kustomization.spec.dependsOn` 为准。
- `ks.yaml`：约定为 Flux `Kustomization` CR（不是 kustomize 的 `kustomization.yaml`）。

## ANTI-PATTERNS
- 不要在 `apps/default/kustomization.yaml` 里直接塞复杂逻辑：它更像“目录索引/开关面板”。复杂依赖放在各 app 的 `ks.yaml`。
