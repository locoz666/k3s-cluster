# cluster/000-base/flux-system/ — Flux 自身

## OVERVIEW
Flux 引导与组件安装清单：本仓库的 reconcile 起点。

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| GitRepository + 根 Kustomization | `gotk-sync.yaml` | `path: ./cluster/000-base`；含 `decryption: sops` 与 `sops-gpg` SecretRef |
| Flux 组件安装 | `gotk-components.yaml` | 超大生成文件（包含 controller/CRD/RBAC）；禁止手改 |
| kustomize 聚合 | `kustomization.yaml` | 仅引用 `gotk-*.yaml` |

## ANTI-PATTERNS
- `gotk-*.yaml`：文件头写明 **DO NOT EDIT**。要升级/重建 Flux，走 `flux` CLI/官方流程生成后再替换。
