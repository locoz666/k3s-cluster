# .github/ — PR 校验与自动化

## OVERVIEW
GitHub Actions 主要做静态检查（YAML/Shell/Markdown）；Renovate 用于 Helm chart/镜像更新与自动合并策略。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| Renovate 全局规则 | `renovate.json5` |
| YAML lint | `workflows/lint.yaml` + `lint/.yamllint.yaml` |
| Shell lint | `workflows/lint-shell.yaml` |
| Markdown lint | `workflows/lint-markdown.yaml` + `lint/.markdownlint.yaml` |
| Prettier 配置 | `lint/.prettierrc.yaml` + `lint/.prettierignore` |
| Issue/PR 模板 | `ISSUE_TEMPLATE/` + `PULL_REQUEST_TEMPLATE.md` |

## NOTES
- `lint-markdown.yaml` 当前用的是 `reviewdog/action-shellcheck@v1`，但传入了 `markdownlint_flags`：这看起来像 workflow 配置错误（可能导致 markdownlint 不会真正运行）。
