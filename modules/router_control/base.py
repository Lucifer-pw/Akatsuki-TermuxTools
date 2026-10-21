"""
Base Router Abstract Class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests


class BaseRouter(ABC):
    def __init__(self, host: str, port: int = 80, username: str = "", password: str = "", timeout: int = 5):
        self.host = host.strip()
        self.port = port
        self.username = username.strip()
        self.password = password.strip()
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}" if self.port != 80 else f"http://{self.host}"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        self.is_authenticated = False

    @abstractmethod
    def login(self) -> bool:
        """Authenticates with the router web interface."""
        pass

    @abstractmethod
    def reboot(self) -> bool:
        """Sends the reboot command to the router."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Retrieves router information/status if accessible."""
        pass
