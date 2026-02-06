# scripts/ — 运维脚本

## OVERVIEW
少量脚本用于“集群外”的人工运维（磁盘清空/挂载、镜像导入、BMC 相关、dev-container 挂载覆盖检查）。

## WHERE TO LOOK
| 脚本 | 用途 |
|------|------|
| `clear_disk.sh` | **危险**：对指定磁盘执行 `sgdisk --zap-all` + `dd` + `blkdiscard` |
| `init_rook_data_disk.sh` | 挂载磁盘到 `/var/lib/rook`，并追加 `/etc/fstab` |
| `import_images.py` | 在当前目录遍历镜像 tar 并 `ctr i import`（containerd）；注意当前实现用 `Path.suffix == "tar"` 过滤，可能匹配不到 `.tar` 文件 |
| `get_megarac_jviewer.py` | BMC/JViewer 相关 |
| `find_unmounted_root_paths.py` | 解析 dev-container HelmRelease 的挂载点，找出 `/root` 下未覆盖路径（依赖 `yq`） |

## ANTI-PATTERNS
- 不要在不确认盘符的情况下运行 `clear_disk.sh`（脚本会清空磁盘）。
- `init_rook_data_disk.sh` 会直接写 `/etc/fstab`；确保目标盘已格式化且 UUID 正确。
