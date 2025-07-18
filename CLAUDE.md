# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a K3s Kubernetes cluster managed by GitOps using Flux. The repository follows a GitOps pattern where the Git repository drives the state of the Kubernetes cluster. All configurations are declared as Kubernetes manifests organized in a hierarchical structure.

## Repository Structure

The cluster configuration is organized under the `cluster/` directory with the following key components:

### Base Configuration (`cluster/000-base/`)
- **Entry point**: Flux system configuration and base resources
- **repositories/helm/**: Helm chart repository definitions
- **flux-system/**: Core Flux GitOps components
- **namespaces_**/**: Namespace definitions organized by category
- **cluster-secrets.sops.yaml**: Encrypted cluster-wide secrets using SOPS

### Infrastructure Layers
- **001-infrastructure/**: Core infrastructure services (cert-manager, monitoring, storage)
- **002-infrastructure-extra/**: Additional infrastructure components
- **100-virtual-machine-base/**: KubeVirt base setup for VMs
- **101-virtual-machine-base-extra/**: Extended VM infrastructure
- **102-virtual-machine/**: Virtual machine definitions

### Application Layers
- **230-media-service/**: Media streaming and management applications
- **240-smart-home/**: Home automation services
- **cluster/apps/**: Application deployments organized by namespace
  - **default/**: User applications (Nextcloud, GitLab, gaming servers, etc.)
  - **kube-system/**: System-level applications

## Architecture Patterns

### Flux GitOps Structure
- Uses Flux v2 with Kustomization controllers
- Dependencies defined between layers (000-base → 001-infrastructure → apps)
- SOPS integration for encrypted secrets with GPG keys
- Each application follows the pattern: `app/` (main resources) + `ks.yaml` (Kustomization)

### Application Organization
- **Helm-based**: Most applications use Helm charts with custom values
- **Modular design**: Each service has its own directory with consistent structure
- **Resource separation**: PVCs, configs, and ingress rules separated into logical files
- **Namespace isolation**: Applications grouped by functional namespaces

### Security and Secrets
- SOPS encryption for all sensitive data
- Secrets managed as `.sops.yaml` files with PGP encryption
- Certificate management through cert-manager with Let's Encrypt

## Common Development Tasks

### Task Runner Commands
Use `task` (go-task) for common operations:

```bash
# Sync Flux with Git repository
task flux:sync

# Format all YAML and Markdown files
task format:all

# Lint all files
task lint:all

# Initialize pre-commit hooks
task pre-commit:init

# Run pre-commit checks
task pre-commit:run
```

### Flux Operations
```bash
# Check Flux system status
kubectl get kustomization -A

# Force reconcile a specific Kustomization
flux reconcile source git flux-system

# Check Helm releases
flux get helmrelease -A

# Check Helm repositories
flux get sources helm -A
```

### Working with SOPS Secrets
```bash
# Edit encrypted secret (requires GPG key access)
sops cluster/000-base/cluster-secrets.sops.yaml

# Encrypt a new secret file
sops --encrypt --in-place path/to/secret.sops.yaml
```

### Application Deployment Pattern
Each application typically follows this structure:
```
app-name/
├── app/
│   ├── helm-release.yaml     # Helm chart configuration
│   ├── default.yaml          # Default values/config
│   ├── *-pvc.yaml           # Persistent volume claims
│   └── kustomization.yaml    # Kustomize resources
├── ks.yaml                   # Flux Kustomization definition
└── additional-components/    # Optional: databases, ingress, etc.
```

### Adding New Applications
1. Create directory structure under appropriate namespace in `cluster/apps/`
2. Add Helm repository to `cluster/000-base/repositories/helm/` if needed
3. Create `ks.yaml` Kustomization pointing to the app directory
4. Add reference to the new `ks.yaml` in parent `kustomization.yaml`
5. Flux will automatically detect and deploy changes

## Technology Stack

- **Kubernetes Distribution**: K3s
- **GitOps**: Flux v2
- **Secret Management**: SOPS with GPG encryption
- **Service Mesh/Networking**: Cilium CNI, Traefik ingress
- **Certificate Management**: cert-manager with Let's Encrypt
- **Storage**: Rook Ceph distributed storage, JuiceFS
- **Virtualization**: KubeVirt for VMs
- **Monitoring**: Prometheus stack (kube-prometheus-stack)
- **Container Registry**: Nexus Repository Manager

## Development Workflow

1. Make changes to YAML manifests
2. Run linting and formatting: `task lint:all && task format:all`
3. Commit changes with descriptive messages
4. Flux automatically syncs changes to cluster within 10 minutes
5. Force sync if needed: `task flux:sync`

## Key Configuration Files

- **Taskfile.yml**: Task runner definitions for common operations
- **.sops.yaml**: SOPS configuration with GPG key fingerprints
- **cluster/000-base/cluster-secrets.sops.yaml**: Global encrypted secrets
- **cluster/000-base/flux-system/gotk-sync.yaml**: Flux Git repository configuration