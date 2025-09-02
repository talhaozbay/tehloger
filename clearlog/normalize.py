# clearlog/normalize.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class AuthFail4625:
    ts_utc: str          # "2025-09-02T12:34:56Z"
    host: str            # event kaynağı makine
    user: Optional[str]  # TargetUserName
    domain: Optional[str]# TargetDomainName
    src_ip: Optional[str]# IpAddress ( - ise None )
    src_host: Optional[str] # WorkstationName
    logon_type: Optional[str] # 2,3,10,11...
    status: Optional[str]    # Status
    substatus: Optional[str] # SubStatus
    process: Optional[str]   # ProcessName
    reason: str              # "Logon failure (4625)"
    #raw: Optional[str]       # kırpılmış XML
