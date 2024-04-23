import os
import sys
import subprocess
import toml
import time
import threading
from asktable import AskTable


def create_id(token):
    at = AskTable(token=token)
    st = at.securetunnels.create()
    print(f"Created Secure Tunnel ID: {st.id}")
    return st.id


def generate_config_dict(token, st_id):
    at = AskTable(token=token)
    st = at.securetunnels.get(st_id)
    config = {
        "common": {
            "server_addr": st.atst_server_host,
            "server_port": st.atst_server_port
        },
        "proxies": []
    }
    for link in st.links:
        proxy = {
            "name": link.id,
            "type": "tcp",
            "local_ip": link.target_host,
            "local_port": link.target_port,
            "remote_port": link.proxy_port
        }
        config["proxies"].append(proxy)
    return config


def generate_config_toml(config, config_path):
    """
    [common]
    server_addr = sh0.dminfra.cn
    server_port = 7000

    [[proxies]]
    name = "mysql-tcp1"
    type = "tcp"
    local_ip = "private.mysql.dminfra.cn"
    local_port = 3306
    remote_port = 6000

    [[proxies]]
    name = "mysql-tcp2"
    type = "tcp"
    local_ip = "private.mysql.dminfra.cn"
    local_port = 3306
    remote_port = 6002
    """
    try:
        with open(config_path, 'w') as file:
            toml.dump(config, file)
        print(f"Configuration file saved to {config_path}")
    except IOError as e:
        print(f"Failed to write to {config_path}: {e}")


def monitor_config_and_reload_frpc(token, st_id, config_path, previous_config, interval=5):
    while True:
        current_config = generate_config_dict(token, st_id)
        if current_config != previous_config:
            print("Configuration has changed, updating and reloading frpc.")
            generate_config_toml(current_config, config_path)
            subprocess.run(["/usr/bin/frpc", "reload", "-c", config_path])
            previous_config = current_config
        time.sleep(interval)


def start_atst(token, st_id):
    print("Starting ATST with Secure Tunnel ID:", st_id)
    config_path = "/etc/frpc.toml"
    current_config = generate_config_dict(token, st_id)
    generate_config_toml(current_config, config_path)
    # Start monitoring in a separate thread
    print(f"Starting monitoring thread for {config_path}")
    threading.Thread(
        target=monitor_config_and_reload_frpc,
        args=(token, st_id, config_path, current_config),
        daemon=True
    ).start()
    # Start frpc as the main process and redirect its output
    with subprocess.Popen(["/usr/bin/frpc", "-c", config_path], stdout=sys.stdout, stderr=sys.stderr) as proc:
        proc.wait()


def main():
    token = os.getenv('ASKTABLE_TOKEN')
    if not token:
        print("Missing ASKTABLE_TOKEN")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "create-id":
        create_id(token)
    else:
        st_id = os.getenv('SECURETUNNEL_ID')

        if st_id:
            print(f"Using provided Secure Tunnel ID({st_id}) for starting ATST.")
            start_atst(token, st_id)
        else:
            print(f"Secure Tunnel ID not provided. Creating a new one.")
            st_id = create_id(token)
            start_atst(token, st_id)


if __name__ == "__main__":
    main()