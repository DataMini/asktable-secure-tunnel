# AskTable Secure Tunnel (ATST) 用户使用手册

## 1. 概述
AskTable Secure Tunnel (ATST) 是 AskTable 开发的一个安全工具，允许 AskTable 服务通过安全隧道与内部的本地数据库进行通信。这项服务确保数据源与 AskTable 之间的连接既安全又高效，非常适合需要保证数据通信安全性的企业环境。

您可以参考本文档，在您的私有网络中部署并运行 ATST。

![network-arch.png](network-arch.png)


## 2. 开始使用 ATST

首先需要准备一台用于部署 ATST 的服务器，确保满足以下要求。

服务器要求：
1. 网络方面：确保 ATST 服务器可以访问 AskTable 服务和您的数据源。
2. 操作系统：Linux 或 macOS（M1/M2 ARM）
3. 处理器架构：x86 或 ARM
4. 运行环境：请确保您的服务器上已经安装了 Docker。


### 2.1 下载 ATST 镜像

您可以通过以下命令下载 ATST Docker 镜像

```bash
docker pull datamini/asktable-secure-tunnel
```

### 2.2 使用方法

启动 ATST 服务前，您需要一个唯一的 `Secure Tunnel ID(securetunnel_id)`来标识和启动您的 ATST：

1. 创建 `securetunnel_id`：
    ```bash
    docker run --rm -e ASKTABLE_TOKEN=<asktable_token> datamini/asktable-secure-tunnel create-id
    ```
  此命令将返回一个 `securetunnel_id`，请妥善保存此 ID，因为它是获取您当前 ATST 配置信息的唯一凭证。

2. 启动 ATST 服务：
    ```bash
    docker run  -e ASKTABLE_TOKEN=<asktable_token> \
        [-e SECURETUNNEL_ID=<securetunnel_id>] datamini/asktable-secure-tunnel
    ```
  - 如果环境变量中包含`securetunnel_id`，使用该ID启动。（推荐）
  - 如果环境变量中不包含`securetunnel_id`，自动创建一个ID并启动。（不推荐，因为每次启动都会生成一个新的ID，绑定原ID的数据源将无法访问）

启动后，ATST 将自动从 AskTable 获取配置信息并开始运行，同时定期自动更新。一个 ATST 可以共享给多个数据源使用。

### 2.3 环境变量配置

- ASKTABLE_API_URL： AskTable 服务的 API 地址，默认为 `https://api.asktable.com`
- ASKTABLE_TOKEN： AskTable 服务的 API Token，从[AskTable网站](https://asktable.com)获取。
- SECURETUNNEL_ID： ATST 的唯一标识。
- CONFIG_REFRESH_INTERVAL: 配置自动刷新间隔，默认为 10 秒。


## 3. 注册数据源

要让 AskTable 通过 ATST 访问您的内部数据源，您需要注册数据源并指定 `securetunnel_id`：

```python
from asktable import AskTable
at = AskTable()
at.datasources.register(
    type='mysql', 
    access_config={
        'host': '10.1.2.3', 'port': 3306, 'user': 'xx', 'password': 'xx', 
        'securetunnel_id': 'xxx'
    }
)
```
在 access_config 配置信息中增加 `securetunnel_id` 字段，将其设置为您的 `securetunnel_id`，从而使 AskTable 能够通过 ATST 访问您的数据源。更多信息请参考：[AskTable Python Library](https://pypi.org/project/asktable/).

## 4. 维护和管理 ATST 服务【非常重要】

请不要随意关闭 ATST 服务，否则 AskTable 将无法访问您的数据源。

如果需要重启、升级或迁移 ATST 服务，请确保`securetunnel_id`不变，以保证数据源的正常访问。

为了保证`securetunnel_id`的安全性，我们建议您在启动 ATST 服务时使用环境变量来传递`securetunnel_id`，而不是让 ATST 自动生成。


## 5. 高级功能
您可以通过Python SDK 或命令行工具 `asktable` 来获取 ATST 信息。详见：https://pypi.org/project/asktable/



## 6. 安全和隐私
保持您的 `asktable_token`和`securetunnel_id` 安全是极其重要的。不要在不安全的地方存储或共享这些信息，以避免未授权访问您的数据源。

## 7. 故障排除
若 ATST 服务遇到任何问题，首先请检查 `asktable_token`和`securetunnel_id` 是否正确无误，确保您的网络环境允许 ATST 正常访问您的数据源以及 AskTable 服务。如有更多技术问题，请联系 AskTable 技术支持。

# 感谢
AskTable Secure Tunnel 使用了 [frp](https://github.com/fatedier/frp)，一个高性能的反向代理服务。感谢 frp 项目组的贡献。

