# AskTable Secure Tunnel (ATST) 用户使用手册

## 1. 概述
AskTable Secure Tunnel (ATST) 是一项服务，允许安全地将外部的 AskTable 服务通过安全隧道与内部的本地数据库进行通信。这项服务确保数据源与 AskTable 之间的连接既安全又高效，非常适合需要保证数据通信安全性的企业环境。

## 2. 开始使用 ATST
### 2.1 创建 Secure Tunnel Key
首先，您需要创建一个唯一的 secure tunnel key，这将用于标识并启动您的 ATST。执行以下命令以创建 key：


> asktable -t your_token --create-secure-tunnel

此命令将返回一个 `securetunnel_key`，请妥善保存此 key，因为它是连接您的数据源与 AskTable 的唯一凭证。

### 2.2 启动 ATST
获得 `securetunnel_key` 后，您可以在私有网络中启动 ATST。使用以下 Docker 命令启动：

> docker run datamini/asktable-secure-tunnel -e ASKTABLE_SECURE_TUNNEL_KEY=<securetunnel_key>

启动后，ATST 将自动从 AskTable 获取配置信息并开始运行。ATST 会每 5 秒检查一次配置更新，因此新增的数据源连接会自动生效，无需重启服务。

## 3. 注册数据源

要让 AskTable 通过 ATST 访问您的内部数据源，您只需使用如下命令注册数据源：

```python
asktable.datasources.register(
    type='mysql', 
    access_config={
        'host': 'xxx', 'port': 3306, 'user': 'xx', 'password': 'xx', 
        'securetunnel_key': 'xxx'
    }
)
```
在 access_config 配置信息中增加 `securetunnel_key` 字段，将其设置为您的 `securetunnel_key`。这样，AskTable 将通过 ATST 访问您的数据源。

详见：https://pypi.org/project/asktable/



## 4. 管理 ATST 连接
### 4.1 获取 ATST 信息

如果需要查看当前 ATST 的状态及配置，可以使用以下 API 调用：
```http
GET https://api.securetunnels.asktable.com/securetunnels/<securetunnel_key>
```
这将返回 ATST 的详细信息，包括是否启动及当前配置。


### 4.2 获取数据源连接信息
要查看所有通过当前 ATST 连接的数据源，可以使用：
```http
GET https://api.securetunnels.asktable.com/securetunnels/<securetunnel_key>/links
```
此调用返回一个包含所有数据源连接信息的列表。

## 5. 安全和隐私
保持您的 `securetunnel_key` 安全是极其重要的。不要在不安全的地方存储或共享此 key，以避免未授权访问您的数据源。

## 6. 故障排除
若 ATST 服务遇到任何问题，首先请检查 `securetunnel_key` 是否正确无误，确保您的网络环境允许 ATST 正常访问您的数据源以及 AskTable 服务。如有更多技术问题，请联系 AskTable 技术支持。
