# AskTable Secure Tunnel (ATST) 用户使用手册

## 1. 概述
AskTable Secure Tunnel (ATST) 是一项服务，允许安全地将外部的 AskTable 服务通过安全隧道与内部的本地数据库进行通信。这项服务确保数据源与 AskTable 之间的连接既安全又高效，非常适合需要保证数据通信安全性的企业环境。

## 2. 介绍

利用ATST，用户在向AskTable注册数据源时可以指定一个自己的 `securetunnel_id`。这个标识符使AskTable能够明确识别并通过指定的安全隧道（ATST）访问内部数据源。这一特性不仅简化了数据源的管理过程，同时也增强了数据访问的安全性。

该`securetunnel_id`是用户在运行 ATST 时自动生成，请保存下来，并作为启动 ATST 服务的唯一凭证。

请不要关闭 ATST 服务，否则 AskTable 将无法访问您的数据源。如果您需要更换 ATST 所在的服务器，只需在新服务器上重新启动 ATST 服务，并使用相同的 `securetunnel_id` 即可。


## 3. 开始使用 ATST

### 3.1 下载镜像
```bash
docker pull datamini/asktable-secure-tunnel
```

### 3.2 使用方法

首先，您需要一个唯一的 `Secure Tunnel ID(securetunnel_id)`。这将用于标识并启动您的 ATST。
然后，在您的私有网络中，启动 ATST 服务。

获取 ATST_ID 和 启动 ATST 均使用同一个 Docker 镜像，具体方法如下：

1. 如果指定了`create-id`命令，则只创建一个`securetunnel_id`。

    ```bash
    docker run --rm -e ASKTABLE_TOKEN=<asktable_token> datamini/asktable-secure-tunnel create-id
    ```
  此命令将返回一个 `securetunnel_id`，请妥善保存此 ID，因为它是获取您当前 ATST 配置信息的唯一凭证。

2. 如果没有指定任何命令（即默认行为），则：
  - 如果环境变量中包含`securetunnel_id`，使用该ID启动。
  - 如果环境变量中不包含`securetunnel_id`，自动创建一个ID，然后使用这个ID启动。

    ```bash
    docker run  -e ASKTABLE_TOKEN=<asktable_token> \
        [-e SECURETUNNEL_ID=<securetunnel_id>] datamini/asktable-secure-tunnel
    ```

启动后，ATST 将自动从 AskTable 获取配置信息并开始运行。 并且会自动更新。一个ATST 可以共享给多个DataSource使用。

### 3.3 所有环境变量

- ASKTABLE_API_URL： AskTable 服务的 API 地址，默认为 `https://api.asktable.com`
- ASKTABLE_TOKEN： AskTable 服务的 API Token，从[AskTable网站](https://asktable.com)获取。
- SECURETUNNEL_ID： ATST 的唯一标识，用于获取自己的配置信息
- CONFIG_REFRESH_INTERVAL: 配置自动刷新间隔，默认为 10 秒


## 4. 注册数据源

要让 AskTable 通过 ATST 访问您的内部数据源，您只需使用如下命令注册数据源：

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
在 access_config 配置信息中增加 `securetunnel_id` 字段，将其设置为您的 `securetunnel_id`。这样，AskTable 将通过 ATST 访问您的数据源。

详见：https://pypi.org/project/asktable/


## 5. 高级功能
您可以通过Python SDK 或命令行工具 `asktable` 来管理 ATST 服务。详见：https://pypi.org/project/asktable/



## 6. 安全和隐私
保持您的 `asktable_token`和`securetunnel_id` 安全是极其重要的。不要在不安全的地方存储或共享这些信息，以避免未授权访问您的数据源。

## 7. 故障排除
若 ATST 服务遇到任何问题，首先请检查 `asktable_token`和`securetunnel_id` 是否正确无误，确保您的网络环境允许 ATST 正常访问您的数据源以及 AskTable 服务。如有更多技术问题，请联系 AskTable 技术支持。

# 感谢
AskTable Secure Tunnel 使用了 [frp](https://github.com/fatedier/frp)，一个高性能的反向代理服务。感谢 frp 项目组的贡献。

