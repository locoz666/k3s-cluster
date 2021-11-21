Rancher在卸载时需要使用官方工具来确保资源都移除干净
https://github.com/rancher/system-tools/releases

命令为：

```shell
./system-tools_linux-amd64 remove -c ~/.kube/config
```
