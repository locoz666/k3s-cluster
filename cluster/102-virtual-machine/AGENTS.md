# 102-virtual-machine/ — 虚拟机实例

## OVERVIEW
具体 VM 与相关资源（ISO/VM yaml/PVC 等）。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| 顶层索引 | `kustomization.yaml` |
| 命名空间 | `namespace.yaml` | 带 `sync-https-wildcard-certificate` label |
| Windows VM 示例 | `vm-game/vm.yaml` |
| VM PVC | `vm-game/pvcs/` |
| ISO 资源 | `isos/` |
