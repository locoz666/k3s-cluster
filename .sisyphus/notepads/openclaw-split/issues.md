## 2026-02-22

- 当前执行环境缺少 `pre-commit` 与 `task` 命令，无法运行仓库标准 lint 流程；改用 `kubectl apply --dry-run=client` 对新增 HelmRelease 做语法验证。
