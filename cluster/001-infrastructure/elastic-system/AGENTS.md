# elastic-system/ — Elasticsearch / Kibana (ECK)

## OVERVIEW
通过 ECK operator 管理 Elasticsearch 集群与 Kibana；认证相关 Secret 多为 `*.sops.yaml`。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 顶层索引 | `kustomization.yaml` |
| ECK operator | `eck-operator/`（`helm-release.yaml` / `default.yaml`） |
| ES / Kibana | `elastic-cluster/` |
| 用户/角色等 | `elastic-cluster/auths/`（多为 `*.sops.yaml`） |

## ANTI-PATTERNS
- 不要把认证配置从 SOPS 改成明文 Secret；本仓库默认要求敏感信息加密后提交。
