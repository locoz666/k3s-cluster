# tests/ — 手工验证清单

## OVERVIEW
用于在集群里手工验证存储/网络能力的测试资源（不是自动化单测）。

## WHERE TO LOOK
| 文件 | 验证内容 |
|------|----------|
| `test-ceph-fs.yaml` | CephFS RWX：创建 PVC + Pod 挂载 `/data` |
| `test-ceph-block.yaml` | Ceph RBD：块存储 PVC + Pod |
| `test-ceph-storage-pvcs.yaml` | 多个 StorageClass 的 PVC 组合验证 |
| `test-ceph-rbd-direct-mount.yaml` | RBD 直挂相关验证 |
| `test-local-path.yaml` | local-path provisioner 验证 |
| `test-network-speed.yaml` | iperf3 server（hostPort 5201） |

## COMMANDS
```bash
kubectl apply -f tests/test-ceph-fs.yaml
kubectl apply -f tests/test-network-speed.yaml
```

## NOTES
- 这些清单会创建 namespace/PVC/Pod；验证完记得清理（`kubectl delete -f ...`）。
