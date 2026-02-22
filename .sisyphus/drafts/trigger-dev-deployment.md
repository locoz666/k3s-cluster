# Draft: Trigger.dev Self-Hosted Deployment

## Requirements (confirmed)
- 部署 trigger.dev v4 私有版本到 home k3s 集群
- 所有数据库/对象存储作为外部服务独立部署
- 部署在 default 命名空间
- 遵循现有 FluxCD 部署规范

## Technical Decisions

### 组件分析 (trigger.dev v4)
| 组件 | 说明 | 部署方式 |
|------|------|----------|
| Webapp | 主 UI/API | Helm chart (OCI: ghcr.io/triggerdotdev/charts/trigger) |
| Supervisor | 任务调度器 | Helm chart 内含 |
| PostgreSQL | 主数据库 | 外部 - CloudNativePG (遵循 prefect/immich 模式) |
| Redis | 缓存/队列 | 外部 - Bitnami Redis via OCIRepository (遵循 immich 模式) |
| ClickHouse | 遥测/日志 | 外部 - 需单独部署 |
| MinIO/S3 | 对象存储 | 外部 - bjw-s app-template (遵循 happy-coder 模式) |
| Container Registry | 任务镜像构建 | 使用现有 GitLab Registry |

### 集群现有模式 (已确认)
1. **ks.yaml**: Flux Kustomization CRs，`dependsOn` 链式依赖
2. **CloudNativePG**: `postgresql.cnpg.io/v1 Cluster` + `Pooler` + SOPS secret
3. **Bitnami Redis**: OCIRepository `bitnami-redis` + HelmRelease
4. **MinIO**: bjw-s `app-template` chart + PVC
5. **Secrets**: `${SECRET_*}` 变量替换 via `postBuild.substituteFrom`
6. **Ingress**: Traefik className + wildcard TLS `${SECRET_DOMAIN/./-}-tls`
7. **Storage**: `ceph-application-high-performance` (DB) / `juicefs-application-compressed` (数据)

## Research Findings
- trigger.dev v4 使用 OCI Helm chart: `oci://ghcr.io/triggerdotdev/charts/trigger ~4.0.0`
- 支持 `postgres.deploy: false` + `external.existingSecret` 模式
- 支持 `redis.deploy: false` + `external.host/port/password`
- 支持 `clickhouse.deploy: false` + `external.host/port/username/password`
- 支持 `minio.deploy: false` + `s3.external.endpoint`
- 需要 secrets: SESSION_SECRET, MAGIC_LINK_SECRET, ENCRYPTION_KEY, MANAGED_WORKER_SECRET
- 对象存储凭据: OBJECT_STORE_ACCESS_KEY_ID, OBJECT_STORE_SECRET_ACCESS_KEY
- 容器注册表: DEPLOY_REGISTRY_HOST, DEPLOY_REGISTRY_USERNAME, DEPLOY_REGISTRY_PASSWORD

## Open Questions
1. Container Registry: 使用现有 GitLab Registry 还是部署新的?
2. ClickHouse: 使用什么方式部署? (集群中没有现有 ClickHouse 模式)
3. 是否需要配置 GitHub OAuth 或其他认证方式?

## Scope Boundaries
- INCLUDE: PostgreSQL, Redis, ClickHouse, MinIO, Webapp+Supervisor, Ingress, Secrets
- EXCLUDE: 邮件发送配置, Slack 集成, 自定义 machine presets
