# cluster/002-infrastructure-extra/ — 额外基础设施

## OVERVIEW
补充基础设施层：证书颁发/通配证书、JuiceFS CSI 驱动、Ceph 快照类等。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 顶层索引 | `kustomization.yaml` |
| ClusterIssuer / wildcard 证书 | `cert-manager/` |
| JuiceFS CSI driver 与 StorageClass | `juicefs/helm-release.yaml` |
| VolumeSnapshotClass | `rook-ceph/volume-snapshot-class.yaml` |
