# juicefs/ — JuiceFS CSI driver（额外层）

## OVERVIEW
部署 JuiceFS CSI driver，并创建一组 JuiceFS StorageClass（依赖 `001-infrastructure/juicefs` 创建的 pools/元数据）。

## WHERE TO LOOK
- `helm-release.yaml`：JuiceFS CSI driver 的 HelmRelease（含 StorageClass 参数）。
- `juicefs-cache-pvc.yaml`：cache 相关 PVC（如果 StorageClass 引用 cachePVC）。
