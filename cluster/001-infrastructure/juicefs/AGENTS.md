# juicefs/ — JuiceFS + Ceph Pools + 元数据服务

## OVERVIEW
JuiceFS 在本集群中作为“可共享文件系统”层，底层数据落 Ceph pools；元数据用 Redis/PostgreSQL（按用途区分）。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 资源索引 | `kustomization.yaml` |
| CephBlockPool 定义 | `ceph-*-pool.yaml` |
| 元数据 Redis | `redis/helm-release.yaml` |
| 元数据 PostgreSQL | `*-postgresql/`（`cluster.yaml` + `secret.sops.yaml` 等） |

## CONVENTIONS
- 这里既包含“Ceph pools”（供 JuiceFS/业务使用），也包含“元数据服务”（Redis/PostgreSQL）。
- 业务 PVC 通常在各 app 目录下引用本层创建的 StorageClass（不要在此层里到处改 app 的 PVC）。

## ANTI-PATTERNS
- 不要把数据库类随机写负载放在“压缩/纠删码”类文件系统上（成本与碎片风险高）；按 StorageClass 命名含义选型。
