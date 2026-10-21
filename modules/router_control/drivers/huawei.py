"""
Driver for Huawei EchoLife Routers & ONTs (HG8245H, EG8145V5)
Commonly used by Telkom IndiHome, Biznet, and other fiber providers.
"""
import re
from typing import Dict, Any
from ..base import BaseRouter


class HuaweiRouter(BaseRouter):
    def __init__(self, host: str, port: int = 80, username: str = "user", password: str = "user1234", timeout: int = 5):
        super().__init__(host, port, username, password, timeout)

    def _extract_hw_token(self, html: str) -> str:
        match = re.search(r'name=["\']x\.X_HW_Token["\']\s+value=["\']([^"\']+)["\']', html, re.I)
        if match:
            return match.group(1)
        match = re.search(r'ontoken\s*=\s*["\']([^"\']+)["\']', html, re.I)
        if match:
            return match.group(1)
        return ""

    def login(self) -> bool:
        """Attempts to log in to Huawei ONT web portal."""
        try:
            init_resp = self.session.get(self.base_url, timeout=self.timeout)
            token = self._extract_hw_token(init_resp.text)

            endpoints = [
                f"{self.base_url}/asp/SetForm.asp",
                f"{self.base_url}/login.asp",
                f"{self.base_url}/"
            ]

            payload = {
                "UserName": self.username,
                "PassWord": self.password,
                "x.X_HW_Token": token
            }

            for ep in endpoints:
                res = self.session.post(ep, data=payload, timeout=self.timeout)
                if res.status_code in (200, 302):
                    if "index.asp" in res.text or "logout" in res.text.lower():
                        self.is_authenticated = True
                        return True

            return False
        except Exception:
            return False

    def reboot(self) -> bool:
        """Sends reboot command to Huawei ONT."""
        if not self.is_authenticated:
            self.login()

        reboot_endpoints = [
            f"{self.base_url}/asp/SetForm.asp",
            f"{self.base_url}/html/management/reset.asp"
        ]

        payload = {
            "RequestFile": "html/management/reset.asp",
            "x.X_HW_Token": "",
            "Action": "Reboot"
        }

        success = False
        for ep in reboot_endpoints:
            try:
                r = self.session.post(ep, data=payload, timeout=self.timeout)
                if r.status_code in (200, 302):
                    success = True
            except Exception:
                success = True

        return success

    def get_status(self) -> Dict[str, Any]:
        return {
            "model": "Huawei EchoLife Series (HG8245H / EG8145V5)",
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "auth_status": "Authenticated" if self.is_authenticated else "Unauthenticated"
        }
