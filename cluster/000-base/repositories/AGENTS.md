# cluster/000-base/repositories/ — Source 定义

## OVERVIEW
集中管理 Flux Source：HelmRepository/OCIRepository 等（供 HelmRelease 引用）。

## STRUCTURE
```text
repositories/
├── helm/        # HelmRepository 定义
├── oci/         # OCIRepository 定义（如 bitnami-*）
└── kustomization.yaml
```

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 新增 HelmRepo | `helm/<name>.yaml` + `helm/kustomization.yaml` |
| 新增 OCIRepo | `oci/<name>.yaml` + `oci/kustomization.yaml` |
| 全量聚合 | `kustomization.yaml` |

## CONVENTIONS
- 文件名通常与 repo 名一致（便于 grep/renovate 规则匹配）。
