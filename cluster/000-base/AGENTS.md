# cluster/000-base/ — Flux 入口层

## OVERVIEW
Flux 引导入口：定义 Flux 自身（gotk-*）、Source 仓库、命名空间、全局 secrets，以及后续各层的 Flux `Kustomization` CR。

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| 根 kustomize 资源索引 | `kustomization.yaml` | resources 列表决定 base 包含哪些目录/清单 |
| Flux 自身组件 | `flux-system/` | `gotk-components.yaml` / `gotk-sync.yaml`（生成物，别手改） |
| Helm/OCI 仓库 | `repositories/` | Source CR + 子目录 `helm/`、`oci/` |
| 全局替换变量 Secret | `cluster-secrets.sops.yaml` | SOPS 加密；Flux 通过 `substituteFrom` 注入到多数 Kustomization |
| “层级 Kustomization CR” | `001-infrastructure.yaml` 等 | 每个文件定义一个 `kustomize.toolkit.fluxcd.io/v1` Kustomization |
| 基础命名空间 | `namespaces_infrastructure/`、`namespaces_other/` | 统一声明 namespace |

## CONVENTIONS
- 这里的 `*.yaml`（如 `001-infrastructure.yaml`）是 **Flux Kustomization CR**，不是 kustomize 的 resources 列表。
- `.decrypted~cluster-secrets.sops.yaml` 是 vscode-sops/编辑产物（已在 `.gitignore` 忽略）；不要传播/提交。

## ANTI-PATTERNS
- 不要修改 `cluster-secrets.sops.yaml` 的加密结构（`sops:` 区块）；用 `sops` 工具编辑/加密。
