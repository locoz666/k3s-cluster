helm repo add rook-release https://charts.rook.io/release
helm repo update

kubectl create namespace rook-ceph
helm install -n rook-ceph rook-ceph rook-release/rook-ceph
helm install -n rook-ceph rook-ceph-cluster rook-release/rook-ceph-cluster -f helm-ceph-cluster-values.yaml