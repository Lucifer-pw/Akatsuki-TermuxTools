"""
Driver for ZTE Routers (F609, F670L, F660)
Commonly deployed by PT Telkom Indonesia (IndiHome) and other fiber ISPs.
"""
import re
import hashlib
from typing import Dict, Any
from ..base import BaseRouter


class ZTERouter(BaseRouter):
    def __init__(self, host: str, port: int = 80, username: str = "user", password: str = "user1234", timeout: int = 5):
        super().__init__(host, port, username, password, timeout)

    def _extract_token(self, html: str) -> str:
        """Extracts CSRF or session verification token if present."""
        match = re.search(r'name=["\'](?:_token|token|frash_token)["\']\s+value=["\']([^"\']+)["\']', html, re.I)
        if match:
            return match.group(1)
        match = re.search(r'createTokenStr\s*\(\s*["\']([^"\']+)["\']', html, re.I)
        if match:
            return match.group(1)
        return ""

    def login(self) -> bool:
        """Attempts to log in to the ZTE router web portal."""
        try:
            # 1. Fetch initial login page to acquire session cookies and token
            init_url = f"{self.base_url}/"
            resp = self.session.get(init_url, timeout=self.timeout)
            token = self._extract_token(resp.text)

            # Common login endpoints for ZTE F609 / F670L
            login_endpoints = [
                f"{self.base_url}/getpage.gch?pid=1002",
                f"{self.base_url}/login.gch",
                f"{self.base_url}/"
            ]

            payload = {
                "Username": self.username,
                "Password": self.password,
                "action": "login",
                "_token": token
            }

            for endpoint in login_endpoints:
                post_resp = self.session.post(endpoint, data=payload, timeout=self.timeout)
                # Successful login typically redirects to main menu or sets UID cookie
                if post_resp.status_code in (200, 302):
                    if "logout" in post_resp.text.lower() or "menu" in post_resp.text.lower() or "frmlogin" not in post_resp.text.lower():
                        self.is_authenticated = True
                        return True

            # Also check if already logged in or session cookie exists
            if "uid" in [c.name.lower() for c in self.session.cookies]:
                self.is_authenticated = True
                return True

            return False
        except Exception:
            return False

    def reboot(self) -> bool:
        """Issues the reboot command to the ZTE router."""
        if not self.is_authenticated:
            self.login()

        # Potential reboot endpoints on ZTE firmware
        reboot_urls = [
            f"{self.base_url}/getpage.gch?pid=1002&nextpage=manager_dev_conf_t.gch",
            f"{self.base_url}/manager_dev_conf_t.gch",
            f"{self.base_url}/getpage.gch?pid=1002"
        ]

        payloads = [
            {"IF_ACTION": "reboot", "action": "reboot"},
            {"action": "reboot", "sub_action": "reboot"},
            {"button": "Reboot", "IF_ACTION": "reboot"}
        ]

        success = False
        for url in reboot_urls:
            for p in payloads:
                try:
                    r = self.session.post(url, data=p, timeout=self.timeout)
                    if r.status_code in (200, 302):
                        success = True
                except Exception:
                    # Often router terminates socket immediately upon initiating reboot
                    success = True

        return success

    def get_status(self) -> Dict[str, Any]:
        """Fetches basic ZTE device info."""
        return {
            "model": "ZTE Series (F609/F670L/F660)",
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "auth_status": "Authenticated" if self.is_authenticated else "Unauthenticated"
        }
