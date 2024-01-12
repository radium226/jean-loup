from contextlib import contextmanager
from typing import Generator
from signal import signal, SIGINT, SIGTERM
from threading import Event
from subprocess import Popen, run
from ipaddress import IPv4Network
from tempfile import NamedTemporaryFile
from contextlib import ExitStack
from pathlib import Path
from textwrap import dedent

class HotSpot:

    def __init__(self, ip_network: IPv4Network, domain: str, wireless_hardware_device: str = "phy0", ssid="Jean Loup"):
        self.wireless_hardware_device = wireless_hardware_device
        self.ip_network = ip_network
        self.domain = domain
        self.ssid = ssid

        self.exit_stack = ExitStack()

    def __enter__(self):
        
        iw_command = ["iw", "phy0", "interface", "add", "ap0", "type", "__ap"]
        run(iw_command)
        self.exit_stack.callback(lambda: run(["iw", "phy0", "interface", "del", "ap0"]))


        runtime_folder_path = Path("/run/timelapse/hotspot")
        runtime_folder_path.mkdir(parents=True, exist_ok=True)

        dnsmasq_config_file_path = runtime_folder_path / "dnsmasq.conf"
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
                addn-hosts=/home/alarm/hosts
                expand-hosts                                       
            """).format(
                domain=self.domain,
                dhcp_range_min_address=self.ip_network[1],
                dhcp_range_max_address=self.ip_network[-1],
                dhcp_address=self.ip_network[0],
            ))
        self.exit_stack.callback(lambda: dnsmasq_config_file_path.unlink())

        hostapd_config_file_path = runtime_folder_path / "hostapd.conf"
        with hostapd_config_file_path.open("w") as hostapd_config_file:
            hostapd_config_file.write(dedent("""\
                ctrl_interface={control_socket_path}
                ctrl_interface_group=0
                interface=ap0
                driver=nl80211
                ssid={ssid}
                hw_mode=g
                channel=11
                wmm_enabled=0
                macaddr_acl=0
                auth_algs=1
            """).format(
                control_socket_path=runtime_folder_path / "hostapd.sock",
                ssid=self.ssid,
            ))
        self.exit_stack.callback(lambda: hostapd_config_file_path.unlink())

        dnsmasq_command = [
            "dnsmasq", 
            "-C", str(dnsmasq_config_file_path),
            "--no-daemon",
            "--log-queries",
        ]
        dnsmasq_process = Popen(dnsmasq_command)
        self.exit_stack.callback(lambda: dnsmasq_process.send_signal(SIGTERM))

        hostapd_command = [
            "hostapd",
            str(hostapd_config_file_path),
        ]
        hostapd_process = Popen(hostapd_command)
        self.exit_stack.callback(lambda: hostapd_process.send_signal(SIGTERM))

        return self

    def __exit__(self, type, value, traceback):
        self.exit_stack.close()

    def wait_for(self) -> None:
        event = Event()

        def signal_handler(signum, frame):
            event.set()
        
        signal(SIGINT, signal_handler)
        
        event.wait()
    