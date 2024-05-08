# 基础镜像
FROM python:3.11

# 安装基础工具
RUN apt-get update && apt-get install -y vim curl && apt-get clean

# 安装FRP客户端
ARG FRPC_VERSION=0.52.3
ARG TARGETPLATFORM

# 下载和安装FRPC

RUN case "${TARGETPLATFORM}" in \
    "linux/amd64") \
      curl -sSL "https://github.com/fatedier/frp/releases/download/v${FRPC_VERSION}/frp_${FRPC_VERSION}_linux_amd64.tar.gz" | tar xz --strip-components=1 -C /usr/bin;; \
    "linux/arm64") \
      curl -sSL "https://github.com/fatedier/frp/releases/download/v${FRPC_VERSION}/frp_${FRPC_VERSION}_linux_arm64.tar.gz" | tar xz --strip-components=1 -C /usr/bin;; \
    "linux/arm/v7") \
      curl -sSL "https://github.com/fatedier/frp/releases/download/v${FRPC_VERSION}/frp_${FRPC_VERSION}_linux_arm.tar.gz" | tar xz --strip-components=1 -C /usr/bin;; \
    *) echo "Unsupported arch ${TARGETPLATFORM}" && exit 1 ;; \
    esac

# 设置工作目录
WORKDIR /app

# 安装Python依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制Python脚本和其他必要文件
COPY main.py /app/main.py
COPY system.py /app/system.py

ENV TZ=Asia/Shanghai

EXPOSE 1260

# 设置入口点
ENTRYPOINT ["python", "main.py"]

# 设置默认的CMD
CMD []
