# cert-manager/ — Issuer 与通配证书

## OVERVIEW
cert-manager 的额外配置层：ClusterIssuer（HTTP/DNS）与多套 wildcard Certificate（含 direct 子域名用途）。

## WHERE TO LOOK
| 任务 | 位置 | 备注 |
|------|------|------|
| 入口索引 | `kustomization.yaml` | 列出 secret/issuer/cert 资源 |
| Cloudflare 等凭据 | `secret.sops.yaml` | SOPS 加密 |
| DNS-01 Issuer | `letsencrypt-dns.yaml` | 通常用于 `*.${SECRET_DOMAIN}` |
| HTTP-01 Issuer | `letsencrypt-http.yaml` | 给 ingressShim 或特定场景 |
| 通配证书 | `wildcard-certificate*.yaml` | secretName 通常为 `${SECRET_DOMAIN/./-}-tls` |
| direct 通配证书 | `direct-wildcard-certificate.yaml` | secretName 通常为 `direct-${SECRET_DOMAIN/./-}-tls` |

## CONVENTIONS
- 证书文件里会引用 `${SECRET_DOMAIN}` 等变量（由 Flux `substituteFrom: cluster-secrets` 提供）。
