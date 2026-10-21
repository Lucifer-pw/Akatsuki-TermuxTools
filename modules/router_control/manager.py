"""
Router Manager & Action Dispatcher
Coordinates gateway detection, banner probing, driver selection, and execution.
"""
from typing import Dict, Any, Optional, Tuple
import requests
import socket
from core.utils import get_default_gateway
from .presets import ROUTER_PRESETS
from .drivers.zte import ZTERouter
from .drivers.huawei import HuaweiRouter
from .drivers.generic_http import GenericRouter


class RouterManager:
    def __init__(self, host: Optional[str] = None):
        self.host = host if host and host != "auto" else get_default_gateway()
        self.port = 80
        self.current_preset = ROUTER_PRESETS[0] # Default IndiHome ZTE
        self.username = self.current_preset["username"]
        self.password = self.current_preset["password"]
        self.detected_info: Dict[str, Any] = {}

    def probe_router(self, timeout: int = 3) -> Dict[str, Any]:
        """Probes the gateway web server to determine responsiveness and server signatures."""
        info = {
            "host": self.host,
            "port": self.port,
            "is_reachable": False,
            "server": "Unknown",
            "title": "Unknown",
            "suggested_model": "zte"
        }

        # Check socket reachability first
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            res = s.connect_ex((self.host, self.port))
            s.close()
            if res != 0:
                self.detected_info = info
                return info
        except Exception:
            self.detected_info = info
            return info

        info["is_reachable"] = True

        # HTTP GET probe
        try:
            url = f"http://{self.host}:{self.port}"
            resp = requests.get(url, timeout=timeout)
            info["server"] = resp.headers.get("Server", "Unknown")
            
            # Simple title / body signature scan
            body = resp.text.lower()
            if "zte" in body or "f609" in body or "f670" in body or "zte" in info["server"].lower():
                info["suggested_model"] = "zte"
                info["title"] = "ZTE Home Gateway"
            elif "huawei" in body or "echolife" in body or "hg8245" in body:
                info["suggested_model"] = "huawei"
                info["title"] = "Huawei EchoLife ONT"
            elif "tp-link" in body or "tplink" in body:
                info["suggested_model"] = "tplink"
                info["title"] = "TP-Link Wireless Router"
            else:
                info["suggested_model"] = "zte" # default for IndiHome
                info["title"] = "Generic Router / ONT"
        except Exception:
            pass

        self.detected_info = info
        return info

    def get_driver(self, model: Optional[str] = None):
        """Instantiates the appropriate router driver."""
        chosen_model = model or self.current_preset.get("driver", "zte")
        if chosen_model == "zte":
            return ZTERouter(self.host, self.port, self.username, self.password)
        elif chosen_model == "huawei":
            return HuaweiRouter(self.host, self.port, self.username, self.password)
        else:
            return GenericRouter(self.host, self.port, self.username, self.password)

    def test_login(self) -> Tuple[bool, str]:
        """Tests login with current username and password."""
        driver = self.get_driver()
        success = driver.login()
        if success:
            return True, f"Login Berhasil sebagai '{self.username}' pada {self.host}"
        return False, f"Login Gagal. Pastikan kredensial '{self.username}' / '{self.password}' sesuai model router."

    def execute_reboot(self) -> Tuple[bool, str]:
        """Triggers the reboot process."""
        driver = self.get_driver()
        success = driver.reboot()
        if success:
            return True, f"Perintah reboot berhasil dikirim ke router {self.host}!"
        return False, f"Gagal mengirim perintah reboot ke router {self.host}."
