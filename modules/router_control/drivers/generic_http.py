"""
Generic HTTP Router Driver (Basic Auth / Digest Auth / Direct API)
Compatible with TP-Link, Tenda, OpenWrt, and standard web portals.
"""
from typing import Dict, Any
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from ..base import BaseRouter


class GenericRouter(BaseRouter):
    def __init__(self, host: str, port: int = 80, username: str = "admin", password: str = "admin", timeout: int = 5):
        super().__init__(host, port, username, password, timeout)

    def login(self) -> bool:
        """Tests connectivity with HTTP Basic or Digest auth."""
        try:
            # 1. Try Basic Auth
            r = self.session.get(self.base_url, auth=HTTPBasicAuth(self.username, self.password), timeout=self.timeout)
            if r.status_code == 200:
                self.is_authenticated = True
                return True

            # 2. Try Digest Auth
            r = self.session.get(self.base_url, auth=HTTPDigestAuth(self.username, self.password), timeout=self.timeout)
            if r.status_code == 200:
                self.is_authenticated = True
                return True

            # 3. Plain form reachability
            r = self.session.get(self.base_url, timeout=self.timeout)
            return r.status_code in (200, 401, 403)
        except Exception:
            return False

    def reboot(self) -> bool:
        """Attempts generic reboot endpoints (TP-Link, OpenWrt cgi-bin, etc.)."""
        endpoints = [
            f"{self.base_url}/userRpm/SysRebootRpm.htm?Reboot=Reboot",
            f"{self.base_url}/cgi-bin/luci/admin/system/reboot",
            f"{self.base_url}/goform/SysToolReboot",
            f"{self.base_url}/reboot.cgi"
        ]

        success = False
        for ep in endpoints:
            try:
                r = self.session.get(ep, auth=HTTPBasicAuth(self.username, self.password), timeout=self.timeout)
                if r.status_code in (200, 302):
                    success = True
            except Exception:
                success = True

        return success

    def get_status(self) -> Dict[str, Any]:
        return {
            "model": "Generic / TP-Link Router",
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "auth_status": "Authenticated" if self.is_authenticated else "Unauthenticated"
        }
