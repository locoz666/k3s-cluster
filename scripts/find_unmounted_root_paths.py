#!/usr/bin/env python3
"""Find /root paths not covered by dev-container volume mounts.

This script:
1) Extracts container mount target paths from a HelmRelease YAML (via `yq`).
2) Walks a local root directory (default: /root) up to a max depth.
3) Prints directories that are NOT inside any mount target path.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import subprocess
import sys
from typing import Any, Iterable


DEFAULT_HELM_RELEASE = "cluster/apps/default/dev-container/app/helm-release.yaml"


def _run_yq_to_json(file_path: str) -> Any:
    try:
        proc = subprocess.run(
            ["yq", "-j", ".", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        raise RuntimeError("missing dependency: yq (kislyuk/yq)") from e
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip() or str(e)
        raise RuntimeError(f"yq failed: {msg}") from e

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError("yq output is not valid JSON") from e


def _iter_paths(obj: Any) -> Iterable[str]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "path" and isinstance(v, str):
                yield v
            yield from _iter_paths(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_paths(item)


def _normalize_mount_paths(paths: Iterable[str], root_prefix: str) -> list[str]:
    normed: list[str] = []
    for p in paths:
        if not p.startswith(root_prefix):
            continue
        # Use POSIX normalization even on Linux to be explicit.
        np = posixpath.normpath(p)
        if np == root_prefix:
            continue
        normed.append(np)
    return sorted(set(normed))


def _is_covered_by_mount(path: str, mount_targets: list[str]) -> bool:
    # Covered if path is mount target itself or is under it.
    for m in mount_targets:
        if path == m:
            return True
        if path.startswith(m + "/"):
            return True
    return False


def _walk_dirs_limited(root_dir: str, max_depth: int) -> list[str]:
    out: list[str] = []
    root_dir = os.path.abspath(root_dir)
    for current, dirs, _files in os.walk(root_dir, topdown=True, followlinks=False):
        rel = os.path.relpath(current, root_dir)
        depth = 0 if rel == "." else rel.count(os.sep) + 1

        if depth > max_depth:
            dirs[:] = []
            continue

        if current != root_dir:
            out.append(current)

        # Prevent descending further once we hit max depth.
        if depth == max_depth:
            dirs[:] = []

    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List /root directories (<= N depth) that are not covered by HelmRelease mounts."
        )
    )
    parser.add_argument(
        "--helm-release",
        default=DEFAULT_HELM_RELEASE,
        help=f"Path to HelmRelease YAML (default: {DEFAULT_HELM_RELEASE})",
    )
    parser.add_argument(
        "--root",
        default="/root",
        help="Root directory to scan (default: /root)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Max directory depth under root (default: 3)",
    )
    parser.add_argument(
        "--show-mounts",
        action="store_true",
        help="Also print the extracted mount target paths",
    )
    args = parser.parse_args()

    doc = _run_yq_to_json(args.helm_release)
    mount_targets = _normalize_mount_paths(_iter_paths(doc), args.root.rstrip("/"))
    if args.show_mounts:
        for p in mount_targets:
            print(p)
        print("---")

    all_dirs = _walk_dirs_limited(args.root, args.max_depth)
    unmounted = [d for d in all_dirs if not _is_covered_by_mount(d, mount_targets)]
    for d in sorted(set(unmounted)):
        print(d)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
