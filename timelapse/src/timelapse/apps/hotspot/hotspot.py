from signal import signal, SIGTERM
from threading import Event
from subprocess import Popen, run, PIPE
from ipaddress import IPv4Network
from contextlib import ExitStack
from pathlib import Path
from textwrap import dedent
from retrying import retry

from ...logging import info
from ...config import Config

class Hotspot:

    def __init__(self, config: Config, ip_network: IPv4Network | None = None, domain: str | None = None, wireless_hardware_device: str | None = None, ssid: str | None = None):
        self.wireless_hardware_device = wireless_hardware_device or config.values.hotspot.wireless_hardware_device
        self.ip_network = ip_network or config.values.hotspot.ip_network
        self.domain = domain or config.values.hotspot.domain
        self.ssid = ssid or config.values.hotspot.ssid

        self.exit_stack = ExitStack()

    def __enter__(self):
        runtime_folder_path = Path("/run/timelapse/hotspot")
        runtime_folder_path.mkdir(parents=True, exist_ok=True)

        self._setup_ap0_interface()

        self._start_hostapd(runtime_folder_path)
        self._start_dnsmasq(runtime_folder_path)

        return self

    def __exit__(self, type, value, traceback):
        self.exit_stack.close()

    def _setup_ap0_interface(self):
        commands = [
            ["iw", "phy0", "interface", "add", "ap0", "type", "__ap"],
            ["ip", "addr", "add", f"{self.ip_network[2]}/{self.ip_network.prefixlen}", "dev", "ap0"],
        ]
        for command in commands:
            process = run(command)
            if process.returncode != 0:
                raise Exception("Failed to create ap0 interface! ")
            
        def teardown():
            info("Tearing down ap0 interface")
            run(["iw", "dev", "ap0", "del"])

        self.exit_stack.callback(teardown)

    def _start_dnsmasq(self, runtime_folder_path: Path):
        dnsmasq_config_file_path = runtime_folder_path / "dnsmasq.conf"
        additionnal_hosts_file_path = runtime_folder_path / "additional-hosts"
        with additionnal_hosts_file_path.open("w") as hosts_file:
            hosts_file.write(f"{self.ip_network[2]} jean-loup.{self.domain}\n")

        with dnsmasq_config_file_path.open("w") as dnsmasq_config_file:
            dnsmasq_config_file.write(dedent("""\
                interface=lo,ap0
                no-dhcp-interface=lo,wlan0
                bind-interfaces
                server=8.8.8.8
                domain={domain}
                local=/{domain}/
                domain-needed
                bogus-priv
                dhcp-range={dhcp_range_min_address},{dhcp_range_max_address},12h
                dhcp-option=3,{dhcp_address}
                no-hosts
                addn-hosts={additionnal_hosts_file_path}
                expand-hosts                                       
            """).format(
                domain=self.domain,
                dhcp_range_min_address=self.ip_network[2],
                dhcp_range_max_address=self.ip_network[-1],
                dhcp_address=self.ip_network[1],
                additionnal_hosts_file_path=str(additionnal_hosts_file_path),
            ))
        self.exit_stack.callback(lambda: dnsmasq_config_file_path.unlink())

        dnsmasq_command = [
            "dnsmasq", 
            "-C", str(dnsmasq_config_file_path),
            "--no-daemon",
            "--log-queries",
        ]
        dnsmasq_process = Popen(dnsmasq_command)
        def teardown():
            dnsmasq_process.send_signal(SIGTERM)
            dnsmasq_process.wait()

        self.exit_stack.callback(teardown)

    def _start_hostapd(self, runtime_folder_path: Path):
        interface = "ap0"
        hostapd_config_file_path = runtime_folder_path / "hostapd.conf"
        control_socket_path = runtime_folder_path / "hostapd.sock"
        with hostapd_config_file_path.open("w") as hostapd_config_file:
            hostapd_config_file.write(dedent("""\
                ctrl_interface={control_socket_path}
                ctrl_interface_group=0
                interface={interface}
                driver=nl80211
                ssid={ssid}
                hw_mode=g
                channel=6
                wmm_enabled=0
                macaddr_acl=0
                wpa=0
                auth_algs=1
            """).format(
                control_socket_path=control_socket_path,
                ssid=self.ssid,
                interface=interface,
            ))
        self.exit_stack.callback(lambda: hostapd_config_file_path.unlink())

        hostapd_command = [
            "hostapd",
            "-d",
            str(hostapd_config_file_path),
        ]
        hostapd_process = Popen(hostapd_command)
        def teardown():
            hostapd_process.send_signal(SIGTERM)
            hostapd_process.wait()
        self.exit_stack.callback(teardown)

        @retry(stop_max_attempt_number=10, wait_fixed=500)
        def wait_for():
            info("Pinging hostapd... ")
            command = [
                "hostapd_cli", 
                "-p", f"{control_socket_path}",
                "-i", interface, 
                "ping",
            ]
            process = run(command, text=True, check=False, stdout=PIPE)
            if process.returncode != 0 or process.stdout != "PONG\n":
                info("KO :(")
                raise Exception("Unable to ping hostapd! ")
            
            info("OK :)")
            
        wait_for()


    def serve_forever(self) -> None:
        event = Event()

        def signal_handler(signum, frame):
            event.set()
        
        signal(SIGTERM, signal_handler)
        
        event.wait()
    