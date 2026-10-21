"""
Preset Credentials & Model Signatures for Common Home Routers
"""
from typing import List, Dict

ROUTER_PRESETS: List[Dict[str, str]] = [
    {
        "isp": "IndiHome (ZTE Default)",
        "model": "ZTE F609 / F670L / F660",
        "username": "user",
        "password": "user1234",
        "driver": "zte",
        "description": "Kredensial standar pelanggan IndiHome ZTE"
    },
    {
        "isp": "IndiHome (ZTE Admin)",
        "model": "ZTE F609 Admin",
        "username": "admin",
        "password": "Telkomdso123",
        "driver": "zte",
        "description": "Kredensial teknisi/admin IndiHome ZTE"
    },
    {
        "isp": "IndiHome (Huawei Default)",
        "model": "Huawei HG8245H / EG8145V5",
        "username": "user",
        "password": "user1234",
        "driver": "huawei",
        "description": "Kredensial standar pelanggan IndiHome Huawei"
    },
    {
        "isp": "IndiHome (Huawei Telecom Admin)",
        "model": "Huawei HG8245 Series Admin",
        "username": "telecomadmin",
        "password": "admintelecom",
        "driver": "huawei",
        "description": "Kredensial admin/telecom Huawei ONT"
    },
    {
        "isp": "IndiHome (Huawei Root)",
        "model": "Huawei HG8245A / H",
        "username": "root",
        "password": "admin",
        "driver": "huawei",
        "description": "Kredensial alternatif ONT Huawei"
    },
    {
        "isp": "Retail / Standar TP-Link",
        "model": "TP-Link WR840N / Archer Series",
        "username": "admin",
        "password": "admin",
        "driver": "tplink",
        "description": "Default router TP-Link retail"
    },
    {
        "isp": "FirstMedia / Biznet / Generic",
        "model": "Cisco / Fastweb / Generic Router",
        "username": "admin",
        "password": "password",
        "driver": "generic",
        "description": "Kredensial default router umum"
    },
    {
        "isp": "Tenda / D-Link",
        "model": "Tenda F3 / D-Link DIR Series",
        "username": "admin",
        "password": "",
        "driver": "generic",
        "description": "Default router tanpa password atau admin/kosong"
    }
]
