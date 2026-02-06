# kubevirt/ — KubeVirt Operator 清单

## OVERVIEW
大体量的 KubeVirt operator/CRD/RBAC 清单。

## WHERE TO LOOK
- `kubevirt-operator.yaml`：主清单（行数很大）。

## ANTI-PATTERNS
- 不要在此文件里“顺手格式化/重排 YAML”：会造成巨大无意义 diff。
