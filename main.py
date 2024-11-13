import os
import sys
import subprocess
import logging
import toml
import time
import threading
import asktable
from asktable import Asktable
from system import gather_system_info

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

at_api_url = os.getenv('API_URL', 'https://api.asktable.com/v1')
at_api_key = os.getenv('API_KEY')
if not at_api_key:
    logging.error("Missing ASKTABLE_API_KEY")
    sys.exit(1)

at = Asktable(api_key=at_api_key, api_url=at_api_url)


def create_id():
    st = at.securetunnels.create()
    logging.info(f"Created Secure Tunnel ID: {st.id}")
    return st.id


def generate_config_and_send_client_info(st_id):
    st = at.securetunnels.get(st_id)
    config = {
        "serverAddr": st.atst_server_host,
        "serverPort": st.atst_server_port,
        "webServer": {
            "port": 1260,
            "addr": "0.0.0.0",
        },
        "proxies": []
    }
    links = at.securetunnels.links.list(st_id)
    for link in links:
        proxy = {
            "name": link.id,
            "type": "tcp",
            "localIP": link.target_host,
            "localPort": link.target_port,
            "remotePort": link.proxy_port
        }
        config["proxies"].append(proxy)

    info = gather_system_info()
    st.update(unique_key=info['hostname'], client_info=info)
    return config


def generate_config_toml(config, config_path):
    """
    serverAddr = 10.10.10.10
    serverPort = 7000

    [webServer]
    port = 7703

    [[proxies]]
    name = "mysql-tcp1"
    type = "tcp"
    localIP = "10.1.1.3"
    localPort = 3306
    remotePort = 6000

    [[proxies]]
    name = "mysql-tcp2"
    type = "tcp"
    localIP = "10.2.2.3"
    localPort = 3306
    remotePort = 6002
    """
    try:
        with open(config_path, 'w') as file:
            toml.dump(config, file)
        logging.info(f"Configuration file saved to {config_path}")
    except IOError as e:
        logging.error(f"Failed to write to {config_path}: {e}")


def monitor_config_and_reload_frpc(
        st_id, config_path, previous_config, interval=os.environ.get("CONFIG_REFRESH_INTERVAL", 10)):
    while True:
        try:
            current_config = generate_config_and_send_client_info(st_id)
        except asktable.APIConnectionError:
            logging.error("Failed to connect to the server. Retrying in 10 seconds.")
            time.sleep(10)
            continue
        except asktable.APIStatusError as e:
            logging.error(f"Another non-200-range status code was received: {e}. Retrying in 10 seconds.")
            time.sleep(10)
            continue
        if current_config != previous_config:
            logging.info("Configuration has changed, updating and reloading frpc.")
            generate_config_toml(current_config, config_path)
            subprocess.run(["/usr/bin/frpc", "reload", "-c", config_path])
            previous_config = current_config
        time.sleep(interval)


def start_atst(st_id):
    config_path = "/etc/frpc.toml"
    try:
        current_config = generate_config_and_send_client_info(st_id)
    except asktable.APIConnectionError:
        logging.error(f"Failed to connect to the AskTable Server: {at_api_url}. Exiting.", exc_info=True)
        sys.exit(1)
    generate_config_toml(current_config, config_path)
    # Start monitoring in a separate thread
    logging.info(f"Starting monitoring thread for {config_path}")
    threading.Thread(
        target=monitor_config_and_reload_frpc,
        args=(st_id, config_path, current_config),
        daemon=True
    ).start()
    # Start frpc as the main process and redirect its output
    with subprocess.Popen(["/usr/bin/frpc", "-c", config_path], stdout=sys.stdout, stderr=sys.stderr) as proc:
        proc.wait()


def main():
    masked_api_key = at_api_key[:4] + "*" * (len(at_api_key) - 8) + at_api_key[-4:]
    logging.info(f"Starting ATST Client with AskTable API Key {masked_api_key}")
    if len(sys.argv) > 1 and sys.argv[1] == "create-id":
        create_id()
    else:
        st_id = os.getenv('ATST_ID')
        if st_id:
            logging.info(f"Using provided Secure Tunnel ID({st_id}) for starting ATST.")
            try:
                start_atst(st_id)
            except asktable.NotFoundError:
                logging.error(f"Secure Tunnel ID({st_id}) not found. Exiting.")
        else:
            logging.error("ATST_ID not provided. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()

