# apps/kube-system/ — 系统组件

## OVERVIEW
kube-system 命名空间中的系统级组件与中间件（Traefik/Cilium 等）。

## WHERE TO LOOK
| 任务 | 位置 |
|------|------|
| Traefik 安装 | `traefik/app/helm-release.yaml` |
| Traefik 中间件 | `traefik/middlewares/` | `rfc-1918` 白名单、basic-auth Secret（SOPS）等 |
| Cilium | `cilium/` | 目录内 `default.yaml` 等可能是生成物（文件头会写 DO NOT EDIT） |
| Snapshot Controller | `snapshot-controller/` |
| JuiceFS GC cronjob | `juicefs-gc-cronjob/` |

## CONVENTIONS
- 该 namespace 的中间件常被业务 Ingress 通过注解引用：
  - `traefik.ingress.kubernetes.io/router.middlewares: kube-system-rfc1918@kubernetescrd`
