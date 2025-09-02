# clearlog/collector_legacy.py
import socket
from datetime import datetime, timezone
import win32evtlog
from xml.etree import ElementTree as ET

def _to_iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def collect(max_events=500):
    server = 'localhost'; logtype = 'Security'
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    hand = win32evtlog.OpenEventLog(server, logtype)
    host = socket.gethostname()
    out = []; read=0

    while True:
        recs = win32evtlog.ReadEventLog(hand, flags, 0)
        if not recs: break
        for ev in recs:
            if (ev.EventID & 0xFFFF) != 4625: continue
            read += 1
            dt = ev.TimeGenerated.replace(tzinfo=timezone.utc)
            try:
                xml = win32evtlog.EvtRender(ev, win32evtlog.EvtRenderEventXml)  # bazı sürümlerde çalışır
            except Exception:
                xml = ""
            user = ip = work = dom = lt = st = sst = proc = None
            if xml:
                try:
                    root = ET.fromstring(xml)
                    get = lambda n: root.findtext(f".//EventData/Data[@Name='{n}']")
                    user = get("TargetUserName"); dom = get("TargetDomainName")
                    ip = get("IpAddress"); work = get("WorkstationName")
                    lt = get("LogonType"); st = get("Status"); sst = get("SubStatus"); proc = get("ProcessName")
                except Exception:
                    pass
            out.append({
                "ts_utc": _to_iso_utc(dt), "host": host, "user": user, "domain": dom,
                "src_ip": ip if ip and ip!='-' else None, "src_host": work if work and work!='-' else None,
                "logon_type": lt, "status": st, "substatus": sst, "process": proc,
                "reason": "Logon failure (4625)", "raw": (xml[:800] if xml else None)
            })
            if read>=max_events: break
        if read>=max_events: break
    win32evtlog.CloseEventLog(hand)
    return list(reversed(out))
