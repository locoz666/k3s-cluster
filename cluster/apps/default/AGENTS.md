# apps/default/ — 默认命名空间应用

## OVERVIEW
default 命名空间的应用集合；`kustomization.yaml` 是“启用清单索引”。单个应用一般通过 `<app>/ks.yaml` 进一步拆分依赖。

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| 启用/禁用某个应用 | `kustomization.yaml` | 通过增删（或注释）`./<app>/ks.yaml` |
| 单应用编排 | `<app>/ks.yaml` | 多段 Kustomization：如 nextcloud 拆成 postgresql/redis/imaginary/collabora/app |
| HelmRelease/values | `<app>/app/helm-release.yaml` + `default.yaml` | 大量 `# renovate: registryUrl=...` |
| Secret（镜像拉取/应用密钥） | `<app>/**.sops.yaml` | 例如 `registry-secret.sops.yaml` / `secret.sops.yaml` |
| Ingress/Traefik CRD | `<app>/**ingress*.yaml`、`**/traefik-*.yaml` | 既有标准 Ingress，也有 `traefik.io/v1alpha1` 中间件 |
| 公共共享卷/资源 | `public/` | `kustomization.yaml` 列出多个 *-files.yaml |

## CONVENTIONS
- `ks.yaml` 通常：
  - `targetNamespace: default`
  - `commonMetadata.labels.app.kubernetes.io/name` 统一注入
  - `dependsOn` 声明 infra（常见 `002-infrastructure-extra`）以及自身依赖（postgres/redis 等）

## ANTI-PATTERNS
- 不要在 `kustomization.yaml` 里直接写应用参数；参数归属在各 app 子目录。
