# tmpl/ — bootstrap 模板

## OVERVIEW
用于初始化/迁移时生成关键文件的模板（通常通过 `envsubst`）。

## WHERE TO LOOK
| 模板 | 生成目标（典型） |
|------|------------------|
| `.sops.yaml` | 仓库根 `.sops.yaml` |
| `cluster-secrets.sops.yaml` | `cluster/000-base/cluster-secrets.sops.yaml` |
| `cluster-settings.yaml` | 集群 settings（本仓库当前未必使用） |
| `gotk-sync.yaml` | `cluster/000-base/flux-system/gotk-sync.yaml` |
| `secret.sops.yaml` | cert-manager 等组件的 secret 模板 |

## ANTI-PATTERNS
- 不要把模板当运行时配置：模板用于生成一次性“落地文件”，运行时以 `cluster/` 下实际清单为准。
