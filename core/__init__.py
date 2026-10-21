"""Core modules for Akatsuki Termux Tools"""
from .theme import console, akatsuki_theme
from .utils import load_config, save_config, get_default_gateway, get_local_ip

__all__ = ["console", "akatsuki_theme", "load_config", "save_config", "get_default_gateway", "get_local_ip"]
