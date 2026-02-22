# OpenClaw 从 dev-container 拆分重构计划

## TL;DR

> **目标**: 将 OpenClaw 从 dev-container 内部服务拆分为独立的 Kubernetes Deployment
> 
> **核心变更**:
> - 从 dev-container 移除 clawdbot s6 服务和相关配置
> - 创建独立的 `openclaw` Deployment + Service + Ingress
> - 迁移数据到独立 PVC 或保留在原 PVC 但通过新方式挂载
> - 保留现有的 ingress 域名和 TLS 配置
> 
> **风险等级**: 中等（涉及数据迁移和服务切换）
> **预计工作量**: 2-3 小时
> **并行度**: 低（存在依赖关系）
> **关键路径**: 数据备份 → 创建独立部署 → 切换入口 → 清理旧配置

---

## Context

### 原始需求
用户希望将 OpenClaw 从 dev-container 中拆分出来，实现独立部署。

### 当前架构
OpenClaw 目前作为 dev-container 的内部组件运行：
- **安装**: Dockerfile 中通过 curl 脚本安装
- **进程管理**: s6-overlay 服务（clawdbot）
- **网络**: 监听容器内 18789 端口，通过 dev-container 的 Service/Ingress 暴露
- **数据**: 存储在 dev-share-files PVC 的特定 subPath 中

### 调研发现
1. **无外部依赖**: OpenClaw 是自包含的 gateway 服务，不依赖数据库、缓存等
2. **数据量小**: 主要是配置文件和 skills，易于迁移
3. **共享需求**: skills 目录与 OpenCode 等其他 AI 工具共享
4. **简单网络**: 单端口 HTTP 服务，Ingress 配置简单
5. **健康检测方式**: OpenClaw 是单页应用（SPA），所有路径返回相同 HTML 页面，根路径 `/` 返回 HTTP 200，适合作为健康检测端点

---

## Work Objectives

### 核心目标
将 OpenClaw 从 dev-container 的单体架构中拆分，作为独立的微服务部署。

### 具体交付物
1. **新资源文件**:
   - `cluster/apps/default/openclaw/ks.yaml` - Flux Kustomization
   - `cluster/apps/default/openclaw/app/helm-release.yaml` - HelmRelease（含健康检测探针、共享 PVC 挂载）
   - `cluster/apps/default/openclaw/app/kustomization.yaml`
   - `cluster/apps/default/openclaw/app/ingress.yaml` - Ingress 路由
   - ~~`cluster/apps/default/openclaw/app/pvc.yaml`~~ - **不需要创建**（使用共享 PVC）

2. **修改现有文件**:
   - `cluster/apps/default/dev-container/app/helm-release.yaml` - 移除 OpenClaw 相关配置
   - `cluster/apps/default/kustomization.yaml` - 添加 openclaw 引用

3. **dev-container 更新**:
   - `loco/dev-container/Dockerfile` - 可选：移除 OpenClaw 安装
   - `loco/dev-container/rootfs/etc/s6-overlay/s6-rc.d/` - 移除 clawdbot 服务

### 定义完成标准
- [ ] OpenClaw 作为独立 Pod 运行（非 dev-container 内部）
- [ ] 数据成功迁移，原有配置和 skills 保留
- [ ] Ingress `openclaw.${SECRET_DOMAIN}` 正常访问
- [ ] dev-container 中不再启动 clawdbot 服务
- [ ] 零停机时间切换

### 必须完成
- 独立 Deployment 正常运行
- 数据完整性验证
- Ingress 切换

### 明确排除（Guardrails）
- **不更改域名**: 继续使用 `openclaw.${SECRET_DOMAIN}`
- **不修改数据格式**: 保留现有的文件结构和权限
- **不引入新依赖**: 不添加 Redis、数据库等外部依赖
- **不修改 skills 共享机制**: 保持与其他 AI 工具的 skills 共享
- **不创建新 PVC**: 使用现有的 `dev-share-files` PVC 进行共享挂载

---

## Verification Strategy

### 测试决策
- **基础设施**: 使用现有 k3s + Flux 环境
- **测试方式**: 人工验证（访问 Web UI、检查数据）
- **无自动化测试**: 本项目为基础设施配置，无单元测试

### QA 策略
每个任务包含 Agent-Executed QA Scenarios：
- **部署验证**: kubectl 检查 Pod/Service/Ingress 状态
- **功能验证**: curl 测试 gateway 端口响应
- **数据验证**: 检查挂载卷中的文件完整性

---

## Execution Strategy

### 执行顺序（串行，低并行度）

```
Wave 1: 准备与备份（无法并行）
├── Task 1: 备份现有数据
└── Task 2: 准备新 PVC 和数据

Wave 2: 创建独立部署
├── Task 3: 创建 openclaw namespace 和资源结构
├── Task 4: 创建 HelmRelease 和 Deployment
└── Task 5: 配置 Service 和 Ingress

Wave 3: 切换与验证
├── Task 6: 验证独立部署正常运行
├── Task 7: 更新 dev-container 移除 OpenClaw 配置
└── Task 8: 切换 Ingress 到新的 Service

Wave 4: 清理与验证
├── Task 9: 清理 dev-container 中的旧数据挂载
├── Task 10: 最终验证和文档更新
└── Task F1: 计划合规性审计（oracle）
```

### 依赖矩阵

| Task | Depends On | Blocks | Status |
|------|-----------|--------|--------|
| 1 | - | 2 | pending |
| 2 | 1 | 3,4 | pending |
| 3 | 2 | 4,5 | pending |
| 4 | 3 | 6 | pending |
| 5 | 3 | 7 | pending |
| 6 | 4 | 7 | pending |
| 7 | 5,6 | 8 | pending |
| 8 | 7 | 9 | pending |
| 9 | 8 | 10 | pending |
| 10 | 9 | F1 | pending |
| F1 | 10 | - | pending |

### 关键路径
Task 1 → Task 2 → Task 3 → Task 4 → Task 6 → Task 7 → Task 8 → Task 10 → Task F1

---

## TODOs

- [ ] 1. 备份现有 OpenClaw 数据

  **What to do**:
  - 进入 dev-container Pod，检查当前 OpenClaw 数据
  - 备份 `/root/.openclaw` 和 `/root/clawd` 目录
  - 验证备份完整性

  **Must NOT do**:
  - 不要删除任何原始数据
  - 不要修改 dev-container 的当前配置

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: 执行 kubectl exec 命令进行数据备份，需要基础 Kubernetes 操作能力

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References**:
  - `cluster/apps/default/dev-container/app/helm-release.yaml:224-232` - 当前 OpenClaw 数据挂载配置
  - 数据路径: `/root/.openclaw`, `/root/clawd`

  **Acceptance Criteria**:
  - [ ] 成功创建数据备份（tar 或 cp）
  - [ ] 验证备份文件存在且非空
  - [ ] 记录备份位置和校验和

  **QA Scenarios**:
  ```
  Scenario: 验证数据备份完整性
    Tool: Bash (kubectl)
    Steps:
      1. kubectl exec -it dev-container-pod -- ls -la /root/.openclaw
      2. kubectl exec -it dev-container-pod -- ls -la /root/clawd
      3. kubectl exec -it dev-container-pod -- tar czf /tmp/openclaw-backup.tar.gz /root/.openclaw /root/clawd
      4. kubectl exec -it dev-container-pod -- ls -lh /tmp/openclaw-backup.tar.gz
    Expected Result: 备份文件存在，大小 > 0，包含配置和 skills
    Evidence: kubectl exec 输出截图

  Scenario: 验证备份文件可读取
    Tool: Bash (kubectl)
    Steps:
      1. kubectl exec -it dev-container-pod -- tar tzf /tmp/openclaw-backup.tar.gz | head -20
    Expected Result: 显示备份内容的文件列表
    Evidence: 文件列表输出
  ```

  **Commit**: NO（此任务不产生代码变更）

---

- [ ] 2. 确定共享 PVC 挂载策略

  **What to do**:
  - 确认 OpenClaw 继续使用现有的 `dev-share-files` PVC
  - 规划 HelmRelease 中的 volumeMounts 配置（使用相同的 subPath）
  - 确保与 dev-container 的数据挂载路径一致，避免路径冲突
  - 准备数据访问验证方案

  **决策确认**:
  - ✅ **使用共享 PVC**: `dev-share-files`（与 dev-container 共用）
  - **挂载路径**:
    - `/root/.openclaw` → `user_data/HOME/.openclaw`
    - `/root/clawd` → `user_data/HOME/clawd`
    - `/tmp/clawdbot` → `user_data/tmp`
    - `/root/clawd/skills` → `ai_user_data/skills`（共享）

  **Must NOT do**:
  - 不要创建新的 PVC
  - 不要修改现有 PVC 中的数据路径结构
  - 不要在挂载配置上使用不同的 subPath（会导致数据访问不到）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: 分析现有挂载配置，规划共享策略

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 3, Task 4
  - **Blocked By**: Task 1

  **References**:
  - `cluster/apps/default/dev-container/app/helm-release.yaml:124-232` - 现有 PVC 挂载配置
  - `cluster/apps/default/public/dev-share-files.yaml` - PVC 定义（如存在）

  **Acceptance Criteria**:
  - [ ] 确认共享 PVC 策略文档化
  - [ ] 列出所有需要挂载的路径和对应的 subPath
  - [ ] 验证挂载路径与 dev-container 一致
  - [ ] 确认无路径冲突

  **QA Scenarios**:
  ```
  Scenario: 验证 PVC 存在和状态
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get pvc -n default | grep dev-share-files
      2. kubectl describe pvc dev-share-files -n default
    Expected Result: PVC 状态为 Bound，容量和存储类正确
    Evidence: kubectl 输出

  Scenario: 验证现有挂载配置
    Tool: Bash
    Steps:
      1. grep -A20 "dev-share-files:" cluster/apps/default/dev-container/app/helm-release.yaml | grep -E "subPath|path.*openclaw|path.*clawd"
    Expected Result: 显示当前的 OpenClaw 相关挂载配置
    Evidence: 配置输出
  ```

  **Commit**: NO（此任务为策略确认，不产生代码变更）

---

- [ ] 3. 创建 openclaw 应用目录结构和 Flux Kustomization

  **What to do**:
  - 创建目录 `cluster/apps/default/openclaw/`
  - 创建 `ks.yaml` - Flux Kustomization 入口
  - 创建 `app/kustomization.yaml`
  - 更新 `cluster/apps/default/kustomization.yaml` 添加 openclaw 引用（注释状态）

  **Must NOT do**:
  - 不要在最初就启用 openclaw（先创建结构，后启用）
  - 不要复制其他应用的错误模式

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: 创建基础目录结构和标准 Flux 配置

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 4, Task 5
  - **Blocked By**: Task 2

  **References**:
  - `cluster/apps/default/dev-container/ks.yaml` - 参考结构
  - `cluster/apps/default/kustomization.yaml` - 需要修改的文件
  - `cluster/apps/default/dev-container/app/kustomization.yaml` - 参考模式

  **Acceptance Criteria**:
  - [ ] 目录结构创建完成
  - [ ] ks.yaml 配置正确（参考 dev-container 模式）
  - [ ] kustomization.yaml 正确引用各资源
  - [ ] default/kustomization.yaml 添加 openclaw（注释）

  **QA Scenarios**:
  ```
  Scenario: 验证目录结构
    Tool: Bash
    Steps:
      1. ls -la cluster/apps/default/openclaw/
      2. ls -la cluster/apps/default/openclaw/app/
      3. cat cluster/apps/default/openclaw/ks.yaml
    Expected Result: 目录存在，包含 ks.yaml 和 app/ 子目录
    Evidence: 目录列表和文件内容

  Scenario: 验证 kustomize 语法
    Tool: Bash (kustomize)
    Steps:
      1. kustomize build cluster/apps/default/openclaw/app/ 2>&1 | head -50
    Expected Result: 成功构建，无错误
    Evidence: 构建输出或错误信息
  ```

  **Commit**: YES
  - Message: `feat(openclaw): add directory structure and flux kustomization`
  - Files: `cluster/apps/default/openclaw/ks.yaml`, `cluster/apps/default/openclaw/app/kustomization.yaml`

---

- [ ] 4. 创建 OpenClaw HelmRelease 和 Deployment 配置（含健康检测）

  **What to do**:
  - 创建 `cluster/apps/default/openclaw/app/helm-release.yaml`
  - 配置容器镜像（复用 dev-container 镜像或独立镜像）
  - 配置环境变量（CLAWDBOT_DIAGNOSTICS='*', CLAWDBOT_CACHE_TRACE=1, NODE_DEBUG=undici）
  - 配置资源限制（CPU/内存/GPU，参考 dev-container 配置）
  - **配置共享 PVC 挂载**（使用 dev-share-files，与 dev-container 一致）
  - **配置 Kubernetes 健康检测探针**:
    - **livenessProbe**: HTTP GET /health，失败 3 次后重启 Pod
    - **readinessProbe**: HTTP GET /health，控制流量接入
    - **startupProbe**: 保护慢启动应用，避免过早判定失败
  - 配置命令覆盖（执行 `openclaw gateway`）

  **健康检测配置详情**:
  
  根据实际检查，OpenClaw 是单页应用（SPA），所有路径返回相同前端 HTML：
  - 根路径 `/` 返回 HTTP 200 OK
  - 无专门健康端点（如 `/health`, `/healthz`）
  - 因此使用根路径作为健康检测端点
  
  ```yaml
  probes:
    liveness:
      enabled: true
      type: HTTP
      path: /           # 使用根路径，返回 HTTP 200
      port: 18789
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    readiness:
      enabled: true
      type: HTTP
      path: /           # 使用根路径
      port: 18789
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
    startup:
      enabled: true
      type: HTTP
      path: /           # 使用根路径
      port: 18789
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 30  # 给予 150 秒启动时间
  ```

  **PVC 挂载配置**:
  ```yaml
  persistence:
    dev-share-files:
      existingClaim: dev-share-files
      advancedMounts:
        main:
          openclaw:
            - path: /root/.openclaw
              subPath: user_data/HOME/.openclaw
            - path: /root/clawd
              subPath: user_data/HOME/clawd
            - path: /tmp/clawdbot
              subPath: user_data/tmp
            - path: /root/clawd/skills
              subPath: ai_user_data/skills
  ```

  **Must NOT do**:
  - 不要硬编码敏感信息
  - 不要创建新的 PVC
  - 不要修改 subPath（必须与 dev-container 一致）
  - 不要使用过于激进的探针参数（避免误杀）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: 需要理解 OpenClaw 启动参数、健康检测端点，以及 Kubernetes 探针配置

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 6
  - **Blocked By**: Task 3

  **References**:
  - `cluster/apps/default/dev-container/app/helm-release.yaml` - 参考结构和资源配置
  - `loco/dev-container/rootfs/etc/s6-overlay/s6-rc.d/clawdbot/run` - 启动参数和环境变量
  - `loco/dev-container/Dockerfile:461` - 安装方式和镜像信息
  - Kubernetes Probe 文档: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

  **Acceptance Criteria**:
  - [ ] HelmRelease 配置完整
  - [ ] 环境变量正确映射（CLAWDBOT_DIAGNOSTICS='*', CLAWDBOT_CACHE_TRACE=1, NODE_DEBUG=undici）
  - [ ] 端口配置正确（18789）
  - [ ] **livenessProbe 配置正确**（路径 `/`, 30s 初始延迟）
  - [ ] **readinessProbe 配置正确**（路径 `/`, 10s 初始延迟）
  - [ ] **startupProbe 配置正确**（防止启动时过早重启）
  - [ ] **共享 PVC 挂载配置正确**（dev-share-files，subPath 与 dev-container 一致）
  - [ ] 资源限制合理（CPU/内存，GPU 如需要）
  - [ ] 命令覆盖正确（`openclaw gateway --port 18789 ...`）

  **QA Scenarios**:
  ```
  Scenario: 验证 HelmRelease 语法
    Tool: Bash (kubectl)
    Steps:
      1. kubectl apply --dry-run=client -f cluster/apps/default/openclaw/app/helm-release.yaml
    Expected Result: dry-run 成功，无语法错误
    Evidence: 命令输出

  Scenario: 验证健康检测配置
    Tool: Bash (grep/阅读)
    Steps:
      1. grep -A10 "livenessProbe\|readinessProbe\|startupProbe" cluster/apps/default/openclaw/app/helm-release.yaml
    Expected Result: 显示所有三种探针的配置
    Evidence: 配置片段

  Scenario: 验证 PVC 挂载配置
    Tool: Bash (grep)
    Steps:
      1. grep -B2 -A15 "dev-share-files:" cluster/apps/default/openclaw/app/helm-release.yaml
    Expected Result: 显示共享 PVC 配置，无独立 PVC 声明
    Evidence: 配置输出

  Scenario: 验证 kustomize 构建
    Tool: Bash (kustomize)
    Steps:
      1. kustomize build cluster/apps/default/openclaw/app/ 2>&1 | head -100
    Expected Result: 成功构建，输出包含 Deployment、Service、Ingress
    Evidence: 构建输出
  ```

  **Commit**: YES
  - Message: `feat(openclaw): add HelmRelease with health probes and shared PVC`
  - Files: `cluster/apps/default/openclaw/app/helm-release.yaml`

---

- [ ] 5. 创建 Service 和 Ingress 配置

  **What to do**:
  - 创建 `cluster/apps/default/openclaw/app/ingress.yaml`
  - 配置 LoadBalancer Service（端口 18789）
  - 配置 Traefik IngressRoute 或标准 Ingress
  - 配置 TLS 证书（使用现有证书）
  - 域名: openclaw.${SECRET_DOMAIN}

  **Must NOT do**:
  - 不要更改域名
  - 不要创建新的 TLS 证书（复用现有）
  - 不要暴露非必要端口

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: 标准 Kubernetes Service/Ingress 配置

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 7
  - **Blocked By**: Task 3

  **References**:
  - `cluster/apps/default/dev-container/app/helm-release.yaml:80-122` - 现有 Service 和 Ingress 配置
  - 需要复用的 TLS secret: `${SECRET_DOMAIN/./-}-tls`

  **Acceptance Criteria**:
  - [ ] Service 配置正确（端口 18789，类型 LoadBalancer 或 ClusterIP）
  - [ ] Ingress 配置正确（host: openclaw.${SECRET_DOMAIN}）
  - [ ] TLS 配置正确（复用现有 secret）
  - [ ] Traefik 中间件配置（rfc-1918）

  **QA Scenarios**:
  ```
  Scenario: 验证 Ingress 配置语法
    Tool: Bash (kubectl)
    Steps:
      1. kubectl apply --dry-run=client -f cluster/apps/default/openclaw/app/ingress.yaml
    Expected Result: dry-run 成功
    Evidence: 命令输出

  Scenario: 验证 kustomize 构建包含 Ingress
    Tool: Bash (kustomize)
    Steps:
      1. kustomize build cluster/apps/default/openclaw/app/ | grep -A10 "Ingress"
    Expected Result: 输出 Ingress 配置
    Evidence: 构建输出
  ```

  **Commit**: YES
  - Message: `feat(openclaw): add Service and Ingress configuration`
  - Files: `cluster/apps/default/openclaw/app/ingress.yaml`

---

- [ ] 6. 验证独立部署正常运行

  **What to do**:
  - 启用 openclaw（取消 kustomization.yaml 中的注释）
  - 等待 Flux 同步部署
  - 验证 Pod 正常运行
  - 验证 Service 正常
  - 测试端口 18789 可访问

  **Must NOT do**:
  - 不要切换到生产 Ingress 直到验证完成
  - 不要修改 dev-container 配置（此阶段）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: 需要诊断部署问题，理解 Pod 状态

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 7
  - **Blocked By**: Task 4

  **References**:
  - `cluster/apps/default/openclaw/app/helm-release.yaml` - 部署配置

  **Acceptance Criteria**:
  - [ ] openclaw Pod 状态为 Running
  - [ ] 无 CrashLoopBackOff 或 Error 状态
  - [ ] Service 已创建且端口正确
  - [ ] 端口 18789 可访问（内部测试）

  **QA Scenarios**:
  ```
  Scenario: 验证 Pod 状态
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get pods -n default -l app=openclaw
      2. kubectl describe pod -n default -l app=openclaw
      3. kubectl logs -n default -l app=openclaw --tail=50
    Expected Result: Pod Running，日志无致命错误
    Evidence: kubectl 输出

  Scenario: 验证健康检测探针工作正常
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get pod -n default -l app=openclaw -o jsonpath='{.items[0].status.containerStatuses[0].state}'
      2. kubectl describe pod -n default -l app=openclaw | grep -A5 "Liveness\|Readiness\|Startup"
      3. kubectl get events -n default --field-selector reason=Unhealthy | grep openclaw || echo "No unhealthy events"
    Expected Result: 容器状态为 running，探针配置显示正确，无异常 unhealthy 事件
    Evidence: kubectl 输出

  Scenario: 验证 Service 和端口
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get svc -n default | grep openclaw
      2. kubectl port-forward svc/openclaw 18789:18789 -n default &
      3. curl -s http://localhost:18789/health || curl -s http://localhost:18789/
    Expected Result: Service 存在，端口转发成功，有响应
    Evidence: curl 响应输出

  Scenario: 验证 PVC 挂载正确
    Tool: Bash (kubectl)
    Steps:
      1. kubectl exec -it deploy/openclaw -n default -- ls -la /root/.openclaw
      2. kubectl exec -it deploy/openclaw -n default -- ls -la /root/clawd
      3. kubectl exec -it deploy/openclaw -n default -- touch /root/.openclaw/.k8s-test && echo "Write test passed"
    Expected Result: 目录可访问，文件存在，可写入数据
    Evidence: kubectl exec 输出
  ```

  **Commit**: YES（如果修复了配置问题）

---

- [ ] 7. 更新 dev-container 移除 OpenClaw 配置

  **What to do**:
  - 修改 `cluster/apps/default/dev-container/app/helm-release.yaml`:
    - 从 DEV_SERVICES 移除 "clawdbot"
    - 从 service.ports 移除 openclaw-gateway
    - 从 ingress.hosts 移除 openclaw.${SECRET_DOMAIN}
    - 从 persistence.dev-share-files.advancedMounts 移除 OpenClaw 相关挂载
  - 注意：保留数据文件在 PVC 中，仅移除挂载和入口

  **Must NOT do**:
  - 不要删除 PVC 中的实际数据（仅移除挂载配置）
  - 不要影响 SSH 和 OpenCode 服务

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: YAML 配置修改，需要仔细但不复杂

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 8
  - **Blocked By**: Task 5, Task 6

  **References**:
  - `cluster/apps/default/dev-container/app/helm-release.yaml` - 需要修改的文件

  **Acceptance Criteria**:
  - [ ] DEV_SERVICES 不再包含 clawdbot
  - [ ] service.ports 中无 openclaw-gateway
  - [ ] ingress.hosts 中无 openclaw 域名
  - [ ] persistence 挂载中无 OpenClaw 相关路径

  **QA Scenarios**:
  ```
  Scenario: 验证配置移除
    Tool: Bash
    Steps:
      1. grep -n "clawdbot\|openclaw" cluster/apps/default/dev-container/app/helm-release.yaml
    Expected Result: 无匹配（或确认已移除相关行）
    Evidence: grep 输出（应为空）

  Scenario: 验证 HelmRelease 语法
    Tool: Bash (kubectl)
    Steps:
      1. kubectl apply --dry-run=client -f cluster/apps/default/dev-container/app/helm-release.yaml
    Expected Result: dry-run 成功
    Evidence: 命令输出
  ```

  **Commit**: YES
  - Message: `refactor(dev-container): remove OpenClaw integration`
  - Files: `cluster/apps/default/dev-container/app/helm-release.yaml`

---

- [ ] 8. 切换 Ingress 流量到新的 Service

  **What to do**:
  - 更新 `cluster/apps/default/openclaw/app/ingress.yaml` 确保配置正确
  - 验证 Traefik 路由指向新的 openclaw Service
  - 测试外部访问 https://openclaw.${SECRET_DOMAIN}
  - 确认流量不再经过 dev-container

  **Must NOT do**:
  - 不要在验证前删除旧配置（保留回滚能力）
  - 不要造成服务中断

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: 关键切换步骤，需要监控和验证

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 9
  - **Blocked By**: Task 7

  **References**:
  - `cluster/apps/default/openclaw/app/ingress.yaml` - Ingress 配置
  - Traefik Dashboard（如可用）查看路由

  **Acceptance Criteria**:
  - [ ] Ingress 指向新的 openclaw Service
  - [ ] https://openclaw.${SECRET_DOMAIN} 可正常访问
  - [ ] dev-container 不再接收 OpenClaw 流量

  **QA Scenarios**:
  ```
  Scenario: 验证 Ingress 路由
    Tool: Bash (kubectl)
    Steps:
      1. kubectl get ingress -n default | grep openclaw
      2. kubectl describe ingress openclaw -n default
    Expected Result: Ingress 存在，backend 指向 openclaw service
    Evidence: kubectl 输出

  Scenario: 测试外部访问
    Tool: Bash (curl)
    Steps:
      1. curl -s -o /dev/null -w "%{http_code}" https://openclaw.${SECRET_DOMAIN}
      2. curl -s https://openclaw.${SECRET_DOMAIN}/health || echo "Endpoint check"
    Expected Result: HTTP 200 或其他成功状态码
    Evidence: curl 响应码
  ```

  **Commit**: NO（配置已在之前提交）

---

- [ ] 9. 清理 dev-container 中的旧数据挂载

  **What to do**:
  - 验证数据已成功迁移到新的 openclaw PVC
  - 从 dev-container HelmRelease 中完全移除 OpenClaw 相关的持久化配置
  - 验证 dev-container 重启后正常

  **Must NOT do**:
  - 不要删除 PVC 中的数据（除非确认迁移完成）
  - 不要影响其他数据挂载（code, cache, 其他 AI 工具）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: 清理工作，需要谨慎

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 10
  - **Blocked By**: Task 8

  **References**:
  - `cluster/apps/default/dev-container/app/helm-release.yaml` - 需要彻底清理的文件

  **Acceptance Criteria**:
  - [ ] dev-container HelmRelease 无 OpenClaw 相关配置
  - [ ] dev-container Pod 重启后正常
  - [ ] 其他服务（ssh, opencode）正常工作

  **QA Scenarios**:
  ```
  Scenario: 验证清理完成
    Tool: Bash
    Steps:
      1. grep -i "claw\|openclaw" cluster/apps/default/dev-container/app/helm-release.yaml || echo "Clean"
    Expected Result: 无匹配输出或显示 "Clean"
    Evidence: grep 输出

  Scenario: 验证 dev-container 健康
    Tool: Bash (kubectl)
    Steps:
      1. kubectl rollout status deployment/dev-container -n default
      2. kubectl get pods -n default -l app=dev-container
    Expected Result: Deployment 成功滚动更新，Pod Running
    Evidence: kubectl 输出
  ```

  **Commit**: YES（如果还有未提交的清理）

---

- [ ] 10. 最终验证和文档更新

  **What to do**:
  - 完整测试 OpenClaw 功能
  - 验证数据完整性（.openclaw, clawd 目录）
  - 更新相关文档（如有）
  - 创建迁移总结

  **Must NOT do**:
  - 不要遗漏任何验收标准

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: 全面验证，确保无遗漏

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: Task F1
  - **Blocked By**: Task 9

  **References**:
  - OpenClaw Web UI 测试
  - 数据目录验证

  **Acceptance Criteria**:
  - [ ] OpenClaw Web UI 可正常访问
  - [ ] 所有历史数据和配置保留
  - [ ] Skills 共享正常（如适用）
  - [ ] dev-container 无 OpenClaw 进程
  - [ ] 所有检查点通过

  **QA Scenarios**:
  ```
  Scenario: 完整功能测试
    Tool: Playwright 或手动测试
    Steps:
      1. 访问 https://openclaw.${SECRET_DOMAIN}
      2. 验证页面加载
      3. 测试基本功能（如可访问）
    Expected Result: 页面正常加载，功能可用
    Evidence: 截图或访问日志

  Scenario: 验证数据完整性
    Tool: Bash (kubectl)
    Steps:
      1. kubectl exec -it openclaw-pod -- ls -la /root/.openclaw
      2. kubectl exec -it openclaw-pod -- ls -la /root/clawd
      3. 对比备份数据确认完整性
    Expected Result: 所有预期文件存在，与备份一致
    Evidence: 文件列表对比
  ```

  **Commit**: NO（验证任务，无代码变更）

---

## Final Verification Wave

- [ ] F1. **计划合规性审计** — `oracle`
  读取完整重构计划，验证：
  - 所有 "Must Have" 已完成
  - 所有 "Must NOT Have" 未违反
  - 每个任务的 Acceptance Criteria 都已满足
  - 检查是否有遗漏的配置项或依赖
  
  **检查清单**:
  - [ ] OpenClaw 作为独立 Pod 运行
  - [ ] 数据完整迁移
  - [ ] Ingress 正常工作
  - [ ] dev-container 无 OpenClaw 配置
  - [ ] 无数据丢失
  
  **Output**: 合规性报告，列出任何遗漏或问题

---

## Commit Strategy

### 提交顺序

1. **Task 3**: `feat(openclaw): add directory structure and flux kustomization`
2. **Task 4**: `feat(openclaw): add HelmRelease with health probes and shared PVC`
3. **Task 5**: `feat(openclaw): add Service and Ingress configuration`
4. **Task 7**: `refactor(dev-container): remove OpenClaw integration`
5. **Task 9**: `cleanup(dev-container): remove OpenClaw data mounts`

### 回滚策略

**如果发现严重问题**:

```bash
# 1. 恢复 dev-container 配置
git checkout HEAD~N -- cluster/apps/default/dev-container/app/helm-release.yaml

# 2. 禁用 openclaw
kubectl delete -k cluster/apps/default/openclaw/app/

# 3. 重新部署 dev-container
flux reconcile kustomization dev-container

# 4. 验证服务恢复
curl https://openclaw.${SECRET_DOMAIN}
```

---

## Success Criteria

### 验证命令

```bash
# 1. 验证独立 Pod 运行
kubectl get pods -n default -l app=openclaw

# 2. 验证 Service
kubectl get svc -n default openclaw

# 3. 验证 Ingress
kubectl get ingress -n default openclaw
curl -I https://openclaw.${SECRET_DOMAIN}

# 4. 验证 dev-container 无 OpenClaw
grep -i clawdbot cluster/apps/default/dev-container/app/helm-release.yaml || echo "✓ Clean"

# 5. 验证数据完整性
kubectl exec -it deploy/openclaw -- ls -la /root/.openclaw
kubectl exec -it deploy/openclaw -- ls -la /root/clawd
```

### 最终检查清单

- [ ] OpenClaw 作为独立 Deployment 运行（非 dev-container 内）
- [ ] Pod 状态 Running，无错误
- [ ] **健康检测探针正常工作**（liveness/readiness/startup）
- [ ] **探针失败时 Pod 自动重启**（测试：模拟健康检查失败观察重启）
- [ ] Service 类型正确（LoadBalancer/ClusterIP）
- [ ] Ingress 可访问，HTTPS 正常
- [ ] **数据通过共享 PVC 访问正常**（dev-share-files）
- [ ] 数据目录（.openclaw, clawd）完整
- [ ] dev-container HelmRelease 无 OpenClaw 相关配置
- [ ] dev-container Pod 正常运行
- [ ] 其他 AI 工具（OpenCode）不受影响
- [ ] Skills 共享正常（如适用）

### 完成确认

```bash
# 执行以下命令确认全部通过
kubectl get pods -n default | grep -E "(openclaw|dev-container)"
curl -s -o /dev/null -w "%{http_code}" https://openclaw.${SECRET_DOMAIN}
```

预期输出：
- openclaw Pod: Running
- dev-container Pod: Running
- HTTP 状态码: 200
