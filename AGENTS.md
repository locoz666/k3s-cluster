# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-06 (Asia/Shanghai)
**Branch:** main
**Commit:** 4c9d0933

## OVERVIEW
家用 k3s 集群的 GitOps 仓库：FluxCD 驱动集群状态；绝大多数为 YAML 清单；SOPS(PGP) 加密 Secret；HelmRelease + Kustomization 组合部署。

## STRUCTURE
```text
./
├── cluster/                  # 集群声明式状态（分层：000-base → 001/002 → apps → VM/智能家居）
├── scripts/                  # 少量运维脚本（含磁盘清空/挂载等危险操作）
├── tests/                    # 手工验证用的测试清单（PVC / 网络等）
├── tmpl/                     # bootstrap 模板（envsubst 生成 .sops.yaml / gotk-sync 等）
├── .github/                  # PR lint + Renovate 配置
├── Taskfile.yml              # go-task 入口（包含 flux/format/lint/pre-commit）
├── .pre-commit-config.yaml   # 本地提交前检查（yamllint + forbid-secrets 等）
└── .sops.yaml                # SOPS 加密规则（encrypted_regex + PGP 指纹）
```

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| Flux 引导/同步 | `cluster/000-base/flux-system/gotk-sync.yaml` | 指向 `./cluster/000-base`；含 SOPS 解密配置（`sops-gpg`） |
| 调整分层顺序/依赖 | `cluster/000-base/*.yaml` | 多个 Flux `Kustomization` CR（`dependsOn` + `path`） |
| 全局替换变量（`${SECRET_*}`） | `cluster/000-base/cluster-secrets.sops.yaml` | SOPS 加密；由 `apps.yaml` 等在 `postBuild.substituteFrom` 注入 |
| 新增/更新 Helm/OCI 仓库 | `cluster/000-base/repositories/{helm,oci}/` | Source CR（HelmRepository/OCIRepository） |
| 新增/启用一个 default 命名空间应用 | `cluster/apps/default/kustomization.yaml` | 这里是“开关面板”（是否 include 某个 app 的 `ks.yaml`） |
| 单个应用的 Flux 入口 | `cluster/apps/**/<app>/ks.yaml` | 一个文件里常包含多个 Kustomization（postgres/redis/app 等） |
| 存储（Ceph/JuiceFS） | `cluster/001-infrastructure/{rook-ceph,juicefs}/` | 存储类/池/元数据服务均在此组织 |
| 监控与可观测性 | `cluster/001-infrastructure/monitoring-system/` | kube-prometheus-stack；注意 `vector` 可能被注释掉 |
| TLS / 证书 | `cluster/002-infrastructure-extra/cert-manager/` | ClusterIssuer + wildcard Certificate（含 direct 域名证书） |
| Traefik 中间件/白名单 | `cluster/apps/kube-system/traefik/middlewares/` | `rfc-1918` / basic-auth 等 |

## CONVENTIONS (REPO-SPECIFIC)
- 主要工具链：go-task（`Taskfile.yml` + `.taskfiles/*.yml`）。
- YAML/MD 质量：
  - `yamllint` 配置：`.github/lint/.yamllint.yaml`（忽略 `*.sops.*` 与 `gotk-components.yaml`）。
  - `prettier`：`.github/lint/.prettierrc.yaml` + `.github/lint/.prettierignore`。
  - `markdownlint`：`.github/lint/.markdownlint.yaml`。
- Secrets：SOPS 只加密 `data|stringData`（见 `.sops.yaml` 的 `encrypted_regex`）；本地 pre-commit 有 `forbid-secrets` 防止明文 Secret。
- Renovate：
  - 全局配置：`.github/renovate.json5`（含 automerge、digest、fileMatch 等）。
  - HelmRelease 内联：大量 `# renovate: registryUrl=...`（用于 chart 版本跟踪）。

## ANTI-PATTERNS (THIS REPO)
- **不要编辑** Flux 生成的清单：`cluster/000-base/flux-system/gotk-*.yaml` / `gotk-components.yaml`（文件头会写 DO NOT EDIT）。
- **不要提交** SOPS 解密产物：`.decrypted~*.yaml`（已在 `.gitignore` 忽略，但仍需避免外泄）。
- Rook/Ceph：某些选项只允许“首次部署”设置，错误变更可能导致数据破坏/集群被清空（以 `rook-ceph` Helm values 内的 WARNING 为准）。

## COMMANDS
```bash
# 常用（go-task）
task flux:sync
task lint:all
task format:all
task pre-commit:init
task pre-commit:run

# 直接跑 pre-commit
pre-commit run --all-files
```

## NOTES
- `.envrc` 会导出 `KUBECONFIG=./kubeconfig`；`task flux:sync` 会切 `kubectl ctx home`。
- `cluster/000-base/apps.yaml` 会用 `labelSelector: substitution.flux.home.arpa/disabled notin (true)` 给 **cluster/apps 路径里定义的** Flux `Kustomization` 统一注入 `decryption + substituteFrom`；需要禁用时加 label。
