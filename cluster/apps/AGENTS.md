# cluster/apps/ — 应用层（按 namespace 分组）

## OVERVIEW
所有“业务/系统应用”清单集中在这里；通过各 namespace 的 `kustomization.yaml` 选择启用哪些 app。

## STRUCTURE
```text
apps/
├── default/        # 大多数业务应用
├── kube-system/    # 系统级组件（traefik/cilium/...）
├── cnpg-system/    # CloudNativePG 等
└── cluster-network-addons/
```

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 启用/禁用 default 下的应用 | `default/kustomization.yaml` |
| default 命名空间 | `default/namespace.yaml` |
| kube-system 组件入口 | `kube-system/kustomization.yaml` |
| 单个应用的编排入口 | `<ns>/<app>/ks.yaml` |

## CONVENTIONS
- `<app>/ks.yaml`：Flux `Kustomization` CR（常含多段：postgres/redis/app 等）。
- `<app>/app/`：通常放 HelmRelease + values（以及 ingress/pvc 等）并由 `ks.yaml` 指向。
